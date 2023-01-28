import numpy as np
from scipy import stats
from scipy.stats import norm
import matplotlib
from typing import List
import os
import re

import plotting_utils.get_plotting_data as get_plotting_data


def float_arg_positive_nonzero(arg: str) -> float:
    arg_float = float(arg)

    if arg_float <= 0:
        raise ValueError(f"Arg {arg} must be greater than 0")

    return arg_float


def int_arg_positive_nonzero(arg: str) -> int:
    arg_int = int(arg)

    if arg_int <= 0:
        raise ValueError(f"Arg {arg} must be greater than 0")

    return arg_int

def int_arg_not_negative(arg: str) -> int:
    arg_int = int(arg)

    if arg_int < 0:
        raise ValueError(f"Arg {arg} cannot be negative")

    return arg_int


def path_arg(arg: str) -> str:
    if not os.path.exists(arg):
        raise ValueError(f"Specified directory '{arg}' does not exist")

    return arg


def file_arg(arg: str) -> str:
    if not os.path.isfile(arg):
        raise ValueError(f"Specified file '{arg}' does not exist")

    return arg


class FloatRangeArg(object):
    def __init__(self, min, max):
        self.min = min
        self.max = max

    def __eq__(self, other):
        return self.min <= other <= self.max

    # Define to make argparse's error message more readable when an out of range value is provided
    def __repr__(self) -> str:
        return f"{self.min}-{self.max}"

    # Define to avoid having to wrap the class in a list when providing to choices
    def __getitem__(self, index):
        if index == 0:
            return self
        else:
            raise IndexError()


def check_aedat_csv_format(csv_header: List[str], required_data: List[str]) -> bool:
    """Checks that a provided CSV header containes the required data

    Parameters
    ----------
    csv_header : List[str]
        Header read from a CSV
    required_data : List[str]
        Entries that must be present in the provided header

    Returns
    -------
    bool
        True if required_data is a subset of csv_header. False otherwise
    """
    return set(required_data).issubset(set([x.strip() for x in csv_header]))


def clean_line_title(label: str) -> str:
    line_title_changes = {" ?(Off|On|All) Events": "", " ?[0-9]+(_| )?m[vV]": ""}

    for occurrence, replacement in line_title_changes.items():
        label = re.sub(occurrence, replacement, label)

    return label


def paddBins(hist_bins: np.ndarray, pad_bins: int):
    # pad left & right
    difference = hist_bins[1] - hist_bins[0]
    for i in range(pad_bins):
        hist_bins = np.insert(hist_bins, 0, hist_bins[0] - (difference * (i + 1)))

    for i in range(pad_bins):
        hist_bins = np.append(hist_bins, hist_bins[len(hist_bins) - 1] + difference * (i + 1))

    return hist_bins


def plot_hist(
    data: List, axes, plot_major: int, plot_minor: int, plot_color: str, log_values: bool
) -> matplotlib.lines.Line2D:
    """
    Plots only the hist.
    """
    y, x, _ = axes[plot_major][plot_minor].hist(
        data, bins=100, color=plot_color, edgecolor=plot_color, linewidth=1.5, density=True
    )
    x = paddBins(x, 100)

    (mu, sigma) = norm.fit(data)
    y = stats.norm.pdf(x, mu, sigma)
    accuracy = 0.002
    if log_values:
        accuracy = 0.00002
    while y[0] < accuracy:
        y = np.delete(y, 0)
        x = np.delete(x, 0)
    while y[len(y) - 1] < accuracy:
        y = np.delete(y, len(y) - 1)
        x = np.delete(x, len(x) - 1)

    return axes[plot_major][plot_minor].plot(x, y, linewidth=2)[0]


