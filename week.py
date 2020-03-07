import persistence
import datetime
import calculations
import calculation_data
import formatting
import typing
import dataclasses

from activity import Activity


@dataclasses.dataclass
class WeeklyTotals:

    work_days: int = 0

    distance_total: float = 0
    elevation_total: int = 0
    tss_total: int = 0
    duration_total: int = 0  # in seconds

    max_distance: float = 0
    max_elevation: int = 0
    max_tss: int = 0
    max_duration: int = 0  # in seconds
    max_speed: float = 0
    max_pmax: int = 0
    max_pavg: int = 0
    max_pnor: int = 0
    max_if: float = 0

    avg_distance: typing.List[float] = dataclasses.field(default_factory=list)
    avg_elevation: typing.List[int] = dataclasses.field(default_factory=list)
    avg_tss: typing.List[int] = dataclasses.field(default_factory=list)
    avg_duration: typing.List[int] = dataclasses.field(default_factory=list)  # in seconds


@dataclasses.dataclass
class DailyTotals:

    distance_total: float = 0
    elevation_total: int = 0
    tss_total: int = 0
    duration_total: int = 0  # in seconds


def week_report():
    """
    Print a snapshot of the past week's activities.
    """

    # Fetch the last week's activities.
    db = persistence.Persistence()
    start_date = (datetime.datetime.now() - datetime.timedelta(days=7)).date()
    if not (activities := db.load_for_week(start_date)):
        print(f"No activities this week")
        return

    # Calculate transient values.
    _calculate_transient_values(activities)

    # initialise totals
    weekly_totals = WeeklyTotals()

    # Print our details
    _print_header()
    _print_activity_details(activities, weekly_totals)
    _print_week_summary(weekly_totals)
    _print_footer()


def _print_activity_details(activities: typing.List[Activity], weekly_totals: WeeklyTotals):
    """
    Print the details for our activities.
    
    Args:
        activities:    The list of activities.
        weekly_totals: The weekly totals we're building up.
    """

    # Print the activity for each day
    current_weekday = None
    new_day = True
    first_day = True
    daily_totals = DailyTotals()

    # Visit each activity
    for activity in activities:

        # New day?
        if current_weekday is None or current_weekday != activity.start_time.weekday():
            if current_weekday is not None:
                _print_day_summary(daily_totals)
                daily_totals = DailyTotals()
            weekly_totals.work_days += 1
            new_day = True

        # Capture the current weekday
        current_weekday = activity.start_time.weekday()

        # Print the activity's details
        if (not first_day) and new_day:
            print("")
        _print_activity_detail(activity, new_day)
        new_day = False
        first_day = False

        # Accumulate
        _accumulate_day_detail(activity, daily_totals, weekly_totals)

    # Print the final daily otals
    _print_day_summary(daily_totals)


def _print_header():
    """
    Print the header.
    """

    print("                                                                                                                                                                      ┌──── Watts ─────┐")
    print("ID      Date               Activity                                                                           Start   Distance    Elevation   Duration        Speed    Max    Avg   Norm   VI    IF     TSS   AeroDe")
    _print_separator()


def _print_footer():
    """
    Print the footer.
    """
    pass


def _print_separator():
    """
    Print a separator line.
    """
    print("─────   ────────────────   ────────────────────────────────────────────────────────────────────────────────   ─────   ────────   ──────────   ────────   ──────────   ────   ────   ────   ──   ────   ────   ──────")


def _print_activity_detail(activity: Activity, new_day: bool):
    """
    Print the details for a particular activity.
    
    Args:
        activity: The activity to print.
        new_day:  True if this is the first report for a new day; otherwise, False.
    """

    # Format the attributes we'll print
    rowid = format(activity.rowid, "<5d")
    date = activity.start_time.strftime("%a %d %b, %Y") if new_day else "                "
    start = activity.start_time.strftime("%H:%M")
    duration = str(activity.end_time - activity.start_time).rjust(8)
    distance = (format(round(activity.distance / 1000, 2), ".2f") + "km").rjust(8)
    elevation = (format(activity.elevation, ",d") + "m").rjust(6) if activity.elevation else "".rjust(6)
    activity_name = activity.activity_name.ljust(80) if activity.activity_name else "".ljust(80)
    speed = (format(activity.speed_in_kmhr, ".2f") + "km/hr").rjust(10)
    p_max = str(int(activity.max_power)).rjust(4)
    p_avg = str(int(activity.avg_power)).rjust(4)
    p_nor = str(int(activity.normalised_power)).rjust(4)
    variability_index = formatting.format_variability_index(activity=activity, width=4)
    intensity_factor_text = format(activity.intensity_factor, ".2f")
    tss_text = format(activity.tss, ".0f").rjust(4)
    coupling_text = formatting.format_aero_decoupling(aerobic_decoupling=activity.aerobic_decoupling, width=6)

    print(f"{rowid}   {date}   {activity_name}   {start}   {distance}       {elevation}   {duration}   {speed}   {p_max}   {p_avg}   {p_nor} {variability_index}   {intensity_factor_text}   {tss_text}   {coupling_text}")


