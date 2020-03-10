import os
import configparser
from typing import Tuple, List, Optional, Any
from pathlib import Path
from datetime import datetime, timedelta
from dateutil import parser
from collections import namedtuple
import traceback
import sys
import requests

import fitparse.utils
from persistence import Persistence
from activity import Activity
from load_file_data import load_file_data
from zwift import Client

CONFIG_FILE = str(Path.home()) + "/.fit-peaks.rc"

TEMP_FILE = "./xyzzy.fit"

def load_from_zwift():
    """
    Load the latest data from Zwift.
    """
    _load_zwift_data()


def _load_zwift_data():
    """
    Fetch any new data Zwift has for us.
    """

    # Initialise
    db = Persistence()
    loaded = 0

    # Get the list of activities we already have
    known_activities = db.get_known_ids()

    # Get the list of activities to load
    new_activities = _find_new_activities(known_activities)
    print(f"Found {len(new_activities)} to load")

    # Load each new activity
    for activity in new_activities:

        # Fetch the FIT file
        zwift_id = activity["id_str"]
        s3_url = "https://" + activity["fitFileBucket"] + ".s3.amazonaws.com/" + activity["fitFileKey"]
        if not (activity_record := _load_fit_file_content(s3_url)):
            print(f"Failed to load FIT file for {zwift_id=} ({s3_url=})")
            continue

        # Add in extra details
        activity_record.zwift_id = zwift_id
        activity_record.s3_url =s3_url
        activity_name = activity["name"]
        if activity_name.startswith("Zwift - "):
            activity_name = activity_name[8:]
        activity_record.activity_name = activity_name

        # Fetch the elevation
        activity_record.elevation = int(activity["totalElevation"])

        # Store this record
        db.store(activity=activity_record)
        print(f"Loaded activity \"{activity_record.activity_name}\" ({activity_record.start_time})")
        loaded += 1
            
    # Done.
    if not loaded:
        print(f"No new activities found")
    else:
        plural = "activity" if loaded == 1 else "activities"
        print(f"Loaded {loaded} {plural}")


def _find_new_activities(known_ids: set) -> List[Any]:
    """
    Fetch the list of new activities to load.

    Note: We have to load activities in oldest-first, otherwise the activity ID
          list is screwed up. If we find two new activites, for example, the newest
          one will have a lower rowid than the older one. We want to loade the
          older one first.
    
    Args:
        known_ids: The list of IDs we already know about.
    
    Returns:
        The list of activities to load, in the order they should be loaded.
    """

    # Fetch the Zwift credentials
    username, password, player_id = _load_zwift_credentials()
    if not username:
        return

    # Create the client
    client = Client(username, password)
    activity_client = client.get_activity(player_id)

    # Initialise to fetch new activities
    start = 0
    limit = 5
    keep_searching = True

    # The new activity list
    new_activity_list = []

    # Loop until we've found all new activities
    while keep_searching:

        # Fetch the activity list
        activities = activity_client.list(start=start, limit=limit)
        if not activities:
            break

        # Visit each activity
        for activity in activities:

            # If we've seen this activity, we're digging into old data
            zwift_id = activity["id_str"]
            if zwift_id in known_ids:
                keep_searching = False
                break

            # Discard blank entries
            if not int(activity["distanceInMeters"]):
                continue
            
            # Add into the list
            new_activity_list.append(activity)
            
        # Move on
        start += limit

    # Done -- return the list in reverse order, so older activities load first
    return new_activity_list[::-1]



def _load_fit_file_content(s3_url: str) -> Optional[Activity]:
    """
    Load the content of a FIT file into an activity.
    
    Args:
        s3_url: The S3 URL to load from.
    
    Returns:
        The activity, if it loaded ok.
    """

    # Setup a request       
    r = requests.get(s3_url)
    if not (r.status_code == 200):
        print(f"Failed to load from S3: {r.status_code=}")
        return None

    # Store the content in our temporary file
    with open(TEMP_FILE, "wb") as fit_file:
        fit_file.write(r.content)

    # Now load the file
    if not (new_activity := load_file_data(path=TEMP_FILE)):
        print(f"Failed to load temporary FIT file")
        return None

    # Delete the temporary file
    os.remove(TEMP_FILE)

    # Done
    return new_activity


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
