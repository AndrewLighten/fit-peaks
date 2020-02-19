from persistence import Persistence
from activity import Activity
from ftp import get_ftp
from typing import List
from calculations import calculate_aerobic_decoupling
from calculation_data import AerobicDecoupling
from formatting import format_aero_decoupling

def detail_report(id: int):
    """
    Print a detailed report.
    
    This will fetch a specific activity from the database, then provide a detailed
    report for it.
    """

    # Load the peak data.
    db = Persistence()
    if not (activity := db.load_by_id(id)):
        print(f"Cannot find activity #{id}")
        return

    # Calculate transient data
    _calculate_transient_activity_values(activity)

    # Print our data
    _print_basic_data(activity)
    _print_power_data(activity)
    if activity.duration_in_seconds >= 300:
        _print_aerobic_decoupling(activity)
    _print_hr_data(activity)
    _print_peaks(activity)

    # Done
    print()


def _print_basic_data(activity: Activity):
    """
    Print the basic data for an activity.
    
    Args:
        activity: The activity to print data for.
    """

    # Activity ID and name
    print("")
    print(f"Activity #{activity.rowid}: \033[32m\033[1m{activity.activity_name}\033[0m")

    # Date, time, duration
    date = activity.start_time.strftime("%A %d %B, %Y")
    start = activity.start_time.strftime("%H:%M:%S")
    end = activity.end_time.strftime("%H:%M:%S")
    duration = str(activity.end_time - activity.start_time).rjust(8)

    print()
    print("\033[34m\033[1mBasic statistics\033[0m")
    print("")
    print(f"    Date ................ {date}")
    print(f"    Time ................ {start} to {end}")
    print(f"    Duration ............ {duration}")

    # Distances
    distance = format(round(activity.distance / 1000, 2), ".2f") + "km"
    elevation = (str(activity.elevation) + "m") if activity.elevation else ""
    average_speed = format(activity.speed_in_kmhr, ".2f")

    print()
    print(f"    Distance ............ {distance}")
    print(f"    Average speed ....... {average_speed}km/hr")
    print(f"    Elevation gain ...... {elevation}")


def _print_power_data(activity: Activity):
    """
    Print the power data we have for an activity.
    
    Args:
        activity: The activity to print power data for.
    """

    variability_index_text = format(activity.variability_index, ".2f")
    intensity_factor_text = format(activity.intensity_factor, ".2f")
    tss_text = str(activity.tss)

    print("")
    print("\033[34m\033[1mPower data\033[0m")
    print("")
    print(f"    Average ............. {int(activity.avg_power)}W")
    print(f"    Maximum ............. {activity.max_power}W")
    print(f"    Normalised .......... {int(activity.normalised_power)}W")
    print(f"    Variability index ... {variability_index_text}")
    print("")
    print(f"    FTP ................. {activity.ftp}W")
    print(f"    Intensity factor .... {intensity_factor_text}")
    print(f"    TSS ................. {tss_text}")


def _print_hr_data(activity: Activity):
    """
    Print the HR data we have for an activity.
    
    Args:
        activity: The activity to print HR data for.
    """
    print("")
    print("\033[34m\033[1mHeart data\033[0m")
    print("")
    print(f"    Average ............. {int(activity.avg_hr)} bpm")
    print(f"    Maximum ............. {activity.max_hr} bpm")


def _print_aerobic_decoupling(activity: Activity):
    """
    Calculate and print the aerobic decoupling ratio.

    Taken from https://www.trainingpeaks.com/blog/aerobic-endurance-and-decoupling.
    
    Args:
        activity: The activity data.
    """

    # Find the aerobic decoupling
    aerobic_decoupling: AerobicDecoupling = calculate_aerobic_decoupling(activity)

    # Format and display
    first_half_text = format(aerobic_decoupling.first_half_ratio, ".2f")
    second_half_text = format(aerobic_decoupling.second_half_ratio, ".2f")
    coupling_text = format_aero_decoupling(aerobic_decoupling=aerobic_decoupling, width=0)

    print("")
    print("\033[34m\033[1mAerobic coupling\033[0m")
    print("")
    print(f"    Overall ............. {coupling_text}")
    print(f"    First half .......... {first_half_text} (pAvg:hrAvg)")
    print(f"    Second half ......... {second_half_text} (pAvg:hrAvg)")


