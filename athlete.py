from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional, Tuple
from pathlib import Path
import json

ATHLETE_FILE = str(Path.home()) + "/.athlete.json"


@dataclass
class AthleteData:
    """
    This class represents an FTP we've loaded from the FTP file.
    """

    start_date: datetime
    ftp: int
    rest_heart_rate: int
    threshold_heart_rate: int
    max_heart_rate: int


ATHLETE_DATA_LIST: List[AthleteData] = []


@dataclass
class HeartRateData:

    rest_heart_rate: int
    threshold_heart_rate: int
    max_heart_rate: int


def get_ftp(when: datetime) -> Optional[int]:
    """
    Get the FTP value that is in effect for a particular date.

    Args:
        when: The date we want an FTP value for.

    Returns:
        Optional[int]: The FTP in effect for that date, if any.
    """

    athlete_data = _get_applicable_entry(when)
    return athlete_data.ftp if athlete_data else None


def get_hr(when: datetime) -> Optional[HeartRateData]:
    """
    Get the athlete's resting and maximum heart rate that is in effect for
    a particular date.

    Args:
        when: The date we want heart rate data for.

    Returns:
        The athlete's heart rate data.
    """

    if not (athlete_data := _get_applicable_entry(when)):
        return None

    return HeartRateData(
        rest_heart_rate=athlete_data.rest_heart_rate,
        threshold_heart_rate=athlete_data.threshold_heart_rate,
        max_heart_rate=athlete_data.max_heart_rate,
    )


def _get_applicable_entry(when: datetime) -> Optional[AthleteData]:
    """
    Get the athlete data entry that's applicable for a certain date.

    Args:
        when: The data whose entry we want.

    Returns:
        Optional[AthleteData]: The athlete data, if found.
    """

    # Make sure we've got athlete data
    _get_athlete_data()

    # Burn any timezone we've got
    when = when.replace(tzinfo=None)

    # Find the athlete data entry with the latest date equal to or before
    # the provided date
    selected_entry: AthleteData = None
    for data in ATHLETE_DATA_LIST:
        if data.start_date.date() < when.date():
            selected_entry = data

    # Done
    return selected_entry


def _get_athlete_data():
    """
    Make sure the athlete data is loaded.
    """

    global ATHLETE_DATA_LIST
    if not ATHLETE_DATA_LIST:
        if not (ATHLETE_DATA_LIST := _get_all_athlete_data()):
            print("Cannot load athlete data (ftp, HR, etc). Cannot proceed.")
            exit(1)


def _get_all_athlete_data() -> Optional[List[AthleteData]]:
    """
    Fetch the list of all athlete data values.

    Returns:
        Optional[List[AthleteData]]: The loaded athlete data.
    """

    # Be ready for problems
    try:

        # Load the JSON array of athlete data
        with open(ATHLETE_FILE) as json_file:
            athlete_values = json.load(json_file)
            return [
                AthleteData(
                    start_date=datetime.strptime(raw_data["date"], "%d-%b-%Y"),
                    ftp=raw_data["ftp"],
                    rest_heart_rate=raw_data["rhr"],
                    threshold_heart_rate=raw_data["thr"],
                    max_heart_rate=raw_data["mhr"],
                )
                for raw_data in athlete_values
            ]

    # No athlete data available
    except FileNotFoundError:
        return None
