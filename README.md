# README for fit peaks

This is a small project that fetches fitness peak data from Zwift and reports on it.

In essence, it does the following:

- When run, loads all fitness peak data from the Zwift activity directory on your local machine.
- The fitness peak data is mined for both power and HR figures, as well as a few other bits and pieces (activity start and end times, distance, activity name).
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

Note that the activity name and total elevation gain values are *not* available in the `.fit` files. Instead, they're loaded from Zwift via its API. Further down this readme there's details on how to specify your Zwift credentials so the activity names can be loaded.

All of the loaded data is stored in an SQLite database in your home directory (`~/.fit-peaks.dat`).

## Sample report

Here's an example of the power report:

```
Date               Activity                                                                           Distance   Elevation   Start   Duration     5s    30s    60s     5m    10m    20m    30m    60m    90m   120m
────────────────   ────────────────────────────────────────────────────────────────────────────────   ────────   ─────────   ─────   ────────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────
Mon 20 Jan, 2020   Steady State 90min  - Group Training Ride 2.9 - 3.5w (B)                            65.07km         97m   16:10    1:32:30    340    318    302    284    276    272    269    267    262
Tue 21 Jan, 2020   Tour de Zwift: Stage 3 Group Ride - Long Distance                                   42.95km        662m   12:00    1:21:00    438    389    359    327    322    313    309    299
Wed 22 Jan, 2020   SAS - Out and Back (C)                                                              43.12km        337m   18:00    1:08:21    584    556    439    351    338    298    288    275
Wed 22 Jan, 2020   SAS - Start 1.5 Ride (D)                                                            12.39km         19m   19:15    0:22:25    330    289    248    202    173    151
Thu 23 Jan, 2020   3R Watopia Flat Route Race - 3 Laps (30.3km/18.8mi 162m) (C)                        31.32km        183m   17:10    0:49:47    713    572    422    326    310    300    298
Thu 23 Jan, 2020   SZR Sunrise Ride (C)                                                                 5.92km         21m   18:05    0:10:04    297    280    273    217    198
Fri 24 Jan, 2020   Ride with Geraint Thomas and Eric Min                                               21.08km        174m   06:30    0:33:11    291    282    278    264    263    257    248
Sat 25 Jan, 2020   Tour de Zwift: Stage 4 Group Ride - Long Distance                                   27.68km        515m   09:00    0:52:53    446    366    349    336    333    316    311
Sun 26 Jan, 2020   SAS - ULTRA 200km (B)                                                               67.59km        102m   16:00    1:57:21    346    319    310    277    271    266    265    209    193
────────────────   ────────────────────────────────────────────────────────────────────────────────   ────────   ─────────   ─────   ────────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────

Date               Activity                                                                           Distance   Elevation   Start   Duration     5s    30s    60s     5m    10m    20m    30m    60m    90m   120m
────────────────   ────────────────────────────────────────────────────────────────────────────────   ────────   ─────────   ─────   ────────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────
Mon 27 Jan, 2020   3R VOLT Interval Ride (C)                                                           50.05km        129m   17:05    1:16:52    520    427    398    357    341    296    289    272
Tue 28 Jan, 2020   3R Watopia Flat Route Reverse Race - 3 Laps (30.8km/19.1mi 162m) (B)                40.05km        154m   08:15    1:06:04    569    521    399    343    337    325    321    301
Wed 29 Jan, 2020   SAS - Out and Back (C)                                                              43.44km        334m   18:00    1:09:41    400    375    371    362    357    339    329    300
Wed 29 Jan, 2020   Watopia                                                                             14.37km         21m   19:15    0:27:43    281    246    238    189    168    155
Wed 29 Jan, 2020   SAS - Start 1.5 Ride (D)                                                            10.30km         12m   19:45    0:20:26    321    242    213    172    159    140
────────────────   ────────────────────────────────────────────────────────────────────────────────   ────────   ─────────   ─────   ────────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────

                                                                                                                                                  5s    30s    60s     5m    10m    20m    30m    60m    90m   120m
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────
Peak values                                                                                                                             First    761    593    456    382    357    353    330    323    278    239
                                                                                                                                       Second    756    577    446    372    356    339    329    321    275    239
                                                                                                                                        Third    713    572    445    362    348    334    325    317    274
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────
```

