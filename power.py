from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import defaultdict
from dataclasses import dataclass, field

from persistence import Persistence
from activity import Activity
from athlete import get_ftp
from calculations import calculate_progressive_fitness, calculate_transient_values, calculate_fitness
from calculation_data import AerobicDecoupling
from formatting import format_aero_decoupling, format_aero_efficiency, format_variability_index, format_atl, format_ctl, format_tsb


@dataclass
class WeeklyFigures:
    def __init__(self):
        self.avg_5sec = []
        self.avg_30sec = []
        self.avg_60sec = []
        self.avg_5min = []
        self.avg_10min = []
        self.avg_20min = []
        self.avg_30min = []
        self.avg_60min = []
        self.avg_90min = []
        self.avg_120min = []

    distance_total: int = 0
    elevation_total: int = 0
    tss_total: int = 0
    ctl_total: int = 0
    atl_total: int = 0
    tsb_total: int = 0
    duration_total: timedelta = timedelta(0)

    work_days = 0

    avg_5sec: List[int] = field(default_factory=list)
    avg_30sec: List[int] = field(default_factory=list)
    avg_60sec: List[int] = field(default_factory=list)
    avg_5min: List[int] = field(default_factory=list)
    avg_10min: List[int] = field(default_factory=list)
    avg_20min: List[int] = field(default_factory=list)
    avg_30min: List[int] = field(default_factory=list)
    avg_60min: List[int] = field(default_factory=list)
    avg_90min: List[int] = field(default_factory=list)
    avg_120min: List[int] = field(default_factory=list)

    max_distance: int = None
    max_elevation: int = None
    max_duration: timedelta = None
    max_speed: float = None
    max_5sec: int = None
    max_30sec: int = None
    max_60sec: int = None
    max_5min: int = None
    max_10min: int = None
    max_20min: int = None
    max_30min: int = None
    max_60min: int = None
    max_90min: int = None
    max_120min: int = None
    max_pmax: int = None
    max_pavg: int = None
    max_pnor: int = None
    max_if: float = None
    max_tss: int = None
    max_ctl: int = None
    max_atl: int = None
    max_tsb: int = None

    def add_work_day(self):
        self.work_days += 1

    def add_distance(self, distance: int):
        self.distance_total += distance
        if self.max_distance is None or distance > self.max_distance:
            self.max_distance = distance

    def add_elevation(self, elevation: int):
        self.elevation_total += elevation
        if self.max_elevation is None or elevation > self.max_elevation:
            self.max_elevation = elevation

    def add_tss(self, tss: int):
        self.tss_total += tss
        if self.max_tss is None or tss > self.max_tss:
            self.max_tss = tss

    def add_ctl(self, ctl: int):
        self.ctl_total += ctl
        if self.max_ctl is None or ctl > self.max_ctl:
            self.max_ctl = ctl
            
    def add_atl(self, atl: int ):
        self.atl_total += atl
        if self.max_atl is None or atl > self.max_atl:
            self.max_atl = atl

    def add_tsb(self, tsb: int):
        self.tsb_total += tsb
        if self.max_tsb is None or tsb < self.max_tsb:
            self.max_tsb = tsb

    def add_duration(self, duration: timedelta):
        self.duration_total += duration
        if self.max_duration is None or duration > self.max_duration:
            self.max_duration = duration

    def add_5sec(self, peak_5sec: int):
        self.avg_5sec.append(peak_5sec)
        if self.max_5sec is None or peak_5sec > self.max_5sec:
            self.max_5sec = peak_5sec

    def add_30sec(self, peak_30sec: int):
        self.avg_30sec.append(peak_30sec)
        if self.max_30sec is None or peak_30sec > self.max_30sec:
            self.max_30sec = peak_30sec

    def add_60sec(self, peak_60sec: int):
        self.avg_60sec.append(peak_60sec)
        if self.max_60sec is None or peak_60sec > self.max_60sec:
            self.max_60sec = peak_60sec

    def add_5min(self, peak_5min: int):
        self.avg_5min.append(peak_5min)
        if self.max_5min is None or peak_5min > self.max_5min:
            self.max_5min = peak_5min

    def add_10min(self, peak_10min: int):
        self.avg_10min.append(peak_10min)
        if self.max_10min is None or peak_10min > self.max_10min:
            self.max_10min = peak_10min

    def add_20min(self, peak_20min: int):
        self.avg_20min.append(peak_20min)
        if self.max_20min is None or peak_20min > self.max_20min:
            self.max_20min = peak_20min

    def add_30min(self, peak_30min: int):
        self.avg_30min.append(peak_30min)
        if self.max_30min is None or peak_30min > self.max_30min:
            self.max_30min = peak_30min

    def add_60min(self, peak_60min: int):
        self.avg_60min.append(peak_60min)
        if self.max_60min is None or peak_60min > self.max_60min:
            self.max_60min = peak_60min

    def add_90min(self, peak_90min: int):
        self.avg_90min.append(peak_90min)
        if self.max_90min is None or peak_90min > self.max_90min:
            self.max_90min = peak_90min

    def add_120min(self, peak_120min: int):
        self.avg_120min.append(peak_120min)
        if self.max_120min is None or peak_120min > self.max_120min:
            self.max_120min = peak_120min

    def add_pmax(self, pmax: int):
        if self.max_pmax is None or pmax > self.max_pmax:
            self.max_pmax = pmax

    def add_pavg(self, pavg: int):
        if self.max_pavg is None or pavg > self.max_pavg:
            self.max_pavg = pavg

    def add_pnor(self, pnor: int):
        if self.max_pnor is None or pnor > self.max_pnor:
            self.max_pnor = pnor

    def add_if(self, intensity_factor: int):
        if self.max_if is None or intensity_factor > self.max_if:
            self.max_if = intensity_factor