def _accumulate_day_detail(activity: Activity, daily_totals: DailyTotals, weekly_totals: WeeklyTotals):
    """
    Accumulate the details for a day.
    
    Args:
        activity:      The activity to add into our totals.
        daily_totals:  The day's totals.
        weekly_totals: The week's totals.
    """

    # Accumulate for the day
    daily_totals.distance_total += activity.distance
    daily_totals.elevation_total += activity.elevation
    daily_totals.tss_total += activity.tss
    daily_totals.duration_total += activity.duration_in_seconds

    # Accumulate for the week
    weekly_totals.distance_total += activity.distance
    weekly_totals.elevation_total += activity.elevation
    weekly_totals.tss_total += activity.tss
    weekly_totals.duration_total += activity.duration_in_seconds

    # Add in averages
    weekly_totals.avg_distance.append(activity.distance)
    weekly_totals.avg_elevation.append(activity.elevation)
    weekly_totals.avg_tss.append(activity.tss)
    weekly_totals.avg_duration.append(activity.duration_in_seconds)

    # Calculate maxima
    weekly_totals.max_distance = max(weekly_totals.max_distance, activity.distance)
    weekly_totals.max_elevation = max(weekly_totals.max_elevation, activity.elevation)
    weekly_totals.max_tss = max(weekly_totals.max_tss, activity.tss)
    weekly_totals.max_duration = max(weekly_totals.max_duration, activity.duration_in_seconds)
    weekly_totals.max_speed = max(weekly_totals.max_speed, activity.speed_in_kmhr)
    weekly_totals.max_pmax = max(weekly_totals.max_pmax, activity.max_power)
    weekly_totals.max_pavg = max(weekly_totals.max_pavg, activity.avg_power)
    weekly_totals.max_pnor = max(weekly_totals.max_pnor, activity.normalised_power)
    weekly_totals.max_if = max(weekly_totals.max_if, activity.intensity_factor)


def _print_day_summary(daily_totals: DailyTotals):
    """
    Print a summary of a day.
    
    Args:
        daily_totals: The day's totals.
    """

    # Format daily summaries
    duration = str(datetime.timedelta(seconds=daily_totals.duration_total)).rjust(8)
    distance = (format(round(daily_totals.distance_total / 1000, 2), ".2f") + "km").rjust(8)
    elevation = (format(daily_totals.elevation_total, ",d") + "m").rjust(6)
    tss_text = format(daily_totals.tss_total, ".0f").rjust(4)

    # Print them
    print(f"\x1B[38;5;240m\x1B[3m                                                                                                                      {distance}       {elevation}   {duration}                                                 {tss_text}\x1B[0m")


def _print_week_summary(weekly_totals: WeeklyTotals):
    """
    Print a summary of the week.
    
    Args:
        weekly_totals: The week's totals.
    """

    # Format daily summaries
    total_duration = str(datetime.timedelta(seconds=weekly_totals.duration_total)).rjust(8)
    total_distance = (format(round(weekly_totals.distance_total / 1000, 2), ".2f") + "km").rjust(8)
    total_elevation = (format(weekly_totals.elevation_total, ",d") + "m").rjust(6)
    total_tss = format(weekly_totals.tss_total, ".0f").rjust(4)

    # Format averages
    avg_distance = (format(round(sum(weekly_totals.avg_distance) / weekly_totals.work_days / 1000, 2), ".2f") + "km").rjust(8)
    avg_elevation = (str(int(sum(weekly_totals.avg_elevation) / weekly_totals.work_days)) + "m").rjust(6)
    avg_tss = str(int(sum(weekly_totals.avg_tss) / weekly_totals.work_days)).rjust(4)
    avg_duration = str(datetime.timedelta(seconds=(sum(weekly_totals.avg_duration) / weekly_totals.work_days))).split(".")[0].rjust(8)

    # Format maxima
    max_duration = str(datetime.timedelta(seconds=weekly_totals.max_duration)).rjust(8)
    max_distance = (format(round(weekly_totals.max_distance / 1000, 2), ".2f") + "km").rjust(8)
    max_elevation = (format(weekly_totals.max_elevation, ",d") + "m").rjust(6)
    max_tss = format(weekly_totals.max_tss, ".0f").rjust(4)
    max_speed = (format(weekly_totals.max_speed, ".2f") + "km/hr").rjust(10)
    max_pmax = str(int(weekly_totals.max_pmax)).rjust(4)
    max_pavg = str(int(weekly_totals.max_pavg)).rjust(4)
    max_pnor = str(int(weekly_totals.max_pnor)).rjust(4)
    max_if = format(weekly_totals.max_if, ".2f")

    # Print them
    _print_separator()
    print(f"\x1B[1m                                                                                            Totals for week           {total_distance}       {total_elevation}   {total_duration}                                                 {total_tss}\x1B[0m")
    print(f"\x1B[1m                                                                                           Averages per day           {avg_distance}       {avg_elevation}   {avg_duration}                                                 {avg_tss}\x1B[0m")
    print(f"\x1B[1m                                                                        Maximums from individual activities           {max_distance}       {max_elevation}   {max_duration}   {max_speed}   {max_pmax}   {max_pavg}   {max_pnor}        {max_if}   {max_tss}\x1B[0m")


def _print_fitness(fitness: calculation_data.Fitness):
    print("")
    print(f"\x1B[1mCTL: Critical training load (42 day TSS average) .... {fitness.ctl}\x1B[0m")
    print(f"\x1B[1mATL: Acute training load (7 day TSS average) ........ {fitness.atl}\x1B[0m")
    print(f"\x1B[1mTSB: Training stress balance (CTL-ATL) .............. {fitness.tsb}\x1B[0m")


def _calculate_transient_values(activities: typing.List[Activity]):
    """
    Calculate the transient values for each activity.
    
    Args:
        activities: The activities to calculate transient values for.
    """

    for activity in activities:
        calculations.calculate_transient_values(activity)