Although this example doesn't show it, the top three values for each peak are highlighted when the report is displayed (top value is white-on-red, second is black-on-yellow, and third is black-on-white).

# Usage

Run from the command line, and specify one of three commands:

```
andrew@i9 ~ (master)> fitpeaks
Usage: fitpeaks [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  hr     Report on peak heart rate
  power  Report on peak power
  zwift  Load Zwift data
andrew@i9 ~ (master)>
```

Pretty self explanatory. To load Zwift data, for example:

    andrew@i9 ~/D/fit-peaks (master)> python fit-peaks.py zwift
    
To generate the power report:

    andrew@i9 ~/D/fit-peaks (master)> python fit-peaks.py power

# Config file with Zwift credentials

The `zwift` command will use the Zwift API to fetch activity names. To do this, you need to create a config file that contains your Zwift username, password, and player ID.

Create it in your home directory — it should be available as `~/.fit-peaks.rc`. It should look like this:

    [zwift]
    username = <my-username>
    password = <my-password>
    player-id = <my-player-id>
    
See https://zwiftinsider.com/find-your-zwift-user-id/ for full details on how to find your Zwift player ID. If you can't be bothered reading that, and you're on a Mac, bung this into your terminal:

    grep -i 'player id' ~/Documents/Zwift/Logs/log.txt

# Dependencies

As specified in the `setup.py` file.

To install locally:

```
andrew@i9 ~/D/fit-peaks (master)> pip3.8 install --editable .
Obtaining file:///Users/andrew/Developer/fit-peaks
Requirement already satisfied: Click>=7.0 in /Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages (from fit-peaks==1.0) (7.0)
Requirement already satisfied: termcolor>=1.1.0 in /Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages (from fit-peaks==1.0) (1.1.0)
Requirement already satisfied: fitparse>=1.1.0 in /Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages (from fit-peaks==1.0) (1.1.0)
Requirement already satisfied: zwift-client>=0.2.0 in /Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages (from fit-peaks==1.0) (0.2.0)
Requirement already satisfied: requests in /Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages (from zwift-client>=0.2.0->fit-peaks==1.0) (2.22.0)
Requirement already satisfied: protobuf in /Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages (from zwift-client>=0.2.0->fit-peaks==1.0) (3.11.2)
Requirement already satisfied: certifi>=2017.4.17 in /Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages (from requests->zwift-client>=0.2.0->fit-peaks==1.0) (2019.9.11)
Requirement already satisfied: urllib3!=1.25.0,!=1.25.1,<1.26,>=1.21.1 in /Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages (from requests->zwift-client>=0.2.0->fit-peaks==1.0) (1.25.6)
Requirement already satisfied: idna<2.9,>=2.5 in /Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages (from requests->zwift-client>=0.2.0->fit-peaks==1.0) (2.8)
Requirement already satisfied: chardet<3.1.0,>=3.0.2 in /Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages (from requests->zwift-client>=0.2.0->fit-peaks==1.0) (3.0.4)
Requirement already satisfied: six>=1.9 in /Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages (from protobuf->zwift-client>=0.2.0->fit-peaks==1.0) (1.13.0)
Requirement already satisfied: setuptools in /Users/andrew/Library/Python/3.8/lib/python/site-packages (from protobuf->zwift-client>=0.2.0->fit-peaks==1.0) (42.0.1)
Installing collected packages: fit-peaks
  Running setup.py develop for fit-peaks
Successfully installed fit-peaks
WARNING: You are using pip version 19.3.1; however, version 20.0.2 is available.
You should consider upgrading via the 'pip install --upgrade pip' command.
andrew@i9 ~/D/fit-peaks (master)>
```

# License stuff

Go at it. Do what you want.

# Caveats

I've only used and tested this on a Mac. I have no idea whether it works on Windows or not.
