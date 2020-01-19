from datetime import datetime
from typing import List, Dict
from collections import defaultdict

from persistence import Persistence
from peaks import Peaks


def hr_report():
    """
    Print a HR report.
    
    This will fetch all the peaks from the database, then:
    
    - Find the maximum for each HR peak (e.g., max 5 seconds, 30 seconds, etc).
    - Print the peak HR for each activity, sorted in date order with a break
      between each week.
    - Print the maximum we found for each HR peak as a final summary.
    """

    # Load the peak data.
    db = Persistence()
    if not (peak_data := db.load_all()):
        print("No data to report on")
        return

    # Find the maximum for each value.
    max = _load_max_values(peak_data)

    # Print the peak data for each week.
    current_weekday = None
    for peak in peak_data:

        # Time to break to a new week?
        if current_weekday is None or current_weekday > peak.start_time.weekday():
            if current_weekday:
                _print_footer()
            _print_header()

        # Capture the weekday.
        current_weekday = peak.start_time.weekday()

        # Print the detail.
        _print_detail(peak, max)

    # Final footer.
    _print_footer()

    # Print the summary.
    _print_summary(max)


def _print_header():
    """
    Print the report header.
    """
    print()
    print(
        "Date               Start   Duration     5s    30s    60s     5m    10m    20m    30m    60m    90m   120m"
    )
    _print_separator()


def _print_detail(peak: Peaks, max: Dict[str, int]):
    """
    Print the detail for a particular activity.
    """

    # Find the date, start time, and duration.
    date = peak.start_time.strftime("%a %d %b, %Y")
    start = peak.start_time.strftime("%H:%M")
    duration = str(peak.end_time - peak.start_time).rjust(8)

    # Find each peak value.
    p5sec = str(peak.peak_5sec_hr).rjust(4) if peak.peak_5sec_hr else "    "
    p30sec = str(peak.peak_30sec_hr).rjust(4) if peak.peak_30sec_hr else "    "
    p60sec = str(peak.peak_60sec_hr).rjust(4) if peak.peak_60sec_hr else "    "
    p5min = str(peak.peak_5min_hr).rjust(4) if peak.peak_5min_hr else "    "
    p10min = str(peak.peak_10min_hr).rjust(4) if peak.peak_10min_hr else "    "
    p20min = str(peak.peak_20min_hr).rjust(4) if peak.peak_20min_hr else "    "
    p30min = str(peak.peak_30min_hr).rjust(4) if peak.peak_30min_hr else "    "
    p60min = str(peak.peak_60min_hr).rjust(4) if peak.peak_60min_hr else "    "
    p90min = str(peak.peak_90min_hr).rjust(4) if peak.peak_90min_hr else "    "
    p120min = str(peak.peak_120min_hr).rjust(4) if peak.peak_120min_hr else "    "

    # Helper to decorate a peak with ANSI escape sequence highlights.
    def _decorate(val: int, max: int, label: str) -> str:
        if val and val >= max:
            label = "\033[37;41m" + label + "\033[0m"
        return label

    # Highlight those peaks in this activity that are the highest peak we've ever seen.
    p5sec = _decorate(peak.peak_5sec_hr, max["5sec"], p5sec)
    p30sec = _decorate(peak.peak_30sec_hr, max["30sec"], p30sec)
    p60sec = _decorate(peak.peak_60sec_hr, max["60sec"], p60sec)
    p5min = _decorate(peak.peak_5min_hr, max["5min"], p5min)
    p10min = _decorate(peak.peak_10min_hr, max["10min"], p10min)
    p20min = _decorate(peak.peak_20min_hr, max["20min"], p20min)
    p30min = _decorate(peak.peak_30min_hr, max["30min"], p30min)
    p60min = _decorate(peak.peak_60min_hr, max["60min"], p60min)
    p90min = _decorate(peak.peak_90min_hr, max["90min"], p90min)
    p120min = _decorate(peak.peak_120min_hr, max["120min"], p120min)

    # Print the data.
    print(
        f"{date}   {start}   {duration}   {p5sec}   {p30sec}   {p60sec}   {p5min}   {p10min}   {p20min}   {p30min}   {p60min}   {p90min}   {p120min}"
    )


def _print_summary(max: Dict[str, int]):
    """
    Print a summary of our highest ever peaks.
    
    Args:
        max: Our collection of maximum peaks.
    """

    # Format each value.
    p5sec = (str(max["5sec"]) if "5sec" in max else "").rjust(4)
    p30sec = (str(max["30sec"]) if "30sec" in max else "").rjust(4)
    p60sec = (str(max["60sec"]) if "60sec" in max else "").rjust(4)
    p5min = (str(max["5min"]) if "5min" in max else "").rjust(4)
    p10min = (str(max["10min"]) if "10min" in max else "").rjust(4)
    p20min = (str(max["20min"]) if "20min" in max else "").rjust(4)
    p30min = (str(max["30min"]) if "30min" in max else "").rjust(4)
    p60min = (str(max["60min"]) if "60min" in max else "").rjust(4)
    p90min = (str(max["90min"]) if "90min" in max else "").rjust(4)
    p120min = (str(max["120min"]) if "120min" in max else "").rjust(4)

    # Print the result.
    print()
    print(
        "                                        5s    30s    60s     5m    10m    20m    30m    60m    90m   120m"
    )
    print(
        "───────────────────────────────────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────"
    )
    print(
        f"Peak values                           {p5sec}   {p30sec}   {p60sec}   {p5min}   {p10min}   {p20min}   {p30min}   {p60min}   {p90min}   {p120min}"
    )
    print(
        "───────────────────────────────────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────"
    )


def _print_footer():
    """
    Print a footer.
    """
    _print_separator()


def _print_separator():
    """
    Print a commonly used separator.
    """
    print(
        "────────────────   ─────   ────────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────"
    )


def _load_max_values(peak_data: List[Peaks]) -> Dict[str, int]:
    """
    Given a list of peaks, find the overall maximum for each of those peaks.
    
    Args:
        peak_data: Our peak data.
    
    Returns:
        Dict[str, int]: The maximum peak for each time period.
    """

    # Initialise.
    max: Dict[str, int] = defaultdict(int)

    # Helper to find maximum.
    def _max(val: int, label: str):
        if val and val > max[label]:
            max[label] = val

    # Visit each time period to find the maximum value.
    for peak in peak_data:
        _max(peak.peak_5sec_hr, "5sec")
        _max(peak.peak_30sec_hr, "30sec")
        _max(peak.peak_60sec_hr, "60sec")
        _max(peak.peak_5min_hr, "5min")
        _max(peak.peak_10min_hr, "10min")
        _max(peak.peak_20min_hr, "20min")
        _max(peak.peak_30min_hr, "30min")
        _max(peak.peak_60min_hr, "60min")
        _max(peak.peak_90min_hr, "90min")
        _max(peak.peak_120min_hr, "120min")

    # Done.
    return max
