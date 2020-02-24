from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import defaultdict

from persistence import Persistence
from activity import Activity
from athlete import get_ftp
from calculations import calculate_transient_values
from calculation_data import AerobicDecoupling
from formatting import format_aero_decoupling, format_variability_index


def power_report():
    """
    Print a power report.
    
    This will fetch all the activities from the database, then:
    
    - Find the maximum for each power peak (e.g., max 5 seconds, 30 seconds, etc).
    - Print the activity data for each activity, sorted in date order with a break
      between each week.
    - Print the maximum we found for each power peak as a final summary.
    """

    # Load the activity data.
    db = Persistence()
    if not (activities := db.load_all()):
        print("No data to report on")
        return

    # Calculate transient values
    _calculate_transient_values(activities)

    # Find the maximum for each value.
    max = _load_max_values(activities)

    # Establish the prevailing FTP
    prevailing_ftp = None

    # Totals for the current week
    week_distance_total = 0
    week_elevation_total = 0
    week_tss_total = 0
    week_duration_total = timedelta()
    week_work_days = 0
    week_5sec_average = []
    week_30sec_average = []
    week_60sec_average = []
    week_5min_average = []
    week_10min_average = []
    week_20min_average = []
    week_30min_average = []
    week_60min_average = []
    week_90min_average = []
    week_120min_average = []

    # Print the activity data for each week.
    current_weekday = None
    for activity in activities:

        # Time to break to a new week?
        if current_weekday is None or current_weekday > activity.start_time.weekday():
            if current_weekday:
                _print_footer(
                    week_distance_total=week_distance_total,
                    week_elevation_total=week_elevation_total,
                    week_tss_total=week_tss_total,
                    week_duration_total=week_duration_total,
                    week_work_days=week_work_days,
                    week_5sec_average=week_5sec_average,
                    week_30sec_average=week_30sec_average,
                    week_60sec_average=week_60sec_average,
                    week_5min_average=week_5min_average,
                    week_10min_average=week_10min_average,
                    week_20min_average=week_20min_average,
                    week_30min_average=week_30min_average,
                    week_60min_average=week_60min_average,
                    week_90min_average=week_90min_average,
                    week_120min_average=week_120min_average,
                )
                week_distance_total = 0
                week_elevation_total = 0
                week_tss_total = 0
                week_duration_total = timedelta(0)
                week_work_days = 0
                week_5sec_average = []
                week_30sec_average = []
                week_60sec_average = []
                week_5min_average = []
                week_10min_average = []
                week_20min_average = []
                week_30min_average = []
                week_60min_average = []
                week_90min_average = []
                week_120min_average = []

            _print_header()
            any_data_since_header = False

        # Capture the weekday.
        if current_weekday is None or current_weekday != activity.start_time.weekday():
            week_work_days = week_work_days + 1
            new_day = True
            if any_data_since_header:
                print()

        current_weekday = activity.start_time.weekday()

        # New FTP?
        activity_ftp = get_ftp(activity.start_time)
        new_ftp = prevailing_ftp and activity_ftp > prevailing_ftp
        prevailing_ftp = activity_ftp

        # Print the detail.
        _print_detail(activity=activity, max=max, new_ftp=new_ftp, new_day=new_day)
        new_day = False
        any_data_since_header = True

        # Find the duration.
        duration = activity.end_time - activity.start_time

        # Accumulate for this week
        week_distance_total = week_distance_total + activity.distance
        if activity.elevation:
            week_elevation_total = week_elevation_total + activity.elevation
        week_tss_total = week_tss_total + activity.tss
        week_duration_total = week_duration_total + duration
        week_5sec_average.append(activity.peak_5sec_power)
        week_30sec_average.append(activity.peak_30sec_power)
        week_60sec_average.append(activity.peak_60sec_power)
        if activity.peak_5min_power:
            week_5min_average.append(activity.peak_5min_power)
        if activity.peak_10min_power:
            week_10min_average.append(activity.peak_10min_power)
        if activity.peak_20min_power:
            week_20min_average.append(activity.peak_20min_power)
        if activity.peak_30min_power:
            week_30min_average.append(activity.peak_30min_power)
        if activity.peak_60min_power:
            week_60min_average.append(activity.peak_60min_power)
        if activity.peak_90min_power:
            week_90min_average.append(activity.peak_90min_power)
        if activity.peak_120min_power:
            week_120min_average.append(activity.peak_120min_power)

    # Final footer.
    _print_footer(
        week_distance_total=week_distance_total,
        week_elevation_total=week_elevation_total,
        week_tss_total=week_tss_total,
        week_duration_total=week_duration_total,
        week_work_days=week_work_days,
        week_5sec_average=week_5sec_average,
        week_30sec_average=week_30sec_average,
        week_60sec_average=week_60sec_average,
        week_5min_average=week_5min_average,
        week_10min_average=week_10min_average,
        week_20min_average=week_20min_average,
        week_30min_average=week_30min_average,
        week_60min_average=week_60min_average,
        week_90min_average=week_90min_average,
        week_120min_average=week_120min_average,
    )

    # Print the summary.
    _print_summary(max)


