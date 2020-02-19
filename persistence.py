import sqlite3
import os.path
from enum import Enum, auto
from pathlib import Path
from datetime import datetime
from dateutil import tz
from typing import Optional, List, Tuple

from activity import Activity

DATABASE_NAME = str(Path.home()) + "/.fitpeaks-activity.dat"

CREATE_TABLE = """
            create table activity
            (
                filename            varchar         primary key,
                
                start_time          timestamp,
                end_time            timestamp,
                
                distance            real,
                elevation           int             null,
                activity_name       varchar         null,

                avg_power           int,
                max_power           int,
                normalised_power    int,

                avg_hr              int,
                max_hr              int,

                raw_power           text,
                raw_hr              text,

                peak_5sec_power     int             null,
                peak_30sec_power    int             null,
                peak_60sec_power    int             null,
                peak_5min_power     int             null,
                peak_10min_power    int             null,
                peak_20min_power    int             null,
                peak_30min_power    int             null,
                peak_60min_power    int             null,
                peak_90min_power    int             null,
                peak_120min_power   int             null,
                
                peak_5sec_hr        int             null,
                peak_30sec_hr       int             null,
                peak_60sec_hr       int             null,
                peak_5min_hr        int             null,
                peak_10min_hr       int             null,
                peak_20min_hr       int             null,
                peak_30min_hr       int             null,
                peak_60min_hr       int             null,
                peak_90min_hr       int             null,
                peak_120min_hr      int             null
            )
            """

SELECT = """
    select rowid,
        filename, start_time, end_time, distance, elevation, activity_name,
        avg_power, max_power, normalised_power, avg_hr, max_hr, raw_power, raw_hr,
        peak_5sec_power,  peak_30sec_power, peak_60sec_power, peak_5min_power,  peak_10min_power,
        peak_20min_power, peak_30min_power, peak_60min_power, peak_90min_power, peak_120min_power, 
        peak_5sec_hr,     peak_30sec_hr,    peak_60sec_hr,    peak_5min_hr,     peak_10min_hr,
        peak_20min_hr,    peak_30min_hr,    peak_60min_hr,    peak_90min_hr,    peak_120min_hr
    from activity
"""

SELECT_FILE = SELECT + " where filename = :filename"

SELECT_ACTIVITY = SELECT + " where rowid = :rowid"


class SelectIndices(Enum):
    RowId = 0
    Filename = auto()
    StartTime = auto()
    EndTime = auto()
    Distance = auto()
    Elevation = auto()
    ActivityName = auto()
    AvgPower = auto()
    MaxPower = auto()
    NormalisedPower = auto()
    AvgHr = auto()
    MaxHr = auto()
    RawPower = auto()
    RawHr = auto()
    Peak5SecPower = auto()
    Peak30SecPower = auto()
    Peak60SecPower = auto()
    Peak5MinPower = auto()
    Peak10MinPower = auto()
    Peak20MinPower = auto()
    Peak30MinPower = auto()
    Peak60MinPower = auto()
    Peak90MinPower = auto()
    Peak120MinPower = auto()
    Peak5SecHr = auto()
    Peak30SecHr = auto()
    Peak60SecHr = auto()
    Peak5MinHr = auto()
    Peak10MinHr = auto()
    Peak20MinHr = auto()
    Peak30MinHr = auto()
    Peak60MinHr = auto()
    Peak90MinHr = auto()
    Peak120MinHr = auto()


SELECT_ALL = SELECT + " where peak_5min_power is not null order by start_time"

