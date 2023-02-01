import os
import re
import math
import glob
import argparse
import sys

import matplotlib.pyplot as plt
import matplotlib
from natsort import natsorted, ns

import plotting_utils.get_plotting_data as get_plotting_data
from plotting_utils.get_plotting_data import CsvData

import plotting_utils.plotting_helper as plotting_helper
from plotting_utils.plotting_helper import int_arg_not_negative, path_arg


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("data_folder", type=path_arg, help="Directory containing AEDAT data to be plotted")

    parser.add_argument(
        "--recursive", "-r", action="store_true", help="Recursively search through the data folder for CSV files"
    )

    parser.add_argument(
        "--reconstruction_window",
        "-w",
        type=int_arg_not_negative,
        required=True,
        help="The reconstruction window used to generate the csv files (µs)",
    )

    parser.add_argument("--log_values", "-l", action="store_true", help="Takes the log of all values")

    parser.add_argument(
        "--max_event_count",
        "-m",
        type=int_arg_not_negative,
        default=sys.maxsize,
        help="The maximum event count to read from the file",
    )

    parser.add_argument("--results_directory", "-d", default="./results", type=str, help="Save files to this directory")

    return parser.parse_args()


def clean_file_name(file_name: str) -> str:
    # Regex for name changes
    file_name_changes = {
        "Event Chunks": "",
        "no ?pol": "NoPolarizer",
        "30 ?deg": "",
        "15min": "",
        "1hz": "",
        "-+": " ",
        " +": " ",
        "Ntarget ?": "",
    }

    for occurrence, replacement in file_name_changes.items():
        file_name = re.sub(occurrence, replacement, file_name)

    return file_name


class OnOffBothLines:
    def __init__(self):
        self.on: matplotlib.lines.Line2D = []
        self.off: matplotlib.lines.Line2D = []
        self.both: matplotlib.lines.Line2D = []


def main(args: argparse.Namespace):
    matplotlib.use("Qt5Agg")

    # Make results directory if it doesn't exist
    if not os.path.exists(args.results_directory):
        os.makedirs(args.results_directory)

    off_guas = []
    off_labels = []

    on_guas = []
    on_labels = []

    both_guas = []
    both_labels = []

    # Get csv files inside of the data folder
    csv_paths = (
        glob.glob(os.path.join(args.data_folder, "**/*.csv"), recursive=True)
        if args.recursive
        else glob.glob(os.path.join(args.data_folder, "*.csv"))
    )
    csv_paths = natsorted(csv_paths, alg=ns.IGNORECASE)

    for csv_path in csv_paths:
        d: CsvData = get_plotting_data.read_aedat_csv(csv_path, args.reconstruction_window, args.max_event_count)

        if args.log_values:
            y_zip = zip(d.y_on, d.y_off, d.y_all)
            for i, (on_count, off_count, all_count) in enumerate(y_zip):
                d.y_on[i] = math.log10(on_count) if on_count != 0 else 0
                d.y_off[i] = math.log10(off_count) if off_count != 0 else 0
                d.y_all[i] = math.log10(all_count) if all_count != 0 else 0

        # Strip path and extension from the csv file. Will be used to name/save figures
        csv_filename = os.path.basename(csv_path)
        csv_filename = os.path.splitext(csv_filename)[0]

        csv_filename = clean_file_name(csv_filename)

        f, axes = plt.subplots(nrows=2, ncols=3, sharex=False, sharey=False)
        f.set_size_inches(15, 9.5)
        f.tight_layout()

        lines = OnOffBothLines()

        # Off events
        current_line = plotting_helper.plot_hist(d.y_off, axes, 1, 0, "red", args.log_values)
        current_line.remove()
        off_guas.append(current_line)
        lines.off = current_line

        # On Events
        current_line = plotting_helper.plot_hist(d.y_on, axes, 1, 1, "green", args.log_values)
        current_line.remove()
        on_guas.append(current_line)
        lines.on = current_line

        # On & Off Events
        current_line = plotting_helper.plot_hist(d.y_all, axes, 1, 2, "blue", args.log_values)
        current_line.remove()
        both_guas.append(current_line)
        lines.both = current_line

        off_labels.append(csv_filename + " Off Events")
        on_labels.append(csv_filename + " On Events")
        both_labels.append(csv_filename + " All Events")

        # Format & add data to scatter sub-plots
        axes[0][0].scatter(d.time_windows, d.y_off, c="red", picker=True, s=1)
        axes[1][0].title.set_text(csv_filename + " Off Events")
        axes[0][1].scatter(d.time_windows, d.y_on, c="green", picker=True, s=1)
        axes[1][1].title.set_text(csv_filename + " On Events")
        axes[0][2].scatter(d.time_windows, d.y_all, c="blue", picker=True, s=1)

        plt.title(csv_filename + " All Events")

        csv_savename = csv_filename.replace(" ", "_") + ("_log-values_" if args.log_values else "")
        plt.savefig(os.path.join(args.results_directory, f"{csv_savename}Dots.png"))
        plt.close()


if __name__ == "__main__":
    args = get_args()
    main(args)
