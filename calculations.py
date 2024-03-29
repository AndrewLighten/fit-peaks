from activity import Activity
from collections import namedtuple
from typing import List, Optional
from calculation_data import AerobicDecoupling, Fitness
from athlete import get_ftp
from collections import deque
import datetime
import itertools
import math


def calculate_transient_values(activity: Activity):
    """
    Calculate the transient values for a specific activity.

    Lots of this logic comes from https://medium.com/critical-powers/formulas-from-training-and-racing-with-a-power-meter-2a295c661b46.

    Args:
        activity: The activity to calculate the transient values for.
    """
    # Simple stuff
    activity.variability_index = round(((activity.normalised_power - activity.avg_power) / activity.normalised_power) * 100, 0)
    activity.ftp = get_ftp(activity.start_time)
    activity.intensity_factor = activity.normalised_power / activity.ftp if activity.ftp else 0

    activity.duration_in_seconds = (activity.end_time - activity.start_time).seconds
    activity.tss = int((activity.duration_in_seconds * activity.normalised_power * activity.intensity_factor) / (activity.ftp * 36)) if activity.ftp else 0

    distance_in_meters = activity.distance
    speed_in_ms = distance_in_meters / activity.duration_in_seconds
    activity.speed_in_kmhr = speed_in_ms * 3600 / 1000

    # Now calculate aerobic decoupling
    # See https://www.trainingpeaks.com/blog/aerobic-endurance-and-decoupling.
    if distance_in_meters >= 10000:
        activity.aerobic_decoupling = calculate_aerobic_decoupling(activity)
        activity.aerobic_efficiency = activity.normalised_power / activity.avg_hr


def calculate_progressive_fitness(activities: List[Activity]):
    """
    Calculate the CTL and ATL for each day in the list of activities.

    Args:
        activities (List[Activity]): The list of activities to calculate for.
    """

    # Let's start by setting the 'first_for_day' flag for each activity; we need this later
    _determine_first_for_day(activities=activities)

    # Now we'll walk through the activities and calculate the CTL and ATL for each one
    for idx, activity in enumerate(activities):

        # If it's not the first for the date, copy from the previous activity
        if not activity.first_for_day:
            activity.ctl = activities[idx - 1].ctl
            activity.atl = activities[idx - 1].atl
            continue

        # It's the first activity for the day — let's calculate CTL and ATL for this day

        # Step 1 — grab the date
        activity_date = activity.start_time.date()

        # Step 2 — determine the earliest date we want in the CTL and ATL
        earliest_date_for_ctl = activity_date - datetime.timedelta(days=42)
        earliest_date_for_atl = activity_date - datetime.timedelta(days=7)

        # Step 3 — setup TSS buffers for CTL and ATL
        ctl_tss_sum: int = 0
        ctl_tss_count: int = 1
        atl_tss_sum: int = 0
        atl_tss_count: int = 1

        # Step 4 — walk backward and sum TSS
        for i in range(idx - 1, 0, -1):
            subject = activities[i]
            subject_date = subject.start_time.date()
            if subject_date < earliest_date_for_ctl:
                break
            ctl_tss_sum += subject.tss
            if subject.first_for_day:
                ctl_tss_count += 1
            if subject_date < earliest_date_for_atl:
                continue
            atl_tss_sum += subject.tss
            if subject.first_for_day:
                atl_tss_count += 1

        # Step 5 — store the CTL and ATL for this activity
        activity.ctl = int(ctl_tss_sum / 42) if ctl_tss_count > 0 else 0
        activity.atl = int(atl_tss_sum / 7) if atl_tss_count > 0 else 0


def _determine_first_for_day(activities: List[Activity]):
    """
    Determine which activity is the first of each day (give we have multiple activities per day)

    Args:
        activities (List[Activity]): The list of activities to separate by day
    """

    # Make sure we got an activity list
    assert activities

    # Buffer for the currennt date
    current_date: datetime.date = None

    # Visit each activity. When the date changes from the previous activity, it's the first
    # one for the date.
    for activity in activities:
        activity_date = activity.start_time.date()
        if current_date is None or activity_date != current_date:
            activity.first_for_day = True
            current_date = activity_date
        else:
            activity.first_for_day = False


def calculate_aerobic_decoupling(activity: Activity) -> Optional[AerobicDecoupling]:
    """
    Calculate the aerobic decoupling for an activity.

    Args:
        activity (Activity): The activity to calculate for.

    Returns:
        The aerobic decoupling.
    """

    # Split the power and HR data in half
    assert len(activity.raw_power) == len(activity.raw_hr)
    half_way_point = int(len(activity.raw_power) / 2)

    first_half_power = activity.raw_power[0:half_way_point]
    first_half_hr = activity.raw_hr[0:half_way_point]

    second_half_power = activity.raw_power[half_way_point:]
    second_half_hr = activity.raw_hr[half_way_point:]

    # If either is empty, we don't have enough data to calculate
    if not first_half_power or not second_half_power:
        return None

    # Calculate the first half's power-to-hr ratio
    first_half_ratio = _calculate_aerobic_ratio(power=first_half_power, hr=first_half_hr)
    second_half_ratio = _calculate_aerobic_ratio(power=second_half_power, hr=second_half_hr)
    if first_half_ratio is None or second_half_ratio is None:
        return None

    # Calculate the decoupling of the two
    coupling = ((first_half_ratio - second_half_ratio) / first_half_ratio) * 100

    # Done
    return AerobicDecoupling(coupling=coupling, first_half_ratio=first_half_ratio, second_half_ratio=second_half_ratio)


