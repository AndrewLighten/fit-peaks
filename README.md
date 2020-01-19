# README for fit peaks

This is a small project that fetches fitness peak data from Zwift and reports on it.

In essence, it does the following:

- When run, loads all fitness peak data from the Zwift activity directory on your local machine.
- The fitness peak data is mined for both power and HR figures, as well as a few other bits and pieces (activity start and end times).
- The peak data is stored in an SQL database. This storage has one record per activity, and for that activity, it has the start time, end time, and peak power and HR for the following time periods:
    - 5 seconds
    - 30 seconds
    - 60 seconds
    - 5 minutes
    - 10 minutes
    - 20 minutes
    - 30 minutes
    - 60 minutes
    - 90 minutes
    - 120 minutes
- Having loaded the peak values, a report can be produced to show what those peak power and HR figures are. 

Here's an example:

```
Date               Start   Duration     5s    30s    60s     5m    10m    20m    30m    60m    90m   120m
────────────────   ─────   ────────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────
Mon 13 Jan, 2020   17:00    1:48:48    450    411    368    310    284    274    270    264    245       
Tue 14 Jan, 2020   09:00    1:18:02    373    342    340    305    289    280    266    263              
Wed 15 Jan, 2020   18:00    1:08:06    464    442    400    372    328    302    305    274              
Thu 16 Jan, 2020   18:05    1:19:57    484    452    446    349    324    316    309    294              
Fri 17 Jan, 2020   17:00    1:19:12    423    416    411    346    328    322    318    310              
Sat 18 Jan, 2020   12:06    0:54:14    502    412    352    342    338    324    318                     
Sun 19 Jan, 2020   19:05    0:41:58    416    397    395    382    348    310    286                     
Sun 19 Jan, 2020   20:12    0:21:59    355    338    332    326    212    106                            
────────────────   ─────   ────────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────

                                        5s    30s    60s     5m    10m    20m    30m    60m    90m   120m
───────────────────────────────────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────
Peak values                            761    593    456    382    356    353    330    323    278    239
───────────────────────────────────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────
andrew@i9 ~/D/fit-peaks (master)> 
```

Although this example doesn't show it, the maximum figure for each peak is highlighted when the report is displayed.

# License and use

Go at it. Do what you want.