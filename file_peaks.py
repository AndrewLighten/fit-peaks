import itertools
from collections import deque
from typing import List, Dict
from datetime import datetime

from fitparse import FitFile
from peaks import Peaks

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


def get_file_peaks(*, path) -> Peaks:

    # Open the file
    fitfile = FitFile(path)

    # Load the power and heart rate data
    start_time, end_time, power, hr = _load_file_data(fitfile=fitfile)

    # Setup the peaks object
    peaks = Peaks()
    peaks.start_time = start_time
    peaks.end_time = end_time
    _load_peaks(source=power, attributes=POWER_AVERAGES, peaks=peaks)
    _load_peaks(source=hr, attributes=HR_AVERAGES, peaks=peaks)

    # Done
    return peaks

def _load_peaks(source: List[int], attributes: Dict[int,str], peaks: Peaks):
    
    for window, attr_name in attributes.items():
        if (moving_average := _get_moving_average(source=source, window=window)):
            peaks.__dict__[attr_name] = int(max(moving_average))
        else:
            peaks.__dict__[attr_name] = None

def _load_file_data(*, fitfile: FitFile) -> (datetime, datetime, List[int], List[int]):

    # Initialise
    start_time = None
    end_time = None
    power = []
    hr = []

    # Iterate over the file
    for record in fitfile.get_messages("record"):

        # Go through all the data entries in this record
        for record_data in record:

            # Start time
            if start_time is None and record_data.name == "timestamp":
                start_time = record_data.value

            # End time
            if record_data.name == "timestamp":
                end_time = record_data.value

            # Fetch power
            if record_data.name == "power":
                power.append(int(record_data.value))

            # Fetch HR
            if record_data.name == "heart_rate":
                hr.append(int(record_data.value))

    # Done
    return start_time, end_time, power, hr


def _get_moving_average(*, source: List[int], window: int) -> List[int]:
    """
    Get a moving average from an iterable value.
    
    Args:
        source: The data to iterate over.
        window:        The moving average window.
    
    Yields:
         The moving averages found in the data.
    """

    # create an iterable object from input argument
    it = iter(source)
    d = deque(itertools.islice(it, window - 1))

    # create deque object by slicing iterable
    d.appendleft(0)

    # Averages
    avg_list = []

    # iterate over the source data, yielding the moving average
    s = sum(d)
    for elem in it:
        s += elem - d.popleft()
        d.append(elem)
        avg_list.append(s / window)

    # Done
    return avg_list