def centerAllGuas(
    lines: List[matplotlib.lines.Line2D],
    axes_index: int,
    labels: List[str],
    title: str,
    axes: np.ndarray,
    config: get_plotting_data.EventChunkConfig,
    smart_shifting: bool = False,
):
    labels_copy = np.copy(labels)

    max_height_pol = 0  # Get the largest y value in all the polarized lines
    max_height_nopol = 0  # Get the largest y value in all the non-polarized lines

    # TODO: see if getting raw y_data (get_ydata(1)) is useful

    for i, line in enumerate(lines):
        if "NoPolarizer" in labels_copy[i]:
            if np.max(line.get_ydata(0)) > max_height_nopol:
                max_height_nopol = np.max(line.get_ydata(0))
        else:
            if np.max(line.get_ydata(0)) > max_height_pol:
                max_height_pol = np.max(line.get_ydata(0))

    for i, line in enumerate(lines):
        max_y = np.max(line.get_ydata(0))
        index = np.where(line.get_ydata(0) == max_y)
        offset = line.get_xdata()[index[0][0]]
        row = 0

        if smart_shifting:
            # TODO: fine control for automatic centering not working
            if line.get_ydata(0)[index[0][0] - 1] > offset:
                diff_low = line.get_xdata()[index[0][0] - 1] - offset
            else:
                diff_low = offset - line.get_xdata()[index[0][0] - 1]

            if line.get_ydata(0)[index[0][0] + 1] > offset:
                diff_high = line.get_xdata()[index[0][0] - 1] + offset
            else:
                diff_high = offset - line.get_xdata()[index[0][0] + 1]

            if diff_high > diff_low:
                offset = offset + (offset - diff_high) / 2
            else:
                offset = offset - (offset - diff_low) / 2
        else:
            # FIXME: manual shifting for now
            if "NoPolarizer" in labels_copy[i]:
                if "burst" in labels_copy[i]:
                    offset = offset + 1.0
                elif "sine" in labels_copy[i]:
                    offset = offset - 2.0
            else:
                if "triangle" in labels_copy[i]:
                    offset = offset + 0.7
                elif "burst" in labels_copy[i]:
                    offset = offset + 0.5

        for j in range(len(line.get_xdata())):
            line.get_xdata()[j] = line.get_xdata()[j] - offset

        labels_copy[i] = clean_line_title(labels_copy[i])

        if "NoPolarizer" in labels_copy[i]:
            row = 1
            labels_copy[i] = labels_copy[i].replace(" NoPolarizer", "")
            axes[axes_index][row].plot(
                line.get_xdata(), line.get_ydata(0) / max_height_nopol, label=labels_copy[i].capitalize()
            )
        else:
            axes[axes_index][row].plot(
                line.get_xdata(), line.get_ydata(0) / max_height_pol, label=labels_copy[i].capitalize()
            )

    axes[axes_index][1].title.set_text("Non-Polarized " + title)
    axes[axes_index][0].title.set_text("Polarized " + title)
    axes[axes_index][0].legend(loc=1, prop={"size": 11})
    axes[axes_index][1].legend(loc=1, prop={"size": 11})

    axes[axes_index][0].set_ylim(config.gaussianMinY, config.gaussianMaxY + 0.05)
    axes[axes_index][1].set_ylim(config.gaussianMinY, config.gaussianMaxY + 0.05)


def showAllGuas(
    lines: List[matplotlib.lines.Line2D],
    labels: List[str],
    axes_index: int,
    title: str,
    axes: np.ndarray,
    config: get_plotting_data.EventChunkConfig,
):
    labels_copy = np.copy(labels)
    max_height = 0

    for line in lines:
        if np.max(line.get_ydata(0)) > max_height:
            max_height = np.max(line.get_ydata(0))

    for i, line in enumerate(lines):
        shift_x = line.get_xdata()[0]
        for j, x in enumerate(line.get_xdata()):
            line.get_xdata()[j] = x - shift_x
        shift_y = line.get_ydata(0)[0]
        for j, y in enumerate(line.get_ydata()):
            line.get_ydata(0)[j] = y - shift_y
        row = 0
        if "NoPolarizer" in labels_copy[i]:
            labels_copy[i] = labels_copy[i].replace(" NoPolarizer", "")
            row = 1

        labels_copy[i] = clean_line_title(labels_copy[i])
        axes[axes_index][row].plot(line.get_xdata(), line.get_ydata(0) / max_height, label=labels_copy[i])

    axes[axes_index][1].title.set_text("Non-Polarized " + title)
    axes[axes_index][0].title.set_text("Polarized " + title)
    axes[axes_index][0].legend(loc=1, prop={"size": 11})
    axes[axes_index][1].legend(loc=1, prop={"size": 11})

    axes[axes_index][0].set_ylim(config.gaussianMinY, config.gaussianMaxY + 0.05)
    axes[axes_index][1].set_ylim(config.gaussianMinY, config.gaussianMaxY + 0.05)