def _print_peaks(activity: Activity):
    """
    Print the peak details for an activity.
    
    Args:
        activity: The activity to report on.
    """

    # Find power details
    p5sec = str(activity.peak_5sec_power).rjust(9) if activity.peak_5sec_power else "         "
    p30sec = str(activity.peak_30sec_power).rjust(9) if activity.peak_30sec_power else "         "
    p60sec = str(activity.peak_60sec_power).rjust(9) if activity.peak_60sec_power else "         "
    p5min = str(activity.peak_5min_power).rjust(9) if activity.peak_5min_power else "         "
    p10min = str(activity.peak_10min_power).rjust(9) if activity.peak_10min_power else "         "
    p20min = str(activity.peak_20min_power).rjust(9) if activity.peak_20min_power else "         "
    p30min = str(activity.peak_30min_power).rjust(9) if activity.peak_30min_power else "         "
    p60min = str(activity.peak_60min_power).rjust(9) if activity.peak_60min_power else "         "
    p90min = str(activity.peak_90min_power).rjust(9) if activity.peak_90min_power else "         "
    p120min = str(activity.peak_120min_power).rjust(9) if activity.peak_120min_power else "         "

    # Find HR details
    hr5sec = str(activity.peak_5sec_hr).rjust(9) if activity.peak_5sec_hr else "         "
    hr30sec = str(activity.peak_30sec_hr).rjust(9) if activity.peak_30sec_hr else "         "
    hr60sec = str(activity.peak_60sec_hr).rjust(9) if activity.peak_60sec_hr else "         "
    hr5min = str(activity.peak_5min_hr).rjust(9) if activity.peak_5min_hr else "         "
    hr10min = str(activity.peak_10min_hr).rjust(9) if activity.peak_10min_hr else "         "
    hr20min = str(activity.peak_20min_hr).rjust(9) if activity.peak_20min_hr else "         "
    hr30min = str(activity.peak_30min_hr).rjust(9) if activity.peak_30min_hr else "         "
    hr60min = str(activity.peak_60min_hr).rjust(9) if activity.peak_60min_hr else "         "
    hr90min = str(activity.peak_90min_hr).rjust(9) if activity.peak_90min_hr else "         "
    hr120min = str(activity.peak_120min_hr).rjust(9) if activity.peak_120min_hr else "         "

    print()
    print("\033[34m\033[1mPeaks\033[0m")
    print("")
    print("           Power (W)   HR (bpm)")
    print("           ---------  ---------")
    print(f"    5 sec  {p5sec}  {hr5sec}")
    print(f"    30 sec {p30sec}  {hr30sec}")
    print(f"    60 sec {p60sec}  {hr60sec}")
    print(f"    5 min  {p5min}  {hr5min}")
    print(f"    10 min {p10min}  {hr10min}")
    if activity.peak_20min_power or activity.peak_20min_hr:
        print(f"    20 min {p20min}  {hr20min}")
    if activity.peak_30min_power or activity.peak_30min_hr:
        print(f"    30 min {p30min}  {hr30min}")
    if activity.peak_60min_power or activity.peak_60min_hr:
        print(f"    60 min {p60min}  {hr60min}")
    if activity.peak_90min_power or activity.peak_90min_hr:
        print(f"    90 min {p90min}  {hr90min}")
    if activity.peak_120min_power or activity.peak_120min_hr:
        print(f"    120 min{p120min}  {hr120min}")
    print("           ---------  ---------")


def _calculate_transient_activity_values(activity: Activity):
    """
    Calculate the transient values for a specific activity.
    
    Args:
        activity: The activity to calculate the transient values for.
    """

    # Calculate some power details
    # Taken from https://medium.com/critical-powers/formulas-from-training-and-racing-with-a-power-meter-2a295c661b46
    activity.variability_index = activity.normalised_power / activity.avg_power
    activity.ftp = get_ftp(activity.start_time)
    activity.intensity_factor = activity.normalised_power / activity.ftp if activity.ftp else 0

    activity.duration_in_seconds = (activity.end_time - activity.start_time).seconds
    activity.tss = (
        int(
            (activity.duration_in_seconds * activity.normalised_power * activity.intensity_factor) / (activity.ftp * 36)
        )
        if activity.ftp
        else 0
    )

    distance_in_meters = activity.distance
    speed_in_ms = distance_in_meters / activity.duration_in_seconds
    activity.speed_in_kmhr = speed_in_ms * 3600 / 1000
