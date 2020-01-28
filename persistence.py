import sqlite3
import os.path
from datetime import datetime
from dateutil import tz
from typing import Optional, List

from peaks import Peaks

DATABASE_NAME = "peaks.dat"

CREATE_TABLE = """
            create table peaks
            (
                filename            varchar         primary key,
                start_time          timestamp,
                end_time            timestamp,
                activity_name       varchar         null,
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
    select
        filename, start_time, end_time, activity_name,
        peak_5sec_power,  peak_30sec_power, peak_60sec_power, peak_5min_power,  peak_10min_power,
        peak_20min_power, peak_30min_power, peak_60min_power, peak_90min_power, peak_120min_power, 
        peak_5sec_hr,     peak_30sec_hr,    peak_60sec_hr,    peak_5min_hr,     peak_10min_hr,
        peak_20min_hr,    peak_30min_hr,    peak_60min_hr,    peak_90min_hr,    peak_120min_hr
    from peaks
"""

SELECT_FILE = SELECT + " where filename = :filename"

SELECT_ALL = SELECT + " where peak_10min_power is not null order by start_time"

INSERT_SQL = """
    insert into peaks 
    (
        filename, start_time, end_time, activity_name,
        peak_5sec_power,  peak_30sec_power, peak_60sec_power, peak_5min_power,  peak_10min_power,
        peak_20min_power, peak_30min_power, peak_60min_power, peak_90min_power, peak_120min_power, 
        peak_5sec_hr,     peak_30sec_hr,    peak_60sec_hr,    peak_5min_hr,     peak_10min_hr,
        peak_20min_hr,    peak_30min_hr,    peak_60min_hr,    peak_90min_hr,    peak_120min_hr
    )
    values 
    (
        :filename, :start_time, :end_time, :activity_name,
        :peak_5sec_power,  :peak_30sec_power, :peak_60sec_power, :peak_5min_power,  :peak_10min_power,
        :peak_20min_power, :peak_30min_power, :peak_60min_power, :peak_90min_power, :peak_120min_power, 
        :peak_5sec_hr,     :peak_30sec_hr,    :peak_60sec_hr,    :peak_5min_hr,     :peak_10min_hr,
        :peak_20min_hr,    :peak_30min_hr,    :peak_60min_hr,    :peak_90min_hr,    :peak_120min_hr

    )
    on conflict(filename) do update
    set start_time          = :start_time,
        end_time            = :end_time,
        activity_name       = :activity_name,
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

UPDATE_NAME_SQL = "update peaks set activity_name = :activity_name where :start_time <= start_time and :end_time > start_time"


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

    def load(self, *, filename: str) -> Optional[Peaks]:
        """
        Load a given filename's peak data.
        
        Args:
            filename: The file whose peak data should be loaded.
        
        Returns:
            The peaks for this file, if found.
        """

        cursor = self.conn.cursor()
        try:
            cursor.execute(SELECT_FILE, {"filename": filename})
            record = cursor.fetchone()
            return self._create_peaks(record=record) if record else None
        finally:
            cursor.close()

    def load_all(self) -> List[Peaks]:
        """
        Load all peak data we have.
        
        Returns:
            The list of peak objects.
        """

        cursor = self.conn.cursor()
        try:
            cursor.execute(SELECT_ALL)
            records = cursor.fetchall()
            peaks = []
            for record in records:
                peaks.append(self._create_peaks(record=record))
            return peaks
        finally:
            cursor.close()

    def _create_peaks(self, *, record: tuple) -> Peaks:
        """
        Create a `Peaks` object given a database record.
        
        Args:
            record: The data we've retrieved from SQLite.
        
        Returns:
            The Peaks object.
        """

        # Create the new peaks object.
        peaks = Peaks()

        # Setup timezones.
        src_tz = tz.tzutc()
        dst_tz = tz.tzlocal()

        # Fetch the start time. We see two formats here:
        #   yyyy-mm-dd hh:mm:ss         — UTC
        #   yyyy-mm-dd hh:mm:ss+hh:mm   - Local time
        # UTC times we correct to local times; local times we use verbatim.
        raw_start_time = record[1]
        if "+" in raw_start_time:
            time_parts = raw_start_time.split("+")
            peaks.start_time = datetime.strptime(time_parts[0], "%Y-%m-%d %H:%M:%S")
        else:
            peaks.start_time = datetime.strptime(raw_start_time, "%Y-%m-%d %H:%M:%S")
            utc = peaks.start_time.replace(tzinfo=src_tz)
            peaks.start_time = utc.astimezone(dst_tz)

        # Fetch the end time. Same deal as the start time with TZ data...
        raw_end_time = record[2]
        if "+" in raw_end_time:
            time_parts = raw_end_time.split("+")
            peaks.end_time = datetime.strptime(time_parts[0], "%Y-%m-%d %H:%M:%S")
        else:
            peaks.end_time = datetime.strptime(raw_end_time, "%Y-%m-%d %H:%M:%S")
            utc = peaks.end_time.replace(tzinfo=src_tz)
            peaks.end_time = utc.astimezone(dst_tz)

        # Fetch activity name.
        peaks.activity_name = record[3]

        # Fetch power data.
        peaks.peak_5sec_power = record[4]
        peaks.peak_30sec_power = record[5]
        peaks.peak_60sec_power = record[6]
        peaks.peak_5min_power = record[7]
        peaks.peak_10min_power = record[8]
        peaks.peak_20min_power = record[9]
        peaks.peak_30min_power = record[10]
        peaks.peak_60min_power = record[11]
        peaks.peak_90min_power = record[12]
        peaks.peak_120min_power = record[13]

        # Fetch HR data.
        peaks.peak_5sec_hr = record[14]
        peaks.peak_30sec_hr = record[15]
        peaks.peak_60sec_hr = record[16]
        peaks.peak_5min_hr = record[17]
        peaks.peak_10min_hr = record[18]
        peaks.peak_20min_hr = record[19]
        peaks.peak_30min_hr = record[20]
        peaks.peak_60min_hr = record[21]
        peaks.peak_90min_hr = record[22]
        peaks.peak_120min_hr = record[23]

        # Done.
        return peaks

    def store(self, *, filename: str, peaks: Peaks):
        """
        Persist a Peaks object in the SQLite database.
        
        Args:
            filename: The name of the file we got this peaks data from.
            peaks:    The peaks itself.
        """

        # Setup parameters for insert.
        params = {
            "filename": filename,
        }
        for key, value in peaks.__dict__.items():
            params[key] = value

        # Insert the record.
        self.conn.execute(INSERT_SQL, params)
        self.conn.commit()

    def name_activity(
        self, *, start_time: datetime, end_time: datetime, activity_name: str
    ):

        self.conn.execute(
            UPDATE_NAME_SQL,
            {
                "activity_name": activity_name,
                "start_time": start_time,
                "end_time": end_time,
            },
        )
        self.conn.commit()