def power_report(all: bool):
    """
    Print a power report.
    
    This will fetch activities from the database, then:
    
    - Find the maximum for each power peak (e.g., max 5 seconds, 30 seconds, etc).
    - Print the activity data for each activity, sorted in date order with a break
      between each week.
    - Print the maximum we found for each power peak as a final summary.
    """

    # Calculate the start date we should use
    if all:
        start_date = datetime(2001, 1, 1)
    else:
        start_date = (datetime.now() - timedelta(days=90)).date()

    # Load the activity data.
    db = Persistence()
    if not (activities := db.load_for_week(start_date)):
        print("No data to report on")
        return

    # Calculate transient values
    _calculate_transient_values(activities)

    # Find the maximum for each value.
    max = _load_max_values(activities)

    # Establish the prevailing FTP
    prevailing_ftp = None

    # Totals for the current week
    weekly_figures = WeeklyFigures()

    # Print the activity data for each week.
    current_weekday = None
    for activity in activities:

        # Time to break to a new week?
        if current_weekday is None or current_weekday > activity.start_time.weekday():
            if current_weekday:
                _print_footer(weekly_figures=weekly_figures, max=max)
                weekly_figures = WeeklyFigures()

            _print_header()
            any_data_since_header = False

        # Capture the weekday.
        if current_weekday is None or current_weekday != activity.start_time.weekday():
            weekly_figures.add_work_day()
            new_day = True
            if any_data_since_header:
                print()

        current_weekday = activity.start_time.weekday()

        # New FTP?
        activity_ftp = get_ftp(activity.start_time)
        new_ftp = prevailing_ftp and activity_ftp > prevailing_ftp
        prevailing_ftp = activity_ftp

        # Print the detail.
        _print_detail(activity=activity, max=max, new_ftp=new_ftp, new_day=new_day, new_week=not any_data_since_header)
        new_day = False
        any_data_since_header = True

        # Find the duration.
        duration = activity.end_time - activity.start_time

        # Accumulate for this week
        weekly_figures.add_distance(activity.distance)
        if activity.elevation:
            weekly_figures.add_elevation(activity.elevation)
        weekly_figures.add_tss(activity.tss)
        if activity.first_for_day:
            weekly_figures.add_ctl(activity.ctl)
            weekly_figures.add_atl(activity.atl)
            weekly_figures.add_tsb(activity.ctl - activity.atl)
        weekly_figures.add_duration(duration)

        weekly_figures.add_5sec(activity.peak_5sec_power)
        weekly_figures.add_30sec(activity.peak_30sec_power)
        weekly_figures.add_60sec(activity.peak_60sec_power)
        if activity.peak_5min_power:
            weekly_figures.add_5min(activity.peak_5min_power)
        if activity.peak_10min_power:
            weekly_figures.add_10min(activity.peak_10min_power)
        if activity.peak_20min_power:
            weekly_figures.add_20min(activity.peak_20min_power)
        if activity.peak_30min_power:
            weekly_figures.add_30min(activity.peak_30min_power)
        if activity.peak_60min_power:
            weekly_figures.add_60min(activity.peak_60min_power)
        if activity.peak_90min_power:
            weekly_figures.add_90min(activity.peak_90min_power)
        if activity.peak_120min_power:
            weekly_figures.add_120min(activity.peak_120min_power)

        weekly_figures.add_pmax(activity.max_power)
        weekly_figures.add_pavg(activity.avg_power)
        weekly_figures.add_pnor(activity.normalised_power)
        weekly_figures.add_if(activity.intensity_factor)

    # Final footer.
    _print_footer(weekly_figures=weekly_figures, max=max)

    # Print the summary.
    _print_summary(max)


