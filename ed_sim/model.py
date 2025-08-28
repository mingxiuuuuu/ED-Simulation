import simpy
import numpy as np
from .params import Params, ResourcesCfg
from .entities import Patient, Stats
from .samplers import Sampler

class EDModel:
    def __init__(self, params: Params, res: ResourcesCfg):
        self.P, self.R = params, res
        self.S = Sampler(self.P.seed)
        self.env = simpy.Environment()
        self.fast_track = simpy.Resource(self.env, capacity=self.R.fast_capacity)
        self.beds = simpy.Resource(self.env, capacity=self.R.main_beds)
        self.providers = simpy.Resource(self.env, capacity=self.R.main_providers)
        self.lab = simpy.Resource(self.env, capacity=self.R.lab_techs)
        self.stats = Stats([],[],[],[],[],[],0,0,0,0,[],[],[],[],0)
        self.start_warm = self.P.warmup_days * 24 * 60
        self.sim_minutes = self.P.sim_days * 24 * 60
        self._pid = 0
        
        # Add overflow tracking
        self.overflow_threshold_minutes = getattr(self.P, 'overflow_threshold_minutes', 60)  # Default 60 min wait triggers overflow

    # ---- Processes ----
    def arrival_process(self):
        lam_per_min = self.P.arrival_rate_per_hr / 60.0
        mean_ia = 1.0/lam_per_min if lam_per_min>0 else 1e9
        while True:
            yield self.env.timeout(self.S.exp_minutes(mean_ia))
            self._pid += 1
            stream = 'fast' if self.S.rng.random() < self.P.p_fast else 'main'
            p = Patient(id=self._pid, arrival_min=self.env.now, stream=stream)
            if stream == 'fast':
                self.env.process(self.patient_fast_with_overflow(p))
            else:
                p.lab_needed = (self.S.rng.random() < self.P.p_lab)
                p.admit = (self.S.rng.random() < self.P.p_admit)
                self.env.process(self.patient_main(p))
            if self.env.now > self.sim_minutes*0.999:
                break

    def patient_fast_with_overflow(self, p: Patient):
        """
        Fast Track patient with overflow capability to Main ED
        """
        # Try Fast Track first
        fast_available = len(self.fast_track.queue) == 0 and len(self.fast_track.users) < self.R.fast_capacity
        
        # Check if overflow should trigger
        estimated_fast_wait = len(self.fast_track.queue) * self.P.fast_service_mean
        should_overflow = (
            estimated_fast_wait > self.overflow_threshold_minutes or
            len(self.fast_track.queue) >= self.R.fast_capacity * 3  # Queue longer than 3x capacity
        )
        
        if should_overflow and len(self.beds.queue) + len(self.beds.users) < self.R.main_beds:
            # Route to Main ED instead - treat as simple Main ED case
            p.stream = 'overflow'  # Track that this was an overflow case
            p.lab_needed = False  # Fast Track equivalent patients don't need lab
            p.admit = False       # Fast Track equivalent patients don't get admitted
            if self.env.now >= self.start_warm:
                self.stats.n_overflow += 1  # Track overflow count
            yield from self.patient_main(p)
            return
        
        # Otherwise proceed with normal Fast Track process
        yield from self.patient_fast_original(p)

    def patient_fast_original(self, p: Patient):
        """
        Original Fast Track process
        """
        # LWBS protection for Fast Track
        lwbs_ev = self.env.timeout(self.P.lwbs_wait_cap_minutes) if self.P.lwbs_wait_cap_minutes else None
        fast_req = self.fast_track.request()
        
        if lwbs_ev:
            got = yield simpy.events.AnyOf(self.env, [fast_req, lwbs_ev])
            if lwbs_ev in got.events:
                # Patient leaves without being seen
                self.fast_track.release(fast_req)
                if self.env.now >= self.start_warm: 
                    self.stats.n_lwbs += 1
                return
        else:
            yield fast_req

        # Patient got fast track resource
        with fast_req:
            if self.env.now >= self.start_warm:
                self.stats.waits_fast.append(self.env.now - p.arrival_min)
            yield self.env.timeout(self.S.lognormal_minutes(self.P.fast_service_mean))
        
        p.exit_min = self.env.now
        if p.exit_min >= self.start_warm:
            self.stats.n_fast += 1
            self.stats.los_fast.append(p.exit_min - p.arrival_min)

    def patient_main(self, p: Patient):
        """
        Main ED process - handles both original Main ED patients and overflow from Fast Track
        """
        # LWBS timer for getting a bed
        lwbs_ev = self.env.timeout(self.P.lwbs_wait_cap_minutes) if self.P.lwbs_wait_cap_minutes else None
        bed_req = self.beds.request()
        
        if lwbs_ev:
            got = yield simpy.events.AnyOf(self.env, [bed_req, lwbs_ev])
            if lwbs_ev in got.events:
                self.beds.release(bed_req)
                if self.env.now >= self.start_warm: 
                    self.stats.n_lwbs += 1
                return
        else:
            yield bed_req

        # Patient got a bed, now wait for provider
        with self.providers.request() as prov_req:
            yield prov_req
            if self.env.now >= self.start_warm:
                self.stats.waits_main.append(self.env.now - p.arrival_min)
            
            # Different service times for overflow patients (Fast Track equivalent)
            if hasattr(p, 'stream') and p.stream == 'overflow':
                # Overflow patients get Fast Track service time but in Main ED
                yield self.env.timeout(self.S.lognormal_minutes(self.P.fast_service_mean))
            else:
                # Regular Main ED initial assessment
                yield self.env.timeout(self.S.lognormal_minutes(self.P.main_initial_mean))

        # Lab and further treatment only for non-overflow patients
        if p.lab_needed:
            with self.lab.request() as lab_req:
                yield lab_req
                yield self.env.timeout(self.S.lognormal_minutes(self.P.lab_mean))
            with self.providers.request() as prov2_req:
                yield prov2_req
                yield self.env.timeout(self.S.lognormal_minutes(self.P.review_mean))

        # Admission process
        if p.admit:
            start = self.env.now
            yield self.env.timeout(self.S.lognormal_minutes(self.P.boarding_mean))
            boarded = self.env.now - start
            self.beds.release(bed_req)
            if self.env.now >= self.start_warm:
                self.stats.n_main_admit += 1
                self.stats.los_main_admit.append(self.env.now - p.arrival_min)
                self.stats.boarding_times.append(boarded)
        else:
            self.beds.release(bed_req)
            if self.env.now >= self.start_warm:
                # Count overflow patients with Fast Track stats but track separately if needed
                if hasattr(p, 'stream') and p.stream == 'overflow':
                    self.stats.n_fast += 1  # Count as Fast Track throughput
                    self.stats.los_fast.append(self.env.now - p.arrival_min)
                else:
                    self.stats.n_main_dc += 1
                    self.stats.los_main_dc.append(self.env.now - p.arrival_min)

    def sampler_process(self):
        while self.env.now < self.sim_minutes:
            if self.env.now >= self.start_warm:
                self.stats.fast_busy_samples.append(len(self.fast_track.users))
                self.stats.beds_busy_samples.append(len(self.beds.users))
                self.stats.prov_busy_samples.append(len(self.providers.users))
                self.stats.lab_busy_samples.append(len(self.lab.users))
            yield self.env.timeout(1.0)

    # ---- Run ----
    def run(self):
        self.env.process(self.arrival_process())
        self.env.process(self.sampler_process())
        self.env.run(until=self.sim_minutes)