INSERT_SQL = """
    insert into activity 
    (
        filename, start_time, end_time, distance, elevation, activity_name,
        avg_power, max_power, normalised_power, avg_hr, max_hr, raw_power, raw_hr,
        peak_5sec_power,  peak_30sec_power, peak_60sec_power, peak_5min_power,  peak_10min_power,
        peak_20min_power, peak_30min_power, peak_60min_power, peak_90min_power, peak_120min_power, 
        peak_5sec_hr,     peak_30sec_hr,    peak_60sec_hr,    peak_5min_hr,     peak_10min_hr,
        peak_20min_hr,    peak_30min_hr,    peak_60min_hr,    peak_90min_hr,    peak_120min_hr
    )
    values 
    (
        :filename, :start_time, :end_time, :distance, :elevation, :activity_name,
        :avg_power, :max_power, :normalised_power, :avg_hr, :max_hr, :raw_power, :raw_hr,
        :peak_5sec_power,  :peak_30sec_power, :peak_60sec_power, :peak_5min_power,  :peak_10min_power,
        :peak_20min_power, :peak_30min_power, :peak_60min_power, :peak_90min_power, :peak_120min_power, 
        :peak_5sec_hr,     :peak_30sec_hr,    :peak_60sec_hr,    :peak_5min_hr,     :peak_10min_hr,
        :peak_20min_hr,    :peak_30min_hr,    :peak_60min_hr,    :peak_90min_hr,    :peak_120min_hr

    )
    on conflict(filename) do update
    set start_time          = :start_time,
        end_time            = :end_time,
        distance            = :distance,
        elevation           = :elevation,
        activity_name       = :activity_name,
        avg_power           = :avg_power,
        max_power           = :max_power,
        normalised_power    = :normalised_power,
        avg_hr              = :avg_hr,
        max_hr              = :max_hr,
        raw_power           = :raw_power,
        raw_hr              = :raw_hr,
        peak_5sec_power     = :peak_5sec_power,  
        peak_30sec_power    = :peak_30sec_power,
        peak_60sec_power    = :peak_60sec_power,
        peak_5min_power     = :peak_5min_power,  
        peak_10min_power    = :peak_10min_power,
        peak_20min_power    = :peak_20min_power, 
        peak_30min_power    = :peak_30min_power, 
        peak_60min_power    = :peak_60min_power, 
        peak_90min_power    = :peak_90min_power, 
        peak_120min_power   = :peak_120min_power, 
        peak_5sec_hr        = :peak_5sec_hr,     
        peak_30sec_hr       = :peak_30sec_hr,    
        peak_60sec_hr       = :peak_60sec_hr,    
        peak_5min_hr        = :peak_5min_hr,     
        peak_10min_hr       = :peak_10min_hr,
        peak_20min_hr       = :peak_20min_hr,    
        peak_30min_hr       = :peak_30min_hr,    
        peak_60min_hr       = :peak_60min_hr,    
        peak_90min_hr       = :peak_90min_hr,    
        peak_120min_hr      = :peak_120min_hr
"""

UPDATE_ZWIFT_SQL = "update activity set activity_name = :activity_name, elevation = :elevation where :start_time <= start_time and :end_time > start_time"


