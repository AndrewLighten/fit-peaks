from file_peaks import get_file_peaks
from peaks import Peaks
from persistence import Persistence

peaks = get_file_peaks(path="./test.fit")


db = Persistence()
db.store(filename="./test.fit", peaks=peaks)

print(f"Start time ........ {peaks.start_time}")
print(f"End time .......... {peaks.end_time}")
print()
print(f"5 second power .... {peaks.peak_5sec_power}")
print(f"30 second power ... {peaks.peak_30sec_power}")
print(f"60 second power ... {peaks.peak_60sec_power}")
print(f"5 minute power .... {peaks.peak_5min_power}")
print(f"10 minute power ... {peaks.peak_10min_power}")
print(f"20 minute power ... {peaks.peak_20min_power}")
print(f"30 minute power ... {peaks.peak_30min_power}")
print(f"60 minute power ... {peaks.peak_60min_power}")
print(f"90 minute power ... {peaks.peak_90min_power}")
print(f"2 hour power ...... {peaks.peak_120min_power}")
print()
print(f"5 second hr ....... {peaks.peak_5sec_hr}")
print(f"30 second hr ...... {peaks.peak_30sec_hr}")
print(f"60 second hr ...... {peaks.peak_60sec_hr}")
print(f"5 minute hr ....... {peaks.peak_5min_hr}")
print(f"10 minute hr ...... {peaks.peak_10min_hr}")
print(f"20 minute hr ...... {peaks.peak_20min_hr}")
print(f"30 minute hr ...... {peaks.peak_30min_hr}")
print(f"60 minute hr ...... {peaks.peak_60min_hr}")
print(f"90 minute hr ...... {peaks.peak_90min_hr}")
print(f"2 hour hr ......... {peaks.peak_120min_hr}")
