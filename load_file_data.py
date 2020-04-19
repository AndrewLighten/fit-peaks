import itertools
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from dateutil import tz
from dataclasses import dataclass

from fitparse import FitFile
from fitparse.utils import FitParseError
from calculations import calculate_normalised_power, get_moving_average
from activity import Activity


@dataclass
class LoadedData:
    """
    This class represents the data we loaded from Zwift.
    """

    start_time: datetime  # The event start time
    end_time: datetime  # The event end time
    power: List[int]  # The list of power values
    hr: List[int]  # The list of HR values
    distance: float  # The total distance travelled
    moving_time: int  # The number of moving seconds


# This dictionary describes the time periods (in seconds) that we break power
# averages into, along with the Peaks attribute that the data is stored in.
POWER_AVERAGES = {
    5: "peak_5sec_power",
    30: "peak_30sec_power",
    60: "peak_60sec_power",
    300: "peak_5min_power",
    600: "peak_10min_power",
    1200: "peak_20min_power",
    1800: "peak_30min_power",
    3600: "peak_60min_power",
    5400: "peak_90min_power",
    7200: "peak_120min_power",
}

# This dictionary describes the time periods (in seconds) that we break HR
# averages into, along with the Peaks attribute that the data is stored in.
HR_AVERAGES = {
    5: "peak_5sec_hr",
    30: "peak_30sec_hr",
    60: "peak_60sec_hr",
    300: "peak_5min_hr",
    600: "peak_10min_hr",
    1200: "peak_20min_hr",
    1800: "peak_30min_hr",
    3600: "peak_60min_hr",
    5400: "peak_90min_hr",
    7200: "peak_120min_hr",
}


def load_file_data(*, path: str) -> Activity:
    """
    Get the peak data from the nominated file.
    
    Args:
        path: The file to load.
    
    Returns:
        The peak data we loaded from the file.
    """

    # Open the file.
    fitfile = FitFile(path)

    # Load the power and heart rate data.
    loaded_data = _load_file_data(fitfile=fitfile)

    # Setup the activity object
    activity = Activity()
    activity.start_time = loaded_data.start_time
    activity.end_time = loaded_data.end_time
    activity.moving_time = loaded_data.moving_time
    activity.activity_name = None
    activity.elevation = None
    activity.distance = loaded_data.distance
    activity.avg_power = int(sum(loaded_data.power) / loaded_data.moving_time)
    activity.max_power = max(loaded_data.power)
    activity.normalised_power = calculate_normalised_power(power=loaded_data.power)
    activity.avg_hr = int(sum(loaded_data.hr) / loaded_data.moving_time)
    activity.max_hr = max(loaded_data.hr)
    activity.raw_power = loaded_data.power
    activity.raw_hr = loaded_data.hr
    _load_peaks(source=loaded_data.power, attributes=POWER_AVERAGES, activity=activity)
    _load_peaks(source=loaded_data.hr, attributes=HR_AVERAGES, activity=activity)

    # Done.
    return activity


def _load_peaks(source: List[int], attributes: Dict[int, str], activity: Activity):
    """
    Load a set of peak data from the nominated source data.
    
    The source data we're given is either the time-series collection of power figures,
    or the time-series collection of HR figures.

    The attributes we're provided tells us what time periods we need to average that
    over. For example: given power data, and an attribute of (5, "peak_5sec_power")
    means that we need to take a moving 5 second average of the source data, find the
    maximum of those 5 second averages, and store that in the "peak_5sec_power" property
    of the Peaks object.

    Args:
        source:     The source data to load from.
        attributes: The attributes we load.
        activity:   The activity object we're populating.
    """

    for window, attr_name in attributes.items():
        if (moving_average := get_moving_average(source=source, window=window)) :
            activity.__dict__[attr_name] = int(max(moving_average))
        else:
            activity.__dict__[attr_name] = None


def _load_file_data(*, fitfile: FitFile) -> LoadedData:
    """
    Load the data from the nominated file.
    
    Args:
        fitfile: The file to load the data from.
    
    Returns:
        The data we loaded.
    """

    # Initialise.
    start_time = None
    end_time = None
    power = []
    hr = []
    distance = 0.0
    moving_time = 0

    # Iterate over the file.
    for record in fitfile.get_messages("record"):

        # Bump the moving time
        moving_time += 1

        # Go through all the data entries in this record.
        for record_data in record:

            # Start time?
            if start_time is None and record_data.name == "timestamp":
                start_time = record_data.value

            # End time? We need to deal carefully with this, because if we've
            # got missing data (the next value isn't exactly one second later
            # than the current value) we have to fill power and HR with
            # zeroes.
            if record_data.name == "timestamp":

                # Check that this data is one second later; if not, extrapolate
                if end_time is not None and end_time + timedelta(seconds=1) < record_data.value:
                    seconds_to_add = (record_data.value - end_time).seconds - 1
                    zeroes = [0] * seconds_to_add
                    power.extend(zeroes)
                    hr.extend(zeroes)

                # Capture the end time
                end_time = record_data.value

            # Fetch power.
            if record_data.name == "power":
                power.append(int(record_data.value))

            # Fetch HR.
            if record_data.name == "heart_rate":
                hr.append(int(record_data.value))

            # Fetch distance.
            if record_data.name == "distance" and record_data.value:
                distance = float(record_data.value)

    # Done.
    return LoadedData(start_time=start_time, end_time=end_time, power=power, hr=hr, distance=distance, moving_time=moving_time)