def _print_header():
    """
    Print the report header.
    """
    print()
    print(
        "                                                                                                                             ┌──────────────────────────────────── Measurements in Watts ──────────────────────────────────┐"
    )
    print(
        "ID      Date               Activity                                   Distance   Elevation   Start   Duration      Speed       5s    30s    60s     5m    10m    20m    30m    60m    90m   120m    Max    Avg   Norm    FTP    V/I    I/F    TSS   AeroDe   AeroEf   CTL   ATL   TSB"
    )
    _print_separator()


def _print_detail(*, activity: Activity, max: Dict[str, List[int]], new_ftp: bool, new_day: bool, new_week: bool):
    """
    Print the detail for a particular activity.
    """

    # Find the ID, date, start time, and duration.
    rowid = format(activity.rowid, "<5d")
    date = activity.start_time.strftime("%a %d %b, %Y") if new_day else "                "
    start = activity.start_time.strftime("%H:%M")
    duration = str(activity.end_time - activity.start_time).rjust(8)

    # Find the activity name
    distance = (format(round(activity.distance / 1000, 2), ".2f") + "km").rjust(8)
    elevation = (format(activity.elevation, ",d") + "m").rjust(6) if activity.elevation else "".rjust(6)
    activity_name = activity.activity_name.ljust(40) if activity.activity_name else "(Unknown)".ljust(40)
    if len(activity_name) > 40:
        activity_name = f'{activity_name[:37]}...'
    speed = (format(activity.speed_in_kmhr, ".2f") + "km/hr").rjust(10)

    # Find the power figures
    p_max = str(int(activity.max_power)).rjust(4)
    p_avg = str(int(activity.avg_power)).rjust(4)
    p_nor = str(int(activity.normalised_power)).rjust(4)

    variability_index = format_variability_index(activity=activity, width=4)
    ftp_text = str(activity.ftp)
    if new_ftp:
        ftp_text = "\x1B[37;44m" + ftp_text + "\x1B[0m"
    elif not new_week:
        ftp_text = "\x1B[38;5;238m" + ftp_text + "\x1B[0m"
    intensity_factor_text = format(activity.intensity_factor, ".2f")
    tss_text = format(activity.tss, ".0f").rjust(4)

    # Find each peak value.
    p5sec = str(activity.peak_5sec_power).rjust(4) if activity.peak_5sec_power else "    "
    p30sec = str(activity.peak_30sec_power).rjust(4) if activity.peak_30sec_power else "    "
    p60sec = str(activity.peak_60sec_power).rjust(4) if activity.peak_60sec_power else "    "
    p5min = str(activity.peak_5min_power).rjust(4) if activity.peak_5min_power else "    "
    p10min = str(activity.peak_10min_power).rjust(4) if activity.peak_10min_power else "    "
    p20min = str(activity.peak_20min_power).rjust(4) if activity.peak_20min_power else "    "
    p30min = str(activity.peak_30min_power).rjust(4) if activity.peak_30min_power else "    "
    p60min = str(activity.peak_60min_power).rjust(4) if activity.peak_60min_power else "    "
    p90min = str(activity.peak_90min_power).rjust(4) if activity.peak_90min_power else "    "
    p120min = str(activity.peak_120min_power).rjust(4) if activity.peak_120min_power else "    "

    # Highlight those peaks in this activity that are the highest peak we've ever seen.
    p5sec = _decorate(activity.peak_5sec_power, max["5sec"], p5sec)
    p30sec = _decorate(activity.peak_30sec_power, max["30sec"], p30sec)
    p60sec = _decorate(activity.peak_60sec_power, max["60sec"], p60sec)
    p5min = _decorate(activity.peak_5min_power, max["5min"], p5min)
    p10min = _decorate(activity.peak_10min_power, max["10min"], p10min)
    p20min = _decorate(activity.peak_20min_power, max["20min"], p20min)
    p30min = _decorate(activity.peak_30min_power, max["30min"], p30min)
    p60min = _decorate(activity.peak_60min_power, max["60min"], p60min)
    p90min = _decorate(activity.peak_90min_power, max["90min"], p90min) if "90min" in max else p90min
    p120min = _decorate(activity.peak_120min_power, max["120min"], p120min) if "120min" in max else p120min

    p_max = _decorate(activity.max_power, max["pMax"], p_max)
    p_avg = _decorate(activity.avg_power, max["pAvg"], p_avg)
    p_nor = _decorate(activity.normalised_power, max["pNor"], p_nor)
    intensity_factor_text = _decorate(activity.intensity_factor, max["IF"], intensity_factor_text)
    tss_text = _decorate(activity.tss, max["tss"], tss_text)

    # Color the aero decoupling
    coupling_text = format_aero_decoupling(aerobic_decoupling=activity.aerobic_decoupling, width=6)
    aerobic_efficiency = format_aero_efficiency(aerobic_efficiency=activity.aerobic_efficiency, width=6)

    # Format the CTL, ATL, and TSB
    ctl = activity.ctl
    atl = activity.atl
    tsb = ctl - atl

    ctl_text = format_ctl(ctl=ctl, width=3) if activity.first_for_day else "   "
    atl_text = format_atl(atl=atl, width=3) if activity.first_for_day else "   "
    tsb_text = _get_decorated_tsb(tsb=tsb) if activity.first_for_day else "   " 

    # Print the data.
    print(
        f"{rowid}   {date}   {activity_name}   {distance}      {elevation}   {start}   {duration}   {speed}   {p5sec}   {p30sec}   {p60sec}   {p5min}   {p10min}   {p20min}   {p30min}   {p60min}   {p90min}   {p120min}   {p_max}   {p_avg}   {p_nor}    {ftp_text}   {variability_index}   {intensity_factor_text}   {tss_text}   {coupling_text}   {aerobic_efficiency}   {ctl_text}   {atl_text}   {tsb_text}"
    )


