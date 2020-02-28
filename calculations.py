from activity import Activity
from collections import namedtuple
from typing import List, Optional
from calculation_data import AerobicDecoupling
from athlete import get_ftp


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
    activity.moving_seconds = len(activity.raw_power)
    activity.tss = int((activity.duration_in_seconds * activity.normalised_power * activity.intensity_factor) / (activity.ftp * 36)) if activity.ftp else 0

    distance_in_meters = activity.distance
    speed_in_ms = distance_in_meters / activity.moving_seconds
    activity.speed_in_kmhr = speed_in_ms * 3600 / 1000

    # Now calculate aerobic decoupling
    # See https://www.trainingpeaks.com/blog/aerobic-endurance-and-decoupling.
    if distance_in_meters >= 10000:
        activity.aerobic_decoupling = calculate_aerobic_decoupling(activity)


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
    power_avg = sum(power) / len(power)
    hr_avg = sum(hr) / len(hr)

    # Determine ratio
    return power_avg / hr_avg if hr_avg else None
