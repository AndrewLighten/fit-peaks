import tempfile
import base64

from persistence import Persistence
from activity import Activity
from calculations import calculate_transient_values
from datetime import timedelta

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.pyplot import figure
from scipy.interpolate import make_interp_spline, BSpline
from scipy.ndimage.filters import gaussian_filter1d

def detail_plot_report(id: int):
    """
    Plot the result of an activity.
    
    This will fetch a specific activity from the database, then plot its power
    and heart rate data.
    """

    # Load the peak data.
    db = Persistence()
    if not (activity := db.load_by_id(id)):
        print(f"Cannot find activity #{id}")
        return

    # Calculate transient data
    calculate_transient_values(activity)

    # Do the plot
    _generate_power_plot(activity)

    # Done
    print()



def _generate_power_plot(activity: Activity):
    """
    Generate a plot of power over the activity.
    
    Args:
        activity: The activity whose power we're plotting.
    """

    # Setup colours
    power_color = "lime"
    power_trend_color = "seagreen"
    hr_color = "red"
    hr_trend_color = "brown"
    time_color = "dimgrey"
    title_color = "cyan"

    # Smooth our inputs
    power_smoothed = gaussian_filter1d(activity.raw_power, sigma=1.5)
    hr_smoothed = gaussian_filter1d(activity.raw_hr, sigma=1.5)

    # Setup the numpy arrays
    power_array = np.array(power_smoothed)
    hr_array = np.array(hr_smoothed)

    # Setup the plot
    plt.style.use("dark_background")
    fig, ax1 = plt.subplots()
    fig.set_size_inches(40, 18)

    # Setup the labelling of the X axis
    def format_date(x, pos=None):
        time = activity.start_time + timedelta(seconds=x)
        return time.strftime("%H:%M")

    ax1.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    ax1.set_xlabel("Time", color=time_color, fontsize=20)
    ax1.tick_params(axis="x", colors=time_color, labelsize=20)

    # Setup X coordinate array for trend lines
    x_coords = np.arange(0, len(power_array))

    # Setup the power Y axis
    power_z = np.polyfit(x_coords, power_array, 1)
    power_p = np.poly1d(power_z)
    ax1.plot(power_array, color=power_color, linewidth=1.5)
    ax1.plot(x_coords, power_p(x_coords), ":", color=power_trend_color, linewidth=2)
    ax1.set_ylabel("Power (W)", color=power_color, fontsize=20)
    ax1.grid(linewidth=0.5, color=power_color)
    ax1.tick_params(axis="y", colors=power_color, labelsize=16)

    # Setup the heart rate Y axis
    hr_z = np.polyfit(x_coords, hr_array, 1)
    hr_p = np.poly1d(hr_z)
    ax2 = ax1.twinx()
    ax2.plot(hr_array, color=hr_color, linewidth=1.5)
    ax2.plot(x_coords, hr_p(x_coords), ":", color=hr_trend_color, linewidth=2)
    ax2.set_ylabel("Heart Rate (BPM)", color=hr_color, fontsize=20)
    # ax2.grid(linewidth=0.5, color=hr_color)
    ax2.tick_params(axis="y", colors=hr_color, labelsize=16)

    # Setup the title
    ax1.set_title(activity.activity_name, color=title_color, fontsize=32)

    # Write to a temporary file
    _, tf = tempfile.mkstemp(suffix=".png")
    fig.savefig(tf)

    # Read the image, and Base64 encode it
    with open(tf, "rb") as img_file:
        b64_image = base64.b64encode(img_file.read()).decode("utf-8")

    # Display it in iTerm
    # ESC ] 1337 ; File = [optional arguments] : base-64 encoded file contents ^G
    print(f"\x1B]1337;File=inline=1;preserveAspectRatio=1:{b64_image}\x07")
