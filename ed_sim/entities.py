
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Patient:
    id: int
    arrival_min: float
    stream: str
    lab_needed: bool = False
    admit: bool = False
    first_seen_min: Optional[float] = None
    exit_min: Optional[float] = None
    boarded_mins: float = 0.0

@dataclass
class Stats:
    waits_fast: List[float]
    waits_main: List[float]
    los_fast: List[float]
    los_main_dc: List[float]
    los_main_admit: List[float]
    boarding_times: List[float]
    n_fast: int
    n_main_dc: int
    n_main_admit: int
    n_lwbs: int
    fast_busy_samples: List[int]
    beds_busy_samples: List[int]
    prov_busy_samples: List[int]
    lab_busy_samples: List[int]
    n_overflow: int = 0 