"""
Fingerprint graphs are a visual display of event counts over time.
Y Axis: event counts in a time window
X Axis: time

CSV Format: on,off,both
"""

import os
import sys
import argparse
from typing import Optional
import matplotlib
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import plotting_utils.get_plotting_data as get_plotting_data
from plotting_utils.get_plotting_data import CsvData
from plotting_utils import filename_regex

file_to_plot = ""
x_lim: Optional[int] = None
reconstruction_window = 0
save_directory = ""


def get_args():
    global file_to_plot, x_lim, reconstruction_window, save_directory

    parser = argparse.ArgumentParser()
    parser.add_argument("aedat_csv_file", help="CSV containing AEDAT data to be plotted", type=str)
    parser.add_argument(
        "reconstruction_window",
        help="Reconstruction window used to generate file: int or path to config file",
        type=str,
    )
    parser.add_argument("--plot_xlim", "-x", help="Limit on the X-axis (seconds)", type=float)
    parser.add_argument("--save_directory", "-d", help="Save file to directory", type=str)
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

    x_lim = args.plot_xlim

    if x_lim is not None and x_lim <= 0:
        sys.exit("The argument --plot_xlim/-x must be greater than 0")

    if args.reconstruction_window.isdigit() and args.reconstruction_window != "0":
        reconstruction_window = int(args.reconstruction_window)

    else:
        if args.reconstruction_window.lstrip("-").isdigit():
            sys.exit("The argument reconstruction window must be greater than 0")

        if os.path.exists(args.reconstruction_window) and args.reconstruction_window.endswith(".json"):
            config = get_plotting_data.parseConfig(args.reconstruction_window)
            reconstruction_window = config.reconstructionWindow
        else:
            sys.exit(f"The path {args.reconstruction_window} does not point to a json file")


def plot_event_count(event_counts: list, t: list, line_color: str, max_plot_entries_x: Optional[int], plot_title: str):
    plt.clf()

    plt.title(plot_title)
    plt.xlabel("Time (seconds)")
    plt.ylabel("Event Count")

    plt.yscale("log", base=10)  # Use a log scale

    ax = plt.gca()  # Get axis
    plt.grid()

    # Ensure that Y-axis ticks are displayed as whole numbers
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.yaxis.set_minor_formatter(mticker.NullFormatter())  # Disable minor tick markers

    # Set Y-axis tick spacing
    try:
        count_range = max(event_counts) - min(event_counts)
        major_spacing = round((count_range / 5), -1)
        ax.yaxis.set_major_locator(mticker.MultipleLocator(major_spacing))
        ax.yaxis.set_minor_locator(mticker.MultipleLocator(major_spacing / 2))
        # ax.set_ylim([max(event_counts), min(event_counts)])
    except ValueError:
        print("WARNING: Could not set tick spacing. No events present?")

    # Plot lines with circles on the points
    plt.plot(t, event_counts, "-o", markersize=4, c=line_color)

    if x_lim is not None:
        ax.set_xlim([0, max_plot_entries_x])

    plt.gcf().set_size_inches((20, 5))

    plt.savefig(os.path.join(save_directory, f'{plot_title.replace(" ", "_")}.png'))


if __name__ == "__main__":
    get_args()
    matplotlib.use("Qt5Agg")

    file_name = os.path.basename(file_to_plot)

    hz = filename_regex.parse_frequency(file_name, "Hz ")
    voltage = filename_regex.parse_voltage(file_name, "V ")
    waveform_type = filename_regex.parse_waveform(file_name, " ")
    degrees = filename_regex.parse_degrees(file_name, " Degrees Polarized")

    if hz == "" and degrees == "":
        print("WARNING: Could not infer polarizer angle or frequency from file name")

    max_csv_entries = (x_lim * 1000000) // reconstruction_window if x_lim is not None else -1

    plot_data: CsvData = get_plotting_data.read_aedat_csv(file_to_plot, reconstruction_window, max_csv_entries)

    plot_event_count(
        plot_data.y_off,
        plot_data.time_windows,
        "r",
        x_lim,
        f"{waveform_type}{voltage}{hz}{degrees}"
        f" OFF Events Fingerprint ({reconstruction_window}μs Reconstruction Window)",
    )
    plot_event_count(
        plot_data.y_on,
        plot_data.time_windows,
        "g",
        x_lim,
        f"{waveform_type}{voltage}{hz}{degrees}"
        f"ON Events Fingerprint ({reconstruction_window}μs Reconstruction Window)",
    )
    plot_event_count(
        plot_data.y_all,
        plot_data.time_windows,
        "b",
        x_lim,
        f"{waveform_type}{voltage}{hz}{degrees}"
        f"All Events Fingerprint ({reconstruction_window}μs Reconstruction Window)",
    )
