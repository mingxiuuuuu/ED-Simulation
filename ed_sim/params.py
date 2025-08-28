from dataclasses import dataclass
from typing import Optional

@dataclass
class Params:
    sim_days: int = 21  #3-week window is commonly modeled
    warmup_days: int = 2 #appropriate for system stabilization
    arrival_rate_per_hr: float = 10.0 
    p_fast: float = 0.52 #P3 ("ambulatory") https://journals.sagepub.com/doi/10.1177/20101058241245236
    p_lab: float = 0.4 
    p_admit: float = 0.3
    fast_service_mean: float = 15.0
    main_initial_mean: float = 30.0
    lab_mean: float = 30.0
    review_mean: float = 15.0
    boarding_mean: float = 120.0
    lwbs_wait_cap_minutes: Optional[int] = 240
    overflow_threshold_minutes: int = 30 # Fast Track patients overflow to Main ED if expected wait > 60 minutes
    seed: int = 88

@dataclass
class ResourcesCfg:
    fast_capacity: int = 1
    main_beds: int = 15
    main_providers: int = 5
    lab_techs: int = 2