def _print_summary(max: Dict[str, List[int]]):
    """
    Print a summary of our highest ever peaks.
    
    Args:
        max: Our collection of maximum peaks.
    """

    # Format each value.
    p5sec_0 = (str(max["5sec"][0]) if "5sec" in max else "").rjust(4)
    p30sec_0 = (str(max["30sec"][0]) if "30sec" in max else "").rjust(4)
    p60sec_0 = (str(max["60sec"][0]) if "60sec" in max else "").rjust(4)
    p5min_0 = (str(max["5min"][0]) if "5min" in max else "").rjust(4)
    p10min_0 = (str(max["10min"][0]) if "10min" in max else "").rjust(4)
    p20min_0 = (str(max["20min"][0]) if "20min" in max else "").rjust(4)
    p30min_0 = (str(max["30min"][0]) if "30min" in max else "").rjust(4)
    p60min_0 = (str(max["60min"][0]) if "60min" in max else "").rjust(4)
    p90min_0 = (str(max["90min"][0]) if "90min" in max else "").rjust(4)
    p120min_0 = (str(max["120min"][0]) if "120min" in max else "").rjust(4)
    pMax_0 = (str(max["pMax"][0]) if "pMax" in max else "").rjust(4)
    pAvg_0 = (str(max["pAvg"][0]) if "pAvg" in max else "").rjust(4)
    pNor_0 = (str(max["pNor"][0]) if "pNor" in max else "").rjust(4)
    if_0 = (format(max["IF"][0], ".2f").rjust(4)) if "IF" in max else "".rjust(4)
    tss_0 = (str(max["tss"][0]) if "tss" in max else "").rjust(4)
    ctl_0 = (str(max["ctl"][0]) if "ctl" in max else "").rjust(3)
    atl_0 = (str(max["atl"][0]) if "atl" in max else "").rjust(3)
    tsb_0 = _get_decorated_tsb(tsb=max["tsb"][0]) if "tsb" in max else "   "

    p5sec_1 = (str(max["5sec"][1]) if "5sec" in max else "").rjust(4)
    p30sec_1 = (str(max["30sec"][1]) if "30sec" in max else "").rjust(4)
    p60sec_1 = (str(max["60sec"][1]) if "60sec" in max else "").rjust(4)
    p5min_1 = (str(max["5min"][1]) if "5min" in max else "").rjust(4)
    p10min_1 = (str(max["10min"][1]) if "10min" in max else "").rjust(4)
    p20min_1 = (str(max["20min"][1]) if "20min" in max else "").rjust(4)
    p30min_1 = (str(max["30min"][1]) if "30min" in max else "").rjust(4)
    p60min_1 = (str(max["60min"][1]) if "60min" in max else "").rjust(4)
    p90min_1 = (str(max["90min"][1]) if "90min" in max else "").rjust(4)
    p120min_1 = (str(max["120min"][1]) if "120min" in max and len(max["120min"]) > 1 else "").rjust(4)
    pMax_1 = (str(max["pMax"][1]) if "pMax" in max else "").rjust(4)
    pAvg_1 = (str(max["pAvg"][1]) if "pAvg" in max else "").rjust(4)
    pNor_1 = (str(max["pNor"][1]) if "pNor" in max else "").rjust(4)
    if_1 = (format(max["IF"][1], ".2f").rjust(4)) if "IF" in max else "".rjust(4)
    tss_1 = (str(max["tss"][1]) if "tss" in max else "").rjust(4)
    ctl_1 = (str(max["ctl"][1]) if "ctl" in max else "").rjust(3)
    atl_1 = (str(max["atl"][1]) if "atl" in max else "").rjust(3)
    tsb_1 = _get_decorated_tsb(tsb=max["tsb"][1]) if "tsb" in max else "   "

    p5sec_2 = (str(max["5sec"][2]) if "5sec" in max else "").rjust(4)
    p30sec_2 = (str(max["30sec"][2]) if "30sec" in max else "").rjust(4)
    p60sec_2 = (str(max["60sec"][2]) if "60sec" in max else "").rjust(4)
    p5min_2 = (str(max["5min"][2]) if "5min" in max else "").rjust(4)
    p10min_2 = (str(max["10min"][2]) if "10min" in max else "").rjust(4)
    p20min_2 = (str(max["20min"][2]) if "20min" in max else "").rjust(4)
    p30min_2 = (str(max["30min"][2]) if "30min" in max else "").rjust(4)
    p60min_2 = (str(max["60min"][2]) if "60min" in max else "").rjust(4)
    p90min_2 = (str(max["90min"][2]) if "90min" in max  and len(max["90min"]) > 2 else "").rjust(4)
    p120min_2 = (str(max["120min"][2]) if "120min" in max and len(max["120min"]) > 2 else "").rjust(4)
    pMax_2 = (str(max["pMax"][2]) if "pMax" in max else "").rjust(4)
    pAvg_2 = (str(max["pAvg"][2]) if "pAvg" in max else "").rjust(4)
    pNor_2 = (str(max["pNor"][2]) if "pNor" in max else "").rjust(4)
    if_2 = (format(max["IF"][2], ".2f").rjust(4)) if "IF" in max else "".rjust(4)
    tss_2 = (str(max["tss"][2]) if "tss" in max else "").rjust(4)
    ctl_2 = (str(max["ctl"][2]) if "ctl" in max else "").rjust(3)
    atl_2 = (str(max["atl"][2]) if "atl" in max else "").rjust(3)
    tsb_2 = (str(max["tsb"][2]) if "tsb" in max else "").rjust(3)
    tsb_2 = _get_decorated_tsb(tsb=max["tsb"][2]) if "tsb" in max else "   "

    # Print the result.
    print()
    print(
        "                                                                                                                             ┌──────────────────────────────── Measurements in Watts ───────────────────────────────┐"
    )
    print(
        "                                                                                                                               5s    30s    60s     5m    10m    20m    30m    60m    90m   120m    Max    Avg   Norm                  I/F    TSS                     CTL   ATL   TSB"
    )
    print(
        "──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────                 ────   ────                     ───   ───   ───"
    )
    print(
        f"Peak values                                                                                                          \x1B[37;41mFirst\x1B[0m   {p5sec_0}   {p30sec_0}   {p60sec_0}   {p5min_0}   {p10min_0}   {p20min_0}   {p30min_0}   {p60min_0}   {p90min_0}   {p120min_0}   {pMax_0}   {pAvg_0}   {pNor_0}                 {if_0}   {tss_0}                     {ctl_0}   {atl_0}   {tsb_0}"
    )
    print(
        f"                                                                                                                    \x1B[30;43mSecond\x1B[0m   {p5sec_1}   {p30sec_1}   {p60sec_1}   {p5min_1}   {p10min_1}   {p20min_1}   {p30min_1}   {p60min_1}   {p90min_1}   {p120min_1}   {pMax_1}   {pAvg_1}   {pNor_1}                 {if_1}   {tss_1}                     {ctl_1}   {atl_1}   {tsb_1}"
    )
    print(
        f"                                                                                                                     \x1B[30;47mThird\x1B[0m   {p5sec_2}   {p30sec_2}   {p60sec_2}   {p5min_2}   {p10min_2}   {p20min_2}   {p30min_2}   {p60min_2}   {p90min_2}   {p120min_2}   {pMax_2}   {pAvg_2}   {pNor_2}                 {if_2}   {tss_2}                     {ctl_2}   {atl_2}   {tsb_2}"
    )
    print(
        "──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────                 ────   ────                     ───   ───   ───"
    )


