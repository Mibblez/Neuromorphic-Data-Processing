"""
Fingerprint graphs are a visual display of event counts over time.
Y Axis: event counts in a time window
X Axis: time

CSV Format: on,off,both
"""

import os
import argparse
from typing import Optional
import matplotlib
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import plotting_utils.get_plotting_data as get_plotting_data
from plotting_utils.get_plotting_data import CsvData
from plotting_utils import filename_regex
from plotting_utils.plotting_helper import int_arg_positive_nonzero, float_arg_positive_nonzero, path_arg, file_arg


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("aedat_csv_file", help="CSV containing AEDAT data to be plotted", type=file_arg)
    parser.add_argument(
        "reconstruction_window",
        help="Reconstruction window used to generate the csv file",
        type=int_arg_positive_nonzero,
    )
    parser.add_argument("--plot_xlim", "-x", help="Limit on the X-axis (seconds)", type=float_arg_positive_nonzero)
    parser.add_argument("--save_directory", "-d", help="Save file to directory", default=".", type=path_arg)

    return parser.parse_args()


def plot_event_count(
    event_counts: list, t: list, line_color: str, max_plot_entries_x: Optional[int], plot_title: str, save_dir: str
):
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

    if max_plot_entries_x is not None:
        ax.set_xlim([0, max_plot_entries_x])

    plt.gcf().set_size_inches((20, 5))

    plt.savefig(os.path.join(save_dir, f'{plot_title.replace(" ", "_")}.png'))


def main(args: argparse.Namespace):
    matplotlib.use("Qt5Agg")

    file_name = os.path.basename(args.aedat_csv_file)

    hz = filename_regex.parse_frequency(file_name, "Hz ")
    voltage = filename_regex.parse_voltage(file_name, "V ")
    waveform_type = filename_regex.parse_waveform(file_name, " ")
    degrees = filename_regex.parse_degrees(file_name, " Degrees Polarized")

    plot_title_starter = f"{waveform_type}{voltage}{hz}{degrees}"

    if hz == "" and degrees == "":
        print("WARNING: Could not infer polarizer angle or frequency from file name")

    max_csv_entries = (args.plot_xlim * 1000000) // args.reconstruction_window if args.plot_xlim is not None else -1

    plot_data: CsvData = get_plotting_data.read_aedat_csv(
        args.aedat_csv_file, args.reconstruction_window, max_csv_entries
    )

    plot_event_count(
        plot_data.y_off,
        plot_data.time_windows,
        "r",
        args.plot_xlim,
        f"{plot_title_starter} OFF Events Fingerprint ({args.reconstruction_window}μs Reconstruction Window)",
        args.save_directory,
    )
    plot_event_count(
        plot_data.y_on,
        plot_data.time_windows,
        "g",
        args.plot_xlim,
        f"{plot_title_starter} ON Events Fingerprint ({args.reconstruction_window}μs Reconstruction Window)",
        args.save_directory,
    )
    plot_event_count(
        plot_data.y_all,
        plot_data.time_windows,
        "b",
        args.plot_xlim,
        f"{plot_title_starter} All Events Fingerprint ({args.reconstruction_window}μs Reconstruction Window)",
        args.save_directory,
    )


if __name__ == "__main__":
    args = get_args()
    main(args)
