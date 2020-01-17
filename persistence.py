import sqlite3
import os.path
from peaks import Peaks

DATABASE_NAME = "peaks.dat"

INSERT_SQL = """
    insert into peaks 
    (
        filename, start_time, end_time,
        peak_5sec_power,  peak_30sec_power, peak_60sec_power, peak_5min_power,  peak_10min_power,
        peak_20min_power, peak_30min_power, peak_60min_power, peak_90min_power, peak_120min_power, 
        peak_5sec_hr,     peak_30sec_hr,    peak_60sec_hr,    peak_5min_hr,     peak_10min_hr,
        peak_20min_hr,    peak_30min_hr,    peak_60min_hr,    peak_90min_hr,    peak_120min_hr
    )
    values 
    (
        :filename, :start_time, :end_time,
        :peak_5sec_power,  :peak_30sec_power, :peak_60sec_power, :peak_5min_power,  :peak_10min_power,
        :peak_20min_power, :peak_30min_power, :peak_60min_power, :peak_90min_power, :peak_120min_power, 
        :peak_5sec_hr,     :peak_30sec_hr,    :peak_60sec_hr,    :peak_5min_hr,     :peak_10min_hr,
        :peak_20min_hr,    :peak_30min_hr,    :peak_60min_hr,    :peak_90min_hr,    :peak_120min_hr

    )
    on conflict(filename) do update
    set start_time          = :start_time,
        end_time            = :end_time,
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


class Persistence:
    def __init__(self):
        new_database = not os.path.exists(DATABASE_NAME)
        self.conn = sqlite3.connect(DATABASE_NAME)
        if new_database:
            self.conn.execute(
                """
            create table peaks
            (
                filename            varchar         primary key,
                start_time          timestamp,
                end_time            timestamp,
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
            )

    def store(self, *, filename: str, peaks: Peaks):

        params = {
            "filename": filename,
        }
        for key, value in peaks.__dict__.items():
            params[key] = value

        self.conn.execute(INSERT_SQL, params)
        self.conn.commit()
