from datetime import datetime, timedelta
from typing import List, Dict
from collections import defaultdict

from persistence import Persistence
from peaks import Peaks


def power_report():
    """
    Print a power report.
    
    This will fetch all the peaks from the database, then:
    
    - Find the maximum for each power peak (e.g., max 5 seconds, 30 seconds, etc).
    - Print the peak power for each activity, sorted in date order with a break
      between each week.
    - Print the maximum we found for each power peak as a final summary.
    """

    # Load the peak data.
    db = Persistence()
    if not (peak_data := db.load_all()):
        print("No data to report on")
        return

    # Find the maximum for each value.
    max = _load_max_values(peak_data)

    # Totals for the current week
    week_distance_total = 0
    week_elevation_total = 0
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

    # Print the peak data for each week.
    current_weekday = None
    for peak in peak_data:

        # Time to break to a new week?
        if current_weekday is None or current_weekday > peak.start_time.weekday():
            if current_weekday:
                _print_footer(
                    week_distance_total=week_distance_total,
                    week_elevation_total=week_elevation_total,
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

        # Capture the weekday.
        if current_weekday is None or current_weekday != peak.start_time.weekday():
            week_work_days = week_work_days + 1

        current_weekday = peak.start_time.weekday()

        # Print the detail.
        _print_detail(peak, max)

        # Find the duration.
        duration = peak.end_time - peak.start_time

        # Accumulate for this week
        week_distance_total = week_distance_total + peak.distance
        week_elevation_total = week_elevation_total + peak.elevation
        week_duration_total = week_duration_total + duration
        week_5sec_average.append(peak.peak_5sec_power)
        week_30sec_average.append(peak.peak_30sec_power)
        week_60sec_average.append(peak.peak_60sec_power)
        week_5min_average.append(peak.peak_5min_power)
        if peak.peak_10min_power:
            week_10min_average.append(peak.peak_10min_power)
        if peak.peak_20min_power:
            week_20min_average.append(peak.peak_20min_power)
        if peak.peak_30min_power:
            week_30min_average.append(peak.peak_30min_power)
        if peak.peak_60min_power:
            week_60min_average.append(peak.peak_60min_power)
        if peak.peak_90min_power:
            week_90min_average.append(peak.peak_90min_power)
        if peak.peak_120min_power:
            week_120min_average.append(peak.peak_120min_power)

    # Final footer.
    _print_footer(
        week_distance_total=week_distance_total,
        week_elevation_total=week_elevation_total,
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
        "Date               Activity                                                                           Distance   Elevation   Start   Duration     5s    30s    60s     5m    10m    20m    30m    60m    90m   120m"
    )
    _print_separator()


def _print_detail(peak: Peaks, max: Dict[str, List[int]]):
    """
    Print the detail for a particular activity.
    """

    # Find the date, start time, and duration.
    date = peak.start_time.strftime("%a %d %b, %Y")
    start = peak.start_time.strftime("%H:%M")
    duration = str(peak.end_time - peak.start_time).rjust(8)

    # Find the activity name
    distance = (format(round(peak.distance / 1000, 2), ".2f") + "km").rjust(8)
    elevation = (str(peak.elevation) + "m").rjust(6) if peak.elevation else "".rjust(6)
    activity_name = peak.activity_name.ljust(80) if peak.activity_name else "".ljust(80)

    # Find each peak value.
    p5sec = str(peak.peak_5sec_power).rjust(4) if peak.peak_5sec_power else "    "
    p30sec = str(peak.peak_30sec_power).rjust(4) if peak.peak_30sec_power else "    "
    p60sec = str(peak.peak_60sec_power).rjust(4) if peak.peak_60sec_power else "    "
    p5min = str(peak.peak_5min_power).rjust(4) if peak.peak_5min_power else "    "
    p10min = str(peak.peak_10min_power).rjust(4) if peak.peak_10min_power else "    "
    p20min = str(peak.peak_20min_power).rjust(4) if peak.peak_20min_power else "    "
    p30min = str(peak.peak_30min_power).rjust(4) if peak.peak_30min_power else "    "
    p60min = str(peak.peak_60min_power).rjust(4) if peak.peak_60min_power else "    "
    p90min = str(peak.peak_90min_power).rjust(4) if peak.peak_90min_power else "    "
    p120min = str(peak.peak_120min_power).rjust(4) if peak.peak_120min_power else "    "

    # Helper to decorate a peak with ANSI escape sequence highlights.
    def _decorate(val: int, max: List[int], label: str) -> str:
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
    p5sec = _decorate(peak.peak_5sec_power, max["5sec"], p5sec)
    p30sec = _decorate(peak.peak_30sec_power, max["30sec"], p30sec)
    p60sec = _decorate(peak.peak_60sec_power, max["60sec"], p60sec)
    p5min = _decorate(peak.peak_5min_power, max["5min"], p5min)
    p10min = _decorate(peak.peak_10min_power, max["10min"], p10min)
    p20min = _decorate(peak.peak_20min_power, max["20min"], p20min)
    p30min = _decorate(peak.peak_30min_power, max["30min"], p30min)
    p60min = _decorate(peak.peak_60min_power, max["60min"], p60min)
    p90min = _decorate(peak.peak_90min_power, max["90min"], p90min)
    p120min = _decorate(peak.peak_120min_power, max["120min"], p120min)

    # Print the data.
    print(
        f"{date}   {activity_name}   {distance}      {elevation}   {start}   {duration}   {p5sec}   {p30sec}   {p60sec}   {p5min}   {p10min}   {p20min}   {p30min}   {p60min}   {p90min}   {p120min}"
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

    p5sec_2 = (str(max["5sec"][2]) if "5sec" in max else "").rjust(4)
    p30sec_2 = (str(max["30sec"][2]) if "30sec" in max else "").rjust(4)
    p60sec_2 = (str(max["60sec"][2]) if "60sec" in max else "").rjust(4)
    p5min_2 = (str(max["5min"][2]) if "5min" in max else "").rjust(4)
    p10min_2 = (str(max["10min"][2]) if "10min" in max else "").rjust(4)
    p20min_2 = (str(max["20min"][2]) if "20min" in max else "").rjust(4)
    p30min_2 = (str(max["30min"][2]) if "30min" in max else "").rjust(4)
    p60min_2 = (str(max["60min"][2]) if "60min" in max else "").rjust(4)
    p90min_2 = (str(max["90min"][2]) if "90min" in max else "").rjust(4)
    p120min_2 = (
        str(max["120min"][2]) if "120min" in max and len(max["120min"]) > 2 else ""
    ).rjust(4)

    # Print the result.
    print()
    print(
        "                                                                                                                                                  5s    30s    60s     5m    10m    20m    30m    60m    90m   120m"
    )
    print(
        "─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────"
    )
    print(
        f"Peak values                                                                                                                             \033[37;41mFirst\033[0m   {p5sec_0}   {p30sec_0}   {p60sec_0}   {p5min_0}   {p10min_0}   {p20min_0}   {p30min_0}   {p60min_0}   {p90min_0}   {p120min_0}"
    )
    print(
        f"                                                                                                                                       \033[30;43mSecond\033[0m   {p5sec_1}   {p30sec_1}   {p60sec_1}   {p5min_1}   {p10min_1}   {p20min_1}   {p30min_1}   {p60min_1}   {p90min_1}   {p120min_1}"
    )
    print(
        f"                                                                                                                                        \033[30;47mThird\033[0m   {p5sec_2}   {p30sec_2}   {p60sec_2}   {p5min_2}   {p10min_2}   {p20min_2}   {p30min_2}   {p60min_2}   {p90min_2}   {p120min_2}"
    )
    print(
        "─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────"
    )


def _print_footer(
    *,
    week_distance_total: int,
    week_elevation_total: int,
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
    distance_average = (
        format(round(distance_average_delta / 1000, 2), ".2f") + "km"
    ).rjust(8)

    elevation_average_delta = int(week_elevation_total / week_work_days)
    elevation_average = (str(elevation_average_delta) + "m").rjust(6)

    duration_average_delta = week_duration_total / week_work_days
    duration_average = str(duration_average_delta).split(".")[0].rjust(8)

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
        f"                                                                                      Weekly totals   {distance}      {elevation}           {duration_total}"
    )
    print(
        f"                                                                                    Weekly averages   {distance_average}      {elevation_average}           {duration_average}   {p5sec}   {p30sec}   {p60sec}   {p5min}   {p10min}   {p20min}   {p30min}   {p60min}   {p90min}   {p120min}"
    )
    print()


def _print_separator():
    """
    Print a commonly used separator.
    """
    print(
        "────────────────   ────────────────────────────────────────────────────────────────────────────────   ────────   ─────────   ─────   ────────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────"
    )


def _load_max_values(peak_data: List[Peaks]) -> Dict[str, List[int]]:
    """
    Given a list of peaks, find the overall maximum for each of those peaks.
    
    Args:
        peak_data: Our peak data.
    
    Returns:
        Dict[str, int]: The maximum peak for each time period.
    """

    # Initialise.
    max: Dict[str, List[int]] = {}

    # Helper to find maximum.
    def _max(val: int, label: str):
        if val is None:
            return
        if label in max:
            l = max[label]
        else:
            l = []
            max[label] = l
        l.append(val)

    # Visit each time period to find the maximum value.
    for peak in peak_data:
        _max(peak.peak_5sec_power, "5sec")
        _max(peak.peak_30sec_power, "30sec")
        _max(peak.peak_60sec_power, "60sec")
        _max(peak.peak_5min_power, "5min")
        _max(peak.peak_10min_power, "10min")
        _max(peak.peak_20min_power, "20min")
        _max(peak.peak_30min_power, "30min")
        _max(peak.peak_60min_power, "60min")
        _max(peak.peak_90min_power, "90min")
        _max(peak.peak_120min_power, "120min")

    # Now sort each list
    for key in max:
        max[key].sort(reverse=True)

    # Done.
    return max