def _print_fitness(fitness):
    """
    Print a summary of our current fitness.

    Args:
        fitness (Fitness): The fitness details — CTL, ATL, and TSB.
    """

    # Fetch CTL, ATL, and TSB
    ctl = str(int(fitness.ctl))  # Chronic training load (average TSS for last 42 days)
    atl = str(int(fitness.atl))  # Acute training load (average TSS for last 7 days)
    tsb = str(int(fitness.tsb))  # Training stress balance (CTL - ATL)

    # Decorate the TSB according to range
    if fitness.tsb < -30 or fitness.tsb >= -10 and fitness.tsb >= 10:
        tsb = "\x1B[38;5;196m" + tsb + "\x1B[0m"
    elif fitness.tsb < -10:
        tsb = "\x1B[38;5;41m" + tsb + "\x1B[0m"
    else:
        tsb = "\x1B[38;5;220m" + tsb + "\x1B[0m"

    # Show the fitness values
    print()
    print(f"Fitness (CTL) ... {ctl}")
    print(f"Fatigue (ATL) ... {atl}")
    print(f"Form (TSB) ...... {tsb}")
    print()


def _print_footer(*, weekly_figures: WeeklyFigures, max: Dict[str, List[int]]):
    """
    Print a footer.
    """

    # Print a separator
    _print_separator()

    # Format our totals and averages for the week
    distance = (format(round(weekly_figures.distance_total / 1000, 2), ".2f") + "km").rjust(8)
    elevation = (format(weekly_figures.elevation_total, ",d") + "m").rjust(6)
    duration_total = str(weekly_figures.duration_total).rjust(8)

    distance_average_delta = weekly_figures.distance_total / weekly_figures.work_days
    distance_average = (format(round(distance_average_delta / 1000, 2), ".2f") + "km").rjust(8)
    distance_maximum = (format(round(weekly_figures.max_distance / 1000, 2), ".2f") + "km").rjust(8)

    elevation_average_delta = int(weekly_figures.elevation_total / weekly_figures.work_days)
    elevation_average = (str(elevation_average_delta) + "m").rjust(6)
    elevation_maximum = (str(weekly_figures.max_elevation) + "m").rjust(6)

    duration_average_delta = weekly_figures.duration_total / weekly_figures.work_days
    duration_average = str(duration_average_delta).split(".")[0].rjust(8)
    duration_maximum = str(weekly_figures.max_duration).split(".")[0].rjust(8)

    tss_average_text = str(int(weekly_figures.tss_total / weekly_figures.work_days)).rjust(4)
    tss_total_text = str(int(weekly_figures.tss_total)).rjust(4)
    tss_maximum_text = str(int(weekly_figures.max_tss)).rjust(4)

    ctl_average_text = str(int(weekly_figures.ctl_total / weekly_figures.work_days)).rjust(3)
    ctl_maximum = str(weekly_figures.max_ctl).rjust(3)
    atl_average_text = str(int(weekly_figures.atl_total / weekly_figures.work_days)).rjust(3)
    atl_maximum = str(weekly_figures.max_atl).rjust(3)
    tsb_average_text = _get_decorated_tsb(tsb=int(weekly_figures.tsb_total / weekly_figures.work_days))
    tsb_maximum = _get_decorated_tsb(tsb=weekly_figures.max_tsb)

    def _average(values: List[int]) -> str:
        return str(int(sum(values) / len(values))).rjust(4) if values else "    "

    def _maximum(value: int) -> str:
        return str(value).rjust(4) if value else "    "

    avg_5sec = _average(weekly_figures.avg_5sec)
    avg_30sec = _average(weekly_figures.avg_30sec)
    avg_60sec = _average(weekly_figures.avg_60sec)
    avg_5min = _average(weekly_figures.avg_5min)
    avg_10min = _average(weekly_figures.avg_10min)
    avg_20min = _average(weekly_figures.avg_20min)
    avg_30min = _average(weekly_figures.avg_30min)
    avg_60min = _average(weekly_figures.avg_60min)
    avg_90min = _average(weekly_figures.avg_90min)
    avg_120min = _average(weekly_figures.avg_120min)

    max_5sec = _maximum(weekly_figures.max_5sec)
    max_30sec = _maximum(weekly_figures.max_30sec)
    max_60sec = _maximum(weekly_figures.max_60sec)
    max_5min = _maximum(weekly_figures.max_5min)
    max_10min = _maximum(weekly_figures.max_10min)
    max_20min = _maximum(weekly_figures.max_20min)
    max_30min = _maximum(weekly_figures.max_30min)
    max_60min = _maximum(weekly_figures.max_60min)
    max_90min = _maximum(weekly_figures.max_90min)
    max_120min = _maximum(weekly_figures.max_120min)
    max_pmax = _maximum(weekly_figures.max_pmax)
    max_pavg = _maximum(weekly_figures.max_pavg)
    max_pnor = _maximum(weekly_figures.max_pnor)
    max_if = format(weekly_figures.max_if, ".2f")

    max_5sec = _decorate(weekly_figures.max_5sec, max["5sec"], max_5sec)
    max_30sec = _decorate(weekly_figures.max_30sec, max["30sec"], max_30sec)
    max_60sec = _decorate(weekly_figures.max_60sec, max["60sec"], max_60sec)
    max_5min = _decorate(weekly_figures.max_5min, max["5min"], max_5min)
    max_10min = _decorate(weekly_figures.max_10min, max["10min"], max_10min)
    max_20min = _decorate(weekly_figures.max_20min, max["20min"], max_20min)
    max_30min = _decorate(weekly_figures.max_30min, max["30min"], max_30min)
    max_60min = _decorate(weekly_figures.max_60min, max["60min"], max_60min)
    max_90min = _decorate(weekly_figures.max_90min, max["90min"], max_90min) if "90min" in max.keys() else max_90min
    max_120min = _decorate(weekly_figures.max_120min, max["120min"], max_120min) if "120min" in max.keys() else max_120min
    max_pmax = _decorate(weekly_figures.max_pmax, max["pMax"], max_pmax)
    max_pavg = _decorate(weekly_figures.max_pavg, max["pAvg"], max_pavg)
    max_pnor = _decorate(weekly_figures.max_pnor, max["pNor"], max_pnor)

    print(
        f"                                                      Weekly totals   {distance}      {elevation}           {duration_total}                                                                                                                                {tss_total_text}"
    )
    print(
        f"                                                    Weekly averages   {distance_average}      {elevation_average}           {duration_average}                {avg_5sec}   {avg_30sec}   {avg_60sec}   {avg_5min}   {avg_10min}   {avg_20min}   {avg_30min}   {avg_60min}   {avg_90min}   {avg_120min}                                             {tss_average_text}                     {ctl_average_text}   {atl_average_text}   {tsb_average_text}"
    )
    print(
        f"                                                      Weekly maxima   {distance_maximum}      {elevation_maximum}           {duration_maximum}                {max_5sec}   {max_30sec}   {max_60sec}   {max_5min}   {max_10min}   {max_20min}   {max_30min}   {max_60min}   {max_90min}   {max_120min}   {max_pmax}   {max_pavg}   {max_pnor}                 {max_if}   {tss_maximum_text}                     {ctl_maximum}   {atl_maximum}   {tsb_maximum}"
    )
    print()