def _print_header():
    """
    Print the report header.
    """
    print()
    print(
        "                                                                                                                                                                     ┌──────────────────────────────────── Measurements in Watts ──────────────────────────────────┐"
    )
    print(
        "ID      Date               Activity                                                                           Distance   Elevation   Start   Duration      Speed       5s    30s    60s     5m    10m    20m    30m    60m    90m   120m   pMax   pAvg   pNor    FTP    V/I    I/F    TSS   AeroDe"
    )
    _print_separator()


def _print_detail(*, activity: Activity, max: Dict[str, List[int]], new_ftp: bool, new_day: bool):
    """
    Print the detail for a particular activity.
    """

    # Find the ID, date, start time, and duration.
    rowid = format(activity.rowid, "<5d")
    date = activity.start_time.strftime("%a %d %b, %Y") if new_day else '                '
    start = activity.start_time.strftime("%H:%M")
    duration = str(activity.end_time - activity.start_time).rjust(8)

    # Find the activity name
    distance = (format(round(activity.distance / 1000, 2), ".2f") + "km").rjust(8)
    elevation = (str(activity.elevation) + "m").rjust(6) if activity.elevation else "".rjust(6)
    activity_name = activity.activity_name.ljust(80) if activity.activity_name else "".ljust(80)
    speed = (format(activity.speed_in_kmhr, ".2f") + "km/hr").rjust(10)

    # Find the power figures
    p_max = str(int(activity.max_power)).rjust(4)
    p_avg = str(int(activity.avg_power)).rjust(4)
    p_nor = str(int(activity.normalised_power)).rjust(4)

    variability_index = format_variability_index(activity=activity, width=4)
    ftp_text = str(activity.ftp)
    if new_ftp:
        ftp_text = "\033[38;5;40m" + ftp_text + "\033[0m"
    else:
        ftp_text = "\033[38;5;238m" + ftp_text + "\033[0m"
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

    # Helper to decorate a peak with ANSI escape sequence highlights.
    def _decorate(val: Any, max: List[Any], label: str) -> str:
        if max is None or val is None:
            return label
        if val >= max[0]:
            label = "\033[37;41m" + label + "\033[0m"
        elif val >= max[1]:
            label = "\033[30;43m" + label + "\033[0m"
        elif len(max) > 2 and val >= max[2]:
            label = "\033[30;47m" + label + "\033[0m"
        return label

    # Highlight those peaks in this activity that are the highest peak we've ever seen.
    p5sec = _decorate(activity.peak_5sec_power, max["5sec"], p5sec)
    p30sec = _decorate(activity.peak_30sec_power, max["30sec"], p30sec)
    p60sec = _decorate(activity.peak_60sec_power, max["60sec"], p60sec)
    p5min = _decorate(activity.peak_5min_power, max["5min"], p5min)
    p10min = _decorate(activity.peak_10min_power, max["10min"], p10min)
    p20min = _decorate(activity.peak_20min_power, max["20min"], p20min)
    p30min = _decorate(activity.peak_30min_power, max["30min"], p30min)
    p60min = _decorate(activity.peak_60min_power, max["60min"], p60min)
    p90min = _decorate(activity.peak_90min_power, max["90min"], p90min)
    if activity.peak_120min_power:
        p120min = _decorate(activity.peak_120min_power, max["120min"], p120min)
    p_max = _decorate(activity.max_power, max["pMax"], p_max)
    p_avg = _decorate(activity.avg_power, max["pAvg"], p_avg)
    p_nor = _decorate(activity.normalised_power, max["pNor"], p_nor)
    intensity_factor_text = _decorate(activity.intensity_factor, max["IF"], intensity_factor_text)
    tss_text = _decorate(activity.tss, max["tss"], tss_text)
    coupling_text = format_aero_decoupling(aerobic_decoupling=activity.aerobic_decoupling, width=6)

    # Color the aero decoupling

    # Print the data.
    print(
        f"{rowid}   {date}   {activity_name}   {distance}      {elevation}   {start}   {duration}   {speed}   {p5sec}   {p30sec}   {p60sec}   {p5min}   {p10min}   {p20min}   {p30min}   {p60min}   {p90min}   {p120min}   {p_max}   {p_avg}   {p_nor}    {ftp_text}   {variability_index}   {intensity_factor_text}   {tss_text}   {coupling_text}"
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

    p5sec_1 = (str(max["5sec"][1]) if "5sec" in max else "").rjust(4)
    p30sec_1 = (str(max["30sec"][1]) if "30sec" in max else "").rjust(4)
    p60sec_1 = (str(max["60sec"][1]) if "60sec" in max else "").rjust(4)
    p5min_1 = (str(max["5min"][1]) if "5min" in max else "").rjust(4)
    p10min_1 = (str(max["10min"][1]) if "10min" in max else "").rjust(4)
    p20min_1 = (str(max["20min"][1]) if "20min" in max else "").rjust(4)
    p30min_1 = (str(max["30min"][1]) if "30min" in max else "").rjust(4)
    p60min_1 = (str(max["60min"][1]) if "60min" in max else "").rjust(4)
    p90min_1 = (str(max["90min"][1]) if "90min" in max else "").rjust(4)
    p120min_1 = (str(max["120min"][1]) if "120min" in max else "").rjust(4)
    pMax_1 = (str(max["pMax"][1]) if "pMax" in max else "").rjust(4)
    pAvg_1 = (str(max["pAvg"][1]) if "pAvg" in max else "").rjust(4)
    pNor_1 = (str(max["pNor"][1]) if "pNor" in max else "").rjust(4)
    if_1 = (format(max["IF"][1], ".2f").rjust(4)) if "IF" in max else "".rjust(4)
    tss_1 = (str(max["tss"][1]) if "tss" in max else "").rjust(4)

    p5sec_2 = (str(max["5sec"][2]) if "5sec" in max else "").rjust(4)
    p30sec_2 = (str(max["30sec"][2]) if "30sec" in max else "").rjust(4)
    p60sec_2 = (str(max["60sec"][2]) if "60sec" in max else "").rjust(4)
    p5min_2 = (str(max["5min"][2]) if "5min" in max else "").rjust(4)
    p10min_2 = (str(max["10min"][2]) if "10min" in max else "").rjust(4)
    p20min_2 = (str(max["20min"][2]) if "20min" in max else "").rjust(4)
    p30min_2 = (str(max["30min"][2]) if "30min" in max else "").rjust(4)
    p60min_2 = (str(max["60min"][2]) if "60min" in max else "").rjust(4)
    p90min_2 = (str(max["90min"][2]) if "90min" in max else "").rjust(4)
    p120min_2 = (str(max["120min"][2]) if "120min" in max and len(max["120min"]) > 2 else "").rjust(4)
    pMax_2 = (str(max["pMax"][2]) if "pMax" in max else "").rjust(4)
    pAvg_2 = (str(max["pAvg"][2]) if "pAvg" in max else "").rjust(4)
    pNor_2 = (str(max["pNor"][2]) if "pNor" in max else "").rjust(4)
    if_2 = (format(max["IF"][2], ".2f").rjust(4)) if "IF" in max else "".rjust(4)
    tss_2 = (str(max["tss"][2]) if "tss" in max else "").rjust(4)

    # Print the result.
    print()
    print(
        "                                                                                                                                                                     ┌──────────────────────────────── Measurements in Watts ───────────────────────────────┐"
    )
    print(
        "                                                                                                                                                                       5s    30s    60s     5m    10m    20m    30m    60m    90m   120m   pMax   pAvg   pNor                  I/F    TSS"
    )
    print(
        "──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────                 ────   ────"
    )
    print(
        f"Peak values                                                                                                                                                  \033[37;41mFirst\033[0m   {p5sec_0}   {p30sec_0}   {p60sec_0}   {p5min_0}   {p10min_0}   {p20min_0}   {p30min_0}   {p60min_0}   {p90min_0}   {p120min_0}   {pMax_0}   {pAvg_0}   {pNor_0}                 {if_0}   {tss_0}"
    )
    print(
        f"                                                                                                                                                            \033[30;43mSecond\033[0m   {p5sec_1}   {p30sec_1}   {p60sec_1}   {p5min_1}   {p10min_1}   {p20min_1}   {p30min_1}   {p60min_1}   {p90min_1}   {p120min_1}   {pMax_1}   {pAvg_1}   {pNor_1}                 {if_1}   {tss_1}"
    )
    print(
        f"                                                                                                                                                             \033[30;47mThird\033[0m   {p5sec_2}   {p30sec_2}   {p60sec_2}   {p5min_2}   {p10min_2}   {p20min_2}   {p30min_2}   {p60min_2}   {p90min_2}   {p120min_2}   {pMax_2}   {pAvg_2}   {pNor_2}                 {if_2}   {tss_2}"
    )
    print(
        "──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────                 ────   ────"
    )


def _print_footer(
    *,
    week_distance_total: int,
    week_elevation_total: int,
    week_tss_total: int,
    week_duration_total: timedelta,
    week_work_days: int,
    week_5sec_average: List[int],
    week_30sec_average: List[int],
    week_60sec_average: List[int],
    week_5min_average: List[int],
    week_10min_average: List[int],
    week_20min_average: List[int],
    week_30min_average: List[int],
    week_60min_average: List[int],
    week_90min_average: List[int],
    week_120min_average: List[int],
):
    """
    Print a footer.
    """

    # Print a separator
    _print_separator()

    # Format our totals and averages for the week
    distance = (format(round(week_distance_total / 1000, 2), ".2f") + "km").rjust(8)
    elevation = (str(week_elevation_total) + "m").rjust(6)
    duration_total = str(week_duration_total).rjust(8)

    distance_average_delta = week_distance_total / week_work_days
    distance_average = (format(round(distance_average_delta / 1000, 2), ".2f") + "km").rjust(8)

    elevation_average_delta = int(week_elevation_total / week_work_days)
    elevation_average = (str(elevation_average_delta) + "m").rjust(6)

    duration_average_delta = week_duration_total / week_work_days
    duration_average = str(duration_average_delta).split(".")[0].rjust(8)

    tss_average_text = str(int(week_tss_total / week_work_days)).rjust(4)
    tss_total_text = str(int(week_tss_total)).rjust(4)

    def _average(values: List[int]) -> str:
        return str(int(sum(values) / len(values))).rjust(4) if values else "    "

    p5sec = _average(week_5sec_average)
    p30sec = _average(week_30sec_average)
    p60sec = _average(week_60sec_average)
    p5min = _average(week_5min_average)
    p10min = _average(week_10min_average)
    p20min = _average(week_20min_average)
    p30min = _average(week_30min_average)
    p60min = _average(week_60min_average)
    p90min = _average(week_90min_average)
    p120min = _average(week_120min_average)

    print(
        f"                                                                                              Weekly totals   {distance}      {elevation}           {duration_total}                                                                                                                                {tss_total_text}"
    )
    print(
        f"                                                                                            Weekly averages   {distance_average}      {elevation_average}           {duration_average}                {p5sec}   {p30sec}   {p60sec}   {p5min}   {p10min}   {p20min}   {p30min}   {p60min}   {p90min}   {p120min}                                             {tss_average_text}"
    )
    print()


def _print_separator():
    """
    Print a commonly used separator.
    """
    print(
        "─────   ────────────────   ────────────────────────────────────────────────────────────────────────────────   ────────   ─────────   ─────   ────────   ──────────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ──────"
    )


def _calculate_transient_values(activities: List[Activity]):
    """
    Calculate the transient values for each activity.
    
    Args:
        activities: The activities to calculate the transient values for.
    """

    for activity in activities:
        calculate_transient_values(activity)


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

    # Now sort each list
    for key in max:
        max[key].sort(reverse=True)

    # Done.
    return max