class Persistence:
    """
    This class is used to persist our peaks data in an SQLite database.
    """

    def __init__(self):
        """
        Initialise ourself.
        """

        # Is this a new database?
        new_database = not os.path.exists(DATABASE_NAME)

        # Connect to the database.
        self.conn = sqlite3.connect(DATABASE_NAME)

        # If it's new, create our tables.
        if new_database:
            self.conn.execute(CREATE_TABLE)

    def load(self, *, filename: str) -> Optional[Activity]:
        """
        Load a given filename's activity data.
        
        Args:
            filename: The file whose activity data should be loaded.
        
        Returns:
            The activity data for this file, if found.
        """

        cursor = self.conn.cursor()
        try:
            cursor.execute(SELECT_FILE, {"filename": filename})
            record = cursor.fetchone()
            return self._create_activity(record=record) if record else None
        finally:
            cursor.close()

    def load_by_id(self, id: int) -> Optional[Activity]:
        """
        Load a given activity's data.
        
        Args:
            id: The ID of the activity whose data should be loaded.
        
        Returns:
            The activity, if found.
        """

        cursor = self.conn.cursor()
        try:
            cursor.execute(SELECT_ACTIVITY, {"rowid": id})
            record = cursor.fetchone()
            return self._create_activity(record=record) if record else None
        finally:
            cursor.close()

    def load_all(self) -> List[Activity]:
        """
        Load all activity data we have.
        
        Returns:
            The list of activities.
        """

        cursor = self.conn.cursor()
        try:
            cursor.execute(SELECT_ALL)
            records = cursor.fetchall()
            activities = []
            for record in records:
                activities.append(self._create_activity(record=record))
            return activities
        finally:
            cursor.close()

    def _create_activity(self, *, record: Tuple) -> Activity:
        """
        Create an Activities object given a database record.
        
        Args:
            record: The data we've retrieved from SQLite.
        
        Returns:
            The activity data object.
        """

        # Create the new activity object.
        activity = Activity()

        # Fetch the row ID
        activity.rowid = record[SelectIndices.RowId.value]

        # Setup timezones.
        src_tz = tz.tzutc()
        dst_tz = tz.tzlocal()

        # Fetch the start time. We see two formats here:
        #   yyyy-mm-dd hh:mm:ss         — UTC
        #   yyyy-mm-dd hh:mm:ss+hh:mm   - Local time
        # UTC times we correct to local times; local times we use verbatim.
        raw_start_time = record[SelectIndices.StartTime.value]
        if "+" in raw_start_time:
            time_parts = raw_start_time.split("+")
            activity.start_time = datetime.strptime(time_parts[0], "%Y-%m-%d %H:%M:%S")
        else:
            activity.start_time = datetime.strptime(raw_start_time, "%Y-%m-%d %H:%M:%S")
            utc = activity.start_time.replace(tzinfo=src_tz)
            activity.start_time = utc.astimezone(dst_tz)

        # Fetch the end time. Same deal as the start time with TZ data...
        raw_end_time = record[SelectIndices.EndTime.value]
        if "+" in raw_end_time:
            time_parts = raw_end_time.split("+")
            activity.end_time = datetime.strptime(time_parts[0], "%Y-%m-%d %H:%M:%S")
        else:
            activity.end_time = datetime.strptime(raw_end_time, "%Y-%m-%d %H:%M:%S")
            utc = activity.end_time.replace(tzinfo=src_tz)
            activity.end_time = utc.astimezone(dst_tz)

        # Fetch activity name and distance
        activity.distance = record[SelectIndices.Distance.value]
        activity.elevation = record[SelectIndices.Elevation.value]
        activity.activity_name = record[SelectIndices.ActivityName.value]

        # Fetch overall power and HR data
        activity.avg_power = record[SelectIndices.AvgPower.value]
        activity.max_power = record[SelectIndices.MaxPower.value]
        activity.normalised_power = record[SelectIndices.NormalisedPower.value]
        activity.avg_hr = record[SelectIndices.AvgHr.value]
        activity.max_hr = record[SelectIndices.MaxHr.value]

        # Fetch raw power and HR
        activity.raw_power = [int(p) for p in record[SelectIndices.RawPower.value].split(",")]
        activity.raw_hr = [int(hr) for hr in record[SelectIndices.RawHr.value].split(",")]

        # Fetch power peaks
        activity.peak_5sec_power = record[SelectIndices.Peak5SecPower.value]
        activity.peak_30sec_power = record[SelectIndices.Peak30SecPower.value]
        activity.peak_60sec_power = record[SelectIndices.Peak60SecPower.value]
        activity.peak_5min_power = record[SelectIndices.Peak5MinPower.value]
        activity.peak_10min_power = record[SelectIndices.Peak10MinPower.value]
        activity.peak_20min_power = record[SelectIndices.Peak20MinPower.value]
        activity.peak_30min_power = record[SelectIndices.Peak30MinPower.value]
        activity.peak_60min_power = record[SelectIndices.Peak60MinPower.value]
        activity.peak_90min_power = record[SelectIndices.Peak90MinPower.value]
        activity.peak_120min_power = record[SelectIndices.Peak120MinPower.value]

        # Fetch HR peaks
        activity.peak_5sec_hr = record[SelectIndices.Peak5SecHr.value]
        activity.peak_30sec_hr = record[SelectIndices.Peak30SecHr.value]
        activity.peak_60sec_hr = record[SelectIndices.Peak60SecHr.value]
        activity.peak_5min_hr = record[SelectIndices.Peak5MinHr.value]
        activity.peak_10min_hr = record[SelectIndices.Peak10MinHr.value]
        activity.peak_20min_hr = record[SelectIndices.Peak20MinHr.value]
        activity.peak_30min_hr = record[SelectIndices.Peak30MinHr.value]
        activity.peak_60min_hr = record[SelectIndices.Peak60MinHr.value]
        activity.peak_90min_hr = record[SelectIndices.Peak90MinHr.value]
        activity.peak_120min_hr = record[SelectIndices.Peak120MinHr.value]

        # Done.
        return activity

    def store(self, *, filename: str, activity: Activity):
        """
        Persist an activity in the SQLite database.
        
        Args:
            filename: The name of the file we got this activity data from.
            activity: The activity to persist.
        """

        # Setup parameters for insert.
        params = {
            "filename": filename,
        }
        for key, value in activity.__dict__.items():
            if key in ["raw_power", "raw_hr"]:
                params[key] = ",".join(str(x) for x in value)
            else:
                params[key] = value

        # Insert the record.
        self.conn.execute(INSERT_SQL, params)
        self.conn.commit()

    def update_with_zwift_data(
        self, *, start_time: datetime, end_time: datetime, elevation: int, activity_name: str,
    ):
        """
        Update an activity with additional data we got from Zwift.
        
        Args:
            start_time:    The activity start time.
            end_time:      The activity end time.
            elevation:     The activity elevation gain.
            activity_name: The activity name.
        """

        self.conn.execute(
            UPDATE_ZWIFT_SQL,
            {"start_time": start_time, "end_time": end_time, "elevation": elevation, "activity_name": activity_name,},
        )
        self.conn.commit()
