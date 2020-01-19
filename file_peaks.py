import itertools
from collections import deque
from typing import List, Dict, Tuple
from datetime import datetime
from dateutil import tz

from fitparse import FitFile
from fitparse.utils import FitParseError

from peaks import Peaks

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


def get_file_peaks(*, path: str) -> Peaks:
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
    start_time, end_time, power, hr = _load_file_data(fitfile=fitfile)

    # Setup the peaks object
    peaks = Peaks()
    peaks.start_time = start_time
    peaks.end_time = end_time
    _load_peaks(source=power, attributes=POWER_AVERAGES, peaks=peaks)
    _load_peaks(source=hr, attributes=HR_AVERAGES, peaks=peaks)

    # Done.
    return peaks


def _load_peaks(source: List[int], attributes: Dict[int, str], peaks: Peaks):
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
        peaks:      The peaks object we're populating.
    """

    for window, attr_name in attributes.items():
        if (moving_average := _get_moving_average(source=source, window=window)) :
            peaks.__dict__[attr_name] = int(max(moving_average))
        else:
            peaks.__dict__[attr_name] = None


def _load_file_data(
    *, fitfile: FitFile
) -> Tuple[datetime, datetime, List[int], List[int]]:
    """
    Load the data from the nominated file.
    
    Args:
        fitfile: The file to load the data from.
    
    Returns:
        Tuple[datetime, datetime, List[int], List[int]]:
            The start time, end time, power figures, and HR figures.
    """

    # Initialise.
    start_time = None
    end_time = None
    power = []
    hr = []

    # Iterate over the file.
    for record in fitfile.get_messages("record"):

        # Go through all the data entries in this record.
        for record_data in record:

            # Start time?
            if start_time is None and record_data.name == "timestamp":
                start_time = record_data.value

            # End time?
            if record_data.name == "timestamp":
                end_time = record_data.value

            # Fetch power.
            if record_data.name == "power":
                power.append(int(record_data.value))

            # Fetch HR.
            if record_data.name == "heart_rate":
                hr.append(int(record_data.value))

    # Done.
    return start_time, end_time, power, hr


def _get_moving_average(*, source: List[int], window: int) -> List[int]:
    """
    Get a moving average from an iterable value.
    
    Args:
        source: The data to iterate over.
        window: The moving average window.
    
    Yields:
         The moving averages found in the data.
    """

    # Create an iterable object from the source data.
    it = iter(source)
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
