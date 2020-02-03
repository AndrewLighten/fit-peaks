import os
import configparser
from typing import Tuple
from pathlib import Path
from datetime import datetime, timedelta
from dateutil import parser
import traceback
import sys

import fitparse.utils
from persistence import Persistence
from peaks import Peaks
from file_peaks import get_file_peaks
from zwift import Client

CONFIG_FILE = str(Path.home()) + "/.fit-peaks.rc"

SOURCE_DIR = str(Path.home()) + "/Documents/Zwift/Activities"


def load_from_zwift():
    """
    Load the latest data from Zwift.
    """
    _load_activity_files()
    _load_extra_zwift_data()


def _load_activity_files():
    """
    Load the Zwift activity files.
    """

    # Initialise.
    db = Persistence()
    loaded = 0

    # Fetch the file list
    filenames = os.listdir(SOURCE_DIR)
    filenames.sort()

    # Visit each file in the Zwift activity directory.
    for filename in filenames:

        # Ignore the in progress file.
        if filename == "inProgressActivity.fit":
            continue

        # See if we've already got this file.
        if db.load(filename=filename):
            continue

        # Some files are busted -- they contain data that the fitparse library
        # can't handle.
        try:

            # Load the file, then persist our peak data.
            new_peaks = get_file_peaks(path=SOURCE_DIR + "/" + filename)
            db.store(filename=filename, peaks=new_peaks)
            print(f"Loaded {filename}...")
            loaded += 1

        # This is a busted file.
        except fitparse.utils.FitParseError:
            # print(traceback.format_exc())
            pass

    # Done.
    print(f"Loaded {loaded} file(s)")


def _load_extra_zwift_data():
    """
    Load extra data from Zwift using its API.
    """

    # Fetch the Zwift credentials
    username, password, player_id = _load_zwift_credentials()
    if not username:
        return

    # Create the client
    client = Client(username, password)

    # Fetch a database connection
    db = Persistence()

    # Initialise Zwift markers
    start = 0
    limit = 50

    # Loop through the Zwift activities
    activity_client = client.get_activity(player_id)
    print("Loading activity names from Zwift...")
    while True:

        # Fetch the activity list
        activities = activity_client.list(start=start, limit=limit)
        if not activities:
            break

        # Visit each activity
        for activity in activities:

            # Discard blank entries
            if not int(activity["distanceInMeters"]):
                continue

            # Fetch the start date, end date, and activity name
            start_time = parser.parse(activity["startDate"]) - timedelta(minutes=5)
            end_time = parser.parse(activity["endDate"])

            # Fetch the activity name
            activity_name = activity["name"]
            if activity_name.startswith("Zwift - "):
                activity_name = activity_name[8:]

            # Fetch the elevation
            elevation = int(activity["totalElevation"])

            # Store the activity name
            db.update_with_zwift_data(
                start_time=start_time,
                end_time=end_time,
                elevation=elevation,
                activity_name=activity_name,
            )

        # Move on
        start += limit


def _load_zwift_credentials() -> Tuple[str, str, str]:
    """
    Load our Zwift credentials.
    
    Returns:
        A tuple containing the Zwift username, password, and player ID.
    """

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    try:
        username = config["zwift"]["username"]
        password = config["zwift"]["password"]
        player_id = config["zwift"]["player-id"]
        return username, password, player_id

    except KeyError:
        print("Create config file properly! See README.md for details.")
        return None, None, None
