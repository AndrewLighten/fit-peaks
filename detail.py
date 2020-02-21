from persistence import Persistence
from activity import Activity
from ftp import get_ftp
from typing import List
from collections import namedtuple, Counter
from calculations import calculate_transient_values
from calculation_data import AerobicDecoupling
from formatting import format_aero_decoupling, format_variability_index
from datetime import timedelta

PowerZoneDefinition = namedtuple("PowerZoneDefinition", "name upper colour")

POWER_ZONE_DEFINITIONS = [
    PowerZoneDefinition("Active Recovery", 55, "\033[38;5;46m"),
    PowerZoneDefinition("Endurance", 75,"\033[38;5;148m"),
    PowerZoneDefinition("Tempo", 90,"\033[38;5;214m"),
    PowerZoneDefinition("Lactate Threshold", 105, "\033[38;5;208m"),
    PowerZoneDefinition("VO2Max", 120, "\033[38;5;202m"),
    PowerZoneDefinition("Anaerobic Capacity", 0, "\033[38;5;196m"),
]

PowerZone = namedtuple("PowerZone", "name lower upper colour")

ZoneResult = namedtuple("ZoneResult", "name lower upper colour count")

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
    calculate_transient_values(activity)

    # Print our data
    _print_basic_data(activity)
    _print_power_data(activity)
    _print_zones(activity)
    if activity.aerobic_decoupling:
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

    variability_index_text = format_variability_index(activity=activity, width=0)
    intensity_factor_text = format(activity.intensity_factor, ".2f")
    tss_text = str(activity.tss)

    print("")
    print("\033[34m\033[1mPower data\033[0m")
    print("")
    print(f"    Average ............. {int(activity.avg_power)}W")
    print(f"    Maximum ............. {activity.max_power}W")
    print(f"    Normalised .......... {int(activity.normalised_power)}W")
    if variability_index_text:
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
    aerobic_decoupling = activity.aerobic_decoupling

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
    if activity.peak_5min_power or activity.peak_5min_hr:
        print(f"    5 min  {p5min}  {hr5min}")
    if activity.peak_10min_power or activity.peak_10min_hr:
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


def _print_zones(activity: Activity):

    # First calculate the actual zones
    zones = _calculate_zones(activity)

    # Now count the number of power values in each zone
    distribution = Counter(activity.raw_power)

    # Now go through each zone and count the number of power values in that zone
    zone_results: List[ZoneResult] = []

    for zone in zones:
        count = 0
        for power in range(zone.lower, zone.upper+1 if zone.upper else activity.max_power+1):
            count += distribution[power]
        zone_results.append(ZoneResult(name=zone.name, lower=zone.lower, upper=zone.upper, colour=zone.colour, count=count))

    # Print the result
    print()
    print("\033[34m\033[1mPower zones\033[0m")
    print("")

    print("    Zone                   Range:W   Duration     Pct%   Histogram")
    print("    --------------------   -------   --------   ------   " + ("-"*100))

    for result in zone_results:
        lower = str(result.lower).rjust(3)
        upper = str(result.upper if result.upper else activity.max_power if activity.max_power >= result.lower else "").rjust(3)
        sep = "-" if upper.strip() else "+"
        pct = (result.count / activity.duration_in_seconds) * 100
        pct_text = format(pct, ".1f").rjust(6)
        duration = str(timedelta(seconds=result.count)).rjust(8)
        bar = "█" * int(pct)
        print(f"    {result.name:20}   {lower}{sep}{upper}   {duration}  {pct_text}%   {result.colour}{bar}\033[0m")

    print("    --------------------   -------   --------   ------   " + ("-"*100))

def _calculate_zones(activity: Activity) -> List[PowerZone]:
    """
    Given an activity, determine what the various power zones are.
    
    Args:
        activity: The activity whose power zones we're calculating.
    
    Returns:
        The list of power zones. Each is a PowerZone with a name, lower,
        and upper watt limits.
    """

    # Initialise list of zones
    zones: List[PowerZone] = []

    # Visit each zone definition and calculate the power range it represents
    last_zone: PowerZone = None
    for zone_def in POWER_ZONE_DEFINITIONS:

        # Lower is the last zone's upper limit, plus one
        lower = last_zone.upper + 1 if last_zone else 0

        # Upper we'll calculate
        upper = int(activity.ftp * zone_def.upper / 100)

        # Create the zone, and add to the list
        last_zone = PowerZone(name=zone_def.name, lower=lower, upper=upper, colour=zone_def.colour)
        zones.append(last_zone)

    # Done
    return zones