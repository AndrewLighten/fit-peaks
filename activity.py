from datetime import datetime
from typing import List
from calculation_data import AerobicDecoupling


class Activity:

    # SQLite row ID
    rowid: int = None

    # Zwift activity ID
    zwift_id: str = None
    s3_url: str = None

    # Start and end times.
    start_time: datetime = None
    end_time: datetime = None
    moving_time: int = None

    # Activity name and distance travelled.
    distance: float = None
    elevation: int = None
    activity_name: str = None

    # Overall statistics
    avg_power: int = None
    max_power: int = None
    normalised_power: int = None
    avg_hr: int = None
    max_hr: int = None

    # Raw data
    raw_power: List[int] = None
    raw_hr: List[int] = None

    # Power data.
    peak_5sec_power: int = None
    peak_30sec_power: int = None
    peak_60sec_power: int = None
    peak_5min_power: int = None
    peak_10min_power: int = None
    peak_20min_power: int = None
    peak_30min_power: int = None
    peak_60min_power: int = None
    peak_90min_power: int = None
    peak_120min_power: int = None

    # Heart rate data.
    peak_5sec_hr: int = None
    peak_30sec_hr: int = None
    peak_60sec_hr: int = None
    peak_5min_hr: int = None
    peak_10min_hr: int = None
    peak_20min_hr: int = None
    peak_30min_hr: int = None
    peak_60min_hr: int = None
    peak_90min_hr: int = None
    peak_120min_hr: int = None

    # Transient values
    duration_in_seconds: int = None
    variability_index: float = None
    ftp: int = None
    intensity_factor: float = None
    tss: int = None
    speed_in_kmhr: float = None
    aerobic_decoupling: AerobicDecoupling = None
    aerobic_efficiency: float = None
    ctl: int = None
    atl: int = None
    first_for_day: bool = True