def _get_decorated_tsb(*, tsb: int):
    tsb_text = str(tsb).rjust(3)
    if tsb < -30 or tsb >= 10:
        return ("\x1B[38;5;196m" + tsb_text + "\x1B[0m")
    elif tsb < -10:
        return "\x1B[38;5;41m" + tsb_text + "\x1B[0m"
    else:
        return "\x1B[38;5;220m" + tsb_text + "\x1B[0m"

def _print_separator():
    """
    Print a commonly used separator.
    """
    print(
        "─────   ────────────────   ────────────────────────────────────────   ────────   ─────────   ─────   ────────   ──────────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ──────   ──────   ───   ───   ───"
    )


def _calculate_transient_values(activities: List[Activity]):
    """
    Calculate the transient values for each activity.
    
    Args:
        activities: The activities to calculate the transient values for.
    """

    for activity in activities:
        calculate_transient_values(activity)
    calculate_progressive_fitness(activities=activities)


def _load_max_values(activities: List[Activity]) -> Dict[str, List[int]]:
    """
    Given a list of activities, find the overall maximum for each of the peaks.
    
    Args:
        activities: Our activity data.
    
    Returns:
        Dict[str, Any]: The maximum peak for each time period.
    """

    # Initialise.
    max: Dict[str, List[Any]] = {}

    # Helper to find maximum.
    def _max(val: Any, label: str):
        if val is None:
            return
        if label in max:
            l = max[label]
        else:
            l = []
            max[label] = l
        if val not in l:
            l.append(val)

    # Visit each time period to find the maximum value.
    for activity in activities:
        _max(activity.peak_5sec_power, "5sec")
        _max(activity.peak_30sec_power, "30sec")
        _max(activity.peak_60sec_power, "60sec")
        _max(activity.peak_5min_power, "5min")
        _max(activity.peak_10min_power, "10min")
        _max(activity.peak_20min_power, "20min")
        _max(activity.peak_30min_power, "30min")
        _max(activity.peak_60min_power, "60min")
        _max(activity.peak_90min_power, "90min")
        _max(activity.peak_120min_power, "120min")
        _max(activity.max_power, "pMax")
        _max(int(activity.avg_power), "pAvg")
        _max(int(activity.normalised_power), "pNor")
        _max(activity.intensity_factor, "IF")
        _max(activity.tss, "tss")
        _max(activity.ctl, "ctl")
        _max(activity.atl, "atl")
        _max(activity.ctl-activity.atl, "tsb")

    # Now sort each list
    for key in max:
        max[key].sort(reverse=True)

    # The one exception is tsb… we want that sorted in ascending order
    max["tsb"].sort()

    # Done.
    return max


# Helper to decorate a peak with ANSI escape sequence highlights.
def _decorate(val: Any, max: List[Any], label: str) -> str:
    if max is None or val is None:
        return label
    if val >= max[0]:
        label = "\x1B[37;41m" + label + "\x1B[0m"
    elif val >= max[1]:
        label = "\x1B[30;43m" + label + "\x1B[0m"
    elif len(max) > 2 and val >= max[2]:
        label = "\x1B[30;47m" + label + "\x1B[0m"
    return label
