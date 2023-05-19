![GitHub pull requests](https://img.shields.io/github/issues-pr/andrewlighten/fit-peaks)

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
ID      Date               Activity                                   Distance   Elevation   Start   Duration      Speed       5s    30s    60s     5m    10m    20m    30m    60m    90m   120m    Max    Avg   Norm    FTP    V/I    I/F    TSS   AeroDe   AeroEf   CTL   ATL   TSB
─────   ────────────────   ────────────────────────────────────────   ────────   ─────────   ─────   ────────   ──────────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ──────   ──────   ───   ───   ───
1602    Mon 27 Jun, 2022   Mountain Route in Watopia                   30.13km        682m   19:13    0:58:20   30.99km/hr    597    525    435    360    350    341    337                         634    296    323    325     8%   0.99     96    -3.0%    2.18%    56    47     9

1603    Tue 28 Jun, 2022   The Fan Flats in Richmond                   10.06km         20m   17:07    0:17:19   34.86km/hr    561    539    424    310    274                                       624    234    269    325    13%   0.83     19   -41.3%    2.36%    56    60    -4
1604                       Three Little Sisters in Watopia             40.08km        449m   17:29    1:09:12   34.75km/hr    483    424    382    324    296    277    277    262                  535    256    268    325     4%   0.82     78     9.6%    2.00%                  

1605    Thu 30 Jun, 2022   Three Sisters in Watopia                    50.01km        943m   17:16    1:29:26   33.55km/hr    762    602    447    389    379    371    367    343                  806    311    338    325     8%   1.04    161     4.9%    2.36%    56    58    -2

1606    Fri 01 Jul, 2022   Volcano Circuit in Watopia                   5.47km         27m   15:48    0:09:56   33.04km/hr    437    325    265    235                                              461    202    217    352          0.62      6                      58    67    -9
1607                       Group Ride: SZR After Sun (C) on Spri...    44.57km        235m   16:00    1:09:03   38.73km/hr    432    381    375    269    231    220    216    214                  444    211    223    352     5%   0.63     46     8.7%    1.91%                  

1608    Sun 03 Jul, 2022   The Fan Flats in Richmond                    8.06km         20m   17:24    0:15:23   31.44km/hr    272    257    238    211    199                                       289    186    193    352          0.55      7                      59    67    -8
1609                       Pace Partner Ride: Figure 8 in Watopi...    32.04km        294m   17:41    0:52:57   36.31km/hr    359    326    300    242    235    223    222                         399    212    222    352     5%   0.63     35    -4.1%    1.90%                  
─────   ────────────────   ────────────────────────────────────────   ────────   ─────────   ─────   ────────   ──────────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ────   ──────   ──────   ───   ───   ───
                                                      Weekly totals   220.43km      2,670m            6:21:36                                                                                                                                 448
                                                    Weekly averages    44.09km        534m            1:16:19                 487    422    358    292    280    286    283    273                                                             89                      57    59    -2
                                                      Weekly maxima    50.01km        943m            1:29:26                 762    602    447    389    379    371    367    343                  806    311    338                 1.04    161                      59    67    -9

```

Although this example doesn't show it, the top three values for each peak are highlighted when the report is displayed (top value is white-on-red, second is black-on-yellow, and third is black-on-white).

# Usage

Run from the command line, and specify one of three commands:

```
$ fitpeaks
Usage: fitpeaks [OPTIONS] [COMMAND] [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  hr     Report on peak heart rate
  power  Report on peak power
  fetch  Load Zwift data
```

If you omit the command, it shows a brief summary of the past week:

```
$ fitpeaks
                                                                                                                                                                      ┌──── Watts ─────┐
ID      Date               Activity                                                                           Start   Distance    Elevation   Duration        Speed    Max    Avg   Norm   VI    IF     TSS   AeroDe
─────   ────────────────   ────────────────────────────────────────────────────────────────────────────────   ─────   ────────   ──────────   ────────   ──────────   ────   ────   ────   ──   ────   ────   ──────
1605    Thu 30 Jun, 2022   Three Sisters in Watopia                                                           17:16    50.01km         943m    1:29:26   33.55km/hr    806    311    338   8%   1.04    161     4.9%
                                                                                                                       50.01km         943m    1:29:26                                                  161

1606    Fri 01 Jul, 2022   Volcano Circuit in Watopia                                                         15:48     5.47km          27m    0:09:56   33.04km/hr    461    202    217        0.62      6         
1607                       Group Ride: SZR After Sun (C) on Sprinter's Playground in Makuri Islands           16:00    44.57km         235m    1:09:03   38.73km/hr    444    211    223   5%   0.63     46     8.7%
                                                                                                                       50.04km         262m    1:18:59                                                   52

1608    Sun 03 Jul, 2022   The Fan Flats in Richmond                                                          17:24     8.06km          20m    0:15:23   31.44km/hr    289    186    193        0.55      7         
1609                       Pace Partner Ride: Figure 8 in Watopia with C. Cadence                             17:41    32.04km         294m    0:52:57   36.31km/hr    399    212    222   5%   0.63     35    -4.1%
                                                                                                                       40.10km         314m    1:08:20                                                   42

1610    Mon 04 Jul, 2022   Pace Partner Ride: Tempus Fugit in Watopia with D. Draft                           17:19    15.02km          22m    0:23:59   37.58km/hr    278    182    186   2%   0.53     11     4.7%
1611                       London Loop in London                                                              17:46    20.02km         236m    0:32:01   37.53km/hr    744    318    344   8%   0.98     50    11.9%
1612                       Pace Partner Ride: Hilly Route in Watopia with C. Cadence                          18:20    10.13km         121m    0:17:03   35.65km/hr    345    198    215   8%   0.61     10     7.8%
                                                                                                                       45.18km         379m    1:13:03                                                   71
─────   ────────────────   ────────────────────────────────────────────────────────────────────────────────   ─────   ────────   ──────────   ────────   ──────────   ────   ────   ────   ──   ────   ────   ──────
                                                                                            Totals for week           185.33km       1,898m    5:09:48                                                  326
                                                                                           Averages per day            46.33km         474m    1:17:27                                                   81
                                                                          Maxima from individual activities            50.01km         943m    1:29:26   38.73km/hr    806    318    344        1.04    161
```

Pretty self explanatory. To load Zwift data, for example:

    $ fitpeaks fetch
    
To generate the power report:

    $ fitpeaks power

# Config file with Zwift credentials

The `fetch` command will use the Zwift API to fetch activity names. To do this, you need to create a config file that contains your Zwift username, password, and player ID.

Create it in your home directory — it should be available as `~/.fit-peaks.rc`. It should look like this:

    [zwift]
    username = <my-username>
    password = <my-password>
    player-id = <my-player-id>
    
See [https://zwiftinsider.com/find-your-zwift-user-id/](https://zwiftinsider.com/find-your-zwift-user-id/) for full details on how to find your Zwift player ID. If you can't be bothered reading that, and you're on a Mac, bung this into your terminal:

    grep -i 'player id' ~/Documents/Zwift/Logs/log.txt

# Athlete file

You need to create an `.athlete.json` file in your home directory. This is used so the tool can understand your FTP and heart rate details. It needs this to calculate intensity factor, power zones, heart rate zones, etc.

Here's mine:

```
[
    {"date":"01-Jan-1990", "ftp":279, "rhr":42, "thr": 155, "mhr": 184},
    {"date":"10-Dec-2019", "ftp":316, "rhr":41, "thr": 155, "mhr": 184},
    {"date":"23-Dec-2019", "ftp":322, "rhr":41, "thr": 155, "mhr": 184},
    {"date":"31-Dec-2019", "ftp":335, "rhr":41, "thr": 156, "mhr": 184},
    {"date":"18-Feb-2020", "ftp":338, "rhr":40, "thr": 156, "mhr": 184},
    {"date":"25-Feb-2020", "ftp":341, "rhr":40, "thr": 156, "mhr": 184},
    {"date":"28-Feb-2020", "ftp":354, "rhr":39, "thr": 156, "mhr": 184},
    {"date":"18-May-2021", "ftp":313, "rhr":42, "thr": 163, "mhr": 174},
    {"date":"09-May-2022", "ftp":325, "rhr":44, "thr": 163, "mhr": 173},
    {"date":"30-Jun-2022", "ftp":352, "rhr":44, "thr": 163, "mhr": 176}
]
```

(Yeah, FTP dropped a fair bit for a while there. Life got in the way.) 

Each entry in the array has five attributes:

- `date` represents the date that the entry takes effect;
- `ftp` is your FTP from that date forward;
- `rhr` is your resting heart rate from that date forward;
- `thr` is your threshold heart rate from that date forward; and
- `mhr` is your maximum heart rate from that date forward.

When your FTP changes, or your heart rate details change, simply add a new entry to the end of the array. Don't forget to add a `,` to the end of the previous entry.

# Dependencies

As specified in the `setup.py` file.

To install locally:

```
$ pip3.8 install --editable .
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
```

# License stuff

Go at it. Do what you want.

# Caveats

I've only used and tested this on a Mac. I have no idea whether it works on Windows or not.
