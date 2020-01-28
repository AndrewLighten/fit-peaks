from datetime import datetime


class Peaks:

    # Start and end times.
    start_time: datetime = None
    end_time: datetime = None

    # Activity name.
    activity_name: str = ""

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