def calculate_fitness(*, activities: List[Activity]) -> Fitness:
    """
    Calculate fitness given a list of activities.

    Args:
        activities: The activities.

    Returns:
        Fitness: The fitness, including CTL, ATL, and TSB.
    """

    # Make sure we've got TSS for each activity
    for activity in activities:
        calculate_transient_values(activity)
    calculate_progressive_fitness(activities=activities)

    # Calculate CTL and ATL
    ctl = _calculate_training_load(activities=activities, days=42)
    atl = _calculate_training_load(activities=activities, days=7)

    # Done
    return Fitness(ctl=ctl, atl=atl, tsb=ctl - atl)


def calculate_normalised_power(*, power: List[int]) -> int:
    """
    Given a collection of power figures, calculate the normalised power.

    This algorithm comes from the book ‘Training and Racing with a Power Meter’,
    by Hunter and Allen via the blog post at
    https://medium.com/critical-powers/formulas-from-training-and-racing-with-a-power-meter-2a295c661b46.

    In essence, it's as follows:

    Step 1
        Calculate the rolling average with a window of 30 seconds:
        Start at 30 seconds, calculate the average power of the previous
        30 seconds and to the end for every second after that.

    Step 2
        Calculate the 4th power of the values from the previous step.

    Step 3
        Calculate the average of the values from the previous step.

    Step 4
        Take the fourth root of the average from the previous step.
        This is your normalized power.

    Args:
        power: The power figures for each second.

    Returns:
        int: The normalised power.
    """

    # Step 1: get our moving averages
    moving_averages = get_moving_average(source=power, window=30)
    if not moving_averages:
        return 0

    # Step 2: calculate the fourth power of each figure
    fourth_powers = [pow(x, 4) for x in moving_averages]

    # Step 3: Calculate the average of our fourth powers
    fourth_power_average = sum(fourth_powers) / len(fourth_powers)

    # Step 4: Take the fourth root of the average to yield normalised power
    normalised_power = pow(fourth_power_average, 0.25)

    # Done!
    return int(normalised_power)


def get_moving_average(*, source: List[int], window: int) -> List[int]:
    """
    Get a moving average from an iterable value.

    Note: Any zero values are ignored.

    Args:
        source: The data to iterate over.
        window: The moving average window, in seconds.

    Returns:
         The moving averages found in the data.
    """

    # Create a copy of the source data without any zeroes.
    fixed_source = [x for x in source if x != 0]

    # Create an iterable object from the preprocessed source data.
    it = iter(fixed_source)
    d = deque(itertools.islice(it, window - 1))

    # Create deque object by slicing iterable.
    d.appendleft(0)

    # Initialise.
    avg_list = []

    # Iterate over the source data, yielding the moving average.
    s = sum(d)
    for elem in it:
        s += elem - d.popleft()
        d.append(elem)
        avg_list.append(int(s / window))

    # Done.
    return avg_list


def _calculate_training_load(*, activities: List[Activity], days: int) -> int:
    """
    Given a list of activities, and a number of days, calculate the training load for the
    specified number of days.

    For example: given all activities in the database, and "42' as the number of days,
    this will calculate the classic CTL value.

    Args:
        activities: The activities to consider.
        days:       The number of days to include in the training load calculation.

    Returns:
        The training load.
    """

    # Determine the TSS on each day in our window
    tss_list = _calculate_daily_tss(activities=activities, days=days)

    # Skip the last day (that's today)
    del tss_list[-1]
    assert len(tss_list) == days

    # Average the tss
    return sum(tss_list) / len(tss_list)


def _calculate_daily_tss(*, activities: List[Activity], days: int) -> List[int]:
    """
    Sum the TSS for each day in the given number of days.

    Args:
        activities: The list of activities.
        days:       The number of days to include in the sum (counting back from today).

    Returns:
        A list of tss values. The length of this list will match the given number
        of days. The last value is today's TSS.
    """

    # Group activities by date
    date_grouping = itertools.groupby(activities, key=lambda x: x.start_time.date())

    # Initialise our list
    tss_list = []

    # Initialise dates
    start_date = (datetime.datetime.now() - datetime.timedelta(days=days)).date()
    current_date = start_date

    # Visit each date
    for date, activity_list in date_grouping:

        # Skip if too early
        if date < start_date:
            continue

        # If we're not exactly one day on from the previous day, we've got a gap, so we'll
        # have to add some padding
        day_count = date - current_date
        if day_count.days > 1:
            padding = day_count.days - 1
            while padding:
                tss_list.append(0)
                padding -= 1

        # Calculate the TSS for this date
        daily_tss = sum([activity.tss for activity in activity_list])

        # Add into the list
        tss_list.append(daily_tss)

        # Advance to the next day
        current_date = date

    # Zero pad if we've got missing days at the end
    while len(tss_list) < days:
        tss_list.append(0)

    # Done
    return tss_list


def _calculate_aerobic_ratio(*, power: List[int], hr: List[int]) -> Optional[float]:
    """
    Given a list of power and HR details, find the ratio between their averages.

    Args:
        power: The list of power values.
        hr: The list of HR values.

    Returns:
        The ratio between their averages.
    """

    # Calculate power and HR averages
    assert len(power) == len(hr)
    power_avg = calculate_normalised_power(power=power)
    hr_avg = sum(hr) / len(hr)

    # Determine ratio
    return power_avg / hr_avg if hr_avg else None
