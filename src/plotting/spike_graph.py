"""
Spike graphs are a record of the acivity of a single pixel or a group of pixels.
Y Axis: ON events correspond to +1 and OFF events correspond to -1
X Axis: Time

CSV Format: on/off,x,y,timestamp
"""
import csv
import math
import sys
import argparse
import os
import itertools
import re
from typing import List
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from plotting_utils.plotting_helper import check_aedat_csv_format
from plotting_utils import filename_regex

file_to_plot = ""
time_limit = math.inf
use_global_area = False
manual_title = None
pixel_x = -1
pixel_y = -1
area_size = -1
save_directory = ""


def get_args():
    global file_to_plot, pixel_x, pixel_y, area_size, time_limit, manual_title, use_global_area, save_directory

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "aedat_csv_file", help="CSV containing AEDAT data to be plotted (ON/OFF,x,y,timestamp)", type=str
    )
    parser.add_argument("--time_limit", "-t", type=float, help="Time limit for the X-axis (seconds)")
    parser.add_argument("--title", type=str, help="Manually set plot title. Title will be auto-generated if not set")
    parser.add_argument("--save_directory", "-d", help="Save file to directory", type=str)

    local_area_args = parser.add_argument_group("Local area arguments")
    local_area_args.add_argument("--pixel_x", "-x", help="X coordinate of the pixel to examine", type=int)
    local_area_args.add_argument("--pixel_y", "-y", help="Y coordinate of the pixel to examine", type=int)
    local_area_args.add_argument("--area_size", "-a", help="Size of area to plot", type=int)

    global_area_args = parser.add_argument_group("Global area arguments")
    global_area_args.add_argument("--global_area", "-g", action="store_true")

    args = parser.parse_args()

    if args.save_directory is not None:
        if not os.path.exists(args.save_directory):
            sys.exit(f'Error: Specified path "{args.save_directory}" does not exist')
        else:
            save_directory = args.save_directory

    file_to_plot = args.aedat_csv_file

    if not os.path.exists(file_to_plot):
        sys.exit(f"File does not exist: {file_to_plot}")
    elif os.path.isdir(file_to_plot):
        sys.exit(f"'{file_to_plot}' is a directory. It should be a csv file")
    if args.time_limit is not None:
        time_limit = args.time_limit

    if args.title is not None:
        manual_title = args.title

    if args.pixel_x or args.pixel_y or args.area_size:
        if args.global_area:
            sys.exit(f"{sys.argv[0]}: error: Global area arguments conflict with Local area arguments")
        elif not (args.pixel_x and args.pixel_y and args.area_size):
            sys.exit(
                f"{sys.argv[0]}: error: pixel_x, pixel_y, and area_size "
                "must all be set when using Local area arguments"
            )

    pixel_x = args.pixel_x
    pixel_y = args.pixel_y
    area_size = args.area_size
    use_global_area = args.global_area


def get_activity_area(
    csv_file, pixel_x: int, pixel_y: int, area_size: int, max_points: int = sys.maxsize, time_limit: float = math.inf
):
    points: List[List[int]] = []
    first_timestamp = 0

    with open(csv_file, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")

        header = next(reader, None)  # Grab the header
        if header is None:
            raise ValueError(f"Error: File '{csv_file}' seems to be empty")

        # Strip whitespace from header if there is any
        header = [x.strip(" ") for x in header]

        if not check_aedat_csv_format(header, ["On/Off", "X", "Y", "Timestamp"]):
            sys.exit(
                f"File {csv_file} is not of the correct format.\n"
                "A csv containing X, Y, and Timestamp columns is required."
            )

        polarity_index = header.index("On/Off")
        x_index = header.index("X")
        y_index = header.index("Y")
        timestamp_index = header.index("Timestamp")

        first_row = next(reader, None)
        if first_row is None:
            raise ValueError(f"Error: File '{csv_file}' has a header but contains no data")

        first_timestamp = int(first_row[timestamp_index])

        if time_limit != math.inf:
            time_limit = time_limit * 1000000  # Convert to microseconds

        for row in itertools.chain([first_row], reader):
            x_pos = int(row[x_index])
            y_pos = 128 - int(row[y_index])

            timestamp = int(row[3]) - first_timestamp
            if timestamp > time_limit:
                return points

            check_x = abs(x_pos - pixel_x)
            check_y = abs(y_pos - pixel_y)

            # Check if this event is inside the specified area
            if check_x < area_size and check_y < area_size:
                if row[polarity_index] in ["1", "True"]:
                    points.append([1, timestamp])
                else:
                    points.append([-1, timestamp])

                if len(points) == max_points:
                    return points

    return points


def auto_generate_title(file_name: str) -> str:
    hz = filename_regex.parse_frequency(file_name, "Hz ")
    voltage = filename_regex.parse_voltage(file_name, "V ")
    waveform_type = filename_regex.parse_waveform(file_name, " ")

    if re.search("no ?pol", file_name, re.IGNORECASE):
        auto_title = f"{waveform_type}{voltage}{hz}Unpolarized"
    else:
        degrees = filename_regex.parse_degrees(file_name, " Degrees Polarized")
        auto_title = f"{waveform_type}{voltage}{hz}{degrees}"

    return auto_title


if __name__ == "__main__":
    get_args()
    matplotlib.use("Qt5Agg")

    file_path = file_to_plot

    if use_global_area:
        plot_points = get_activity_area(file_to_plot, 999, 999, 9999, time_limit=time_limit)
    else:
        plot_points = get_activity_area(file_path, pixel_x, pixel_y, area_size, time_limit=time_limit)

    # Add lines to plot
    for point in plot_points:
        timestamp_seconds = point[1] / 1000000  # Convert to seconds
        color = "g" if point[0] == 1 else "r"

        # Add to points at the same X value to make vertical lines
        plt.plot([timestamp_seconds, timestamp_seconds], [0, point[0]], color)

    plt.ylim(-1.1, 1.1)

    # Get file name from path and remove extension
    file_name = os.path.basename(file_path)
    file_name = os.path.splitext(file_name)[0]

    if manual_title is None:
        title = auto_generate_title(file_name)
        plt.title(title)
    else:
        plt.title(manual_title)

    plt.xlabel("Time (Seconds)")

    plt.gcf().set_size_inches((25, 5))

    # Get axis
    ax = plt.gca()

    # Set Y-axis tick spacing
    ax.yaxis.set_major_locator(mticker.MultipleLocator(1))

    # Increase X and Y tick size
    ax.tick_params(axis="both", which="major", labelsize=12)

    plt.axhline(0, color="black")

    plot_file_name = ""
    if use_global_area:
        plot_file_name = f"spike_plot-{file_name}-global.png"
    else:
        plot_file_name = f"spike_Plot-{file_name}_X-{pixel_x}_Y-{pixel_y}_Area-{area_size}.png"

    plt.savefig(os.path.join(save_directory, plot_file_name), bbox_inches="tight", pad_inches=0.1)
