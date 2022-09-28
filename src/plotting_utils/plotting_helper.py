import numpy as np
from scipy import stats
from scipy.stats import norm
import matplotlib.pyplot as plt
import matplotlib
from sklearn.metrics import pairwise_distances_argmin
from typing import Tuple, List
from pylab import plot, xlabel, ylabel
from scipy import fft, arange
import re

import plotting_utils.get_plotting_data as get_plotting_data


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
    return set(required_data).issubset(set(csv_header))


def clean_line_title(label: str) -> str:
    line_title_changes = {" ?(Off|On|All) Events": "", " ?[0-9]+(_| )?m[vV]": ""}

    for occurrence, replacement in line_title_changes.items():
        label = re.sub(occurrence, replacement, label)

    return label


def paddBins(bins2: np.ndarray, paddTimes: int):

    # pad left & right
    difference = bins2[1] - bins2[0]
    for i in range(paddTimes):
        bins2 = np.insert(bins2, 0, bins2[0] - (difference * (i + 1)))

    for i in range(paddTimes):
        bins2 = np.append(bins2, bins2[len(bins2) - 1] + difference * (i + 1))

    return bins2


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


def find_clusters(X: np.ndarray, n_clusters: int, rseed: int = 2) -> Tuple[np.ndarray, np.ndarray]:
    # 1. Randomly choose clusters
    rng = np.random.RandomState(rseed)
    i = rng.permutation(X.shape[0])[:n_clusters]
    centers = X[i]

    while True:
        # 2a. Assign labels based on closest center
        labels = pairwise_distances_argmin(X, centers)

        # 2b. Find new centers from means of points
        new_centers = np.array([X[labels == i].mean(0) for i in range(n_clusters)])

        # 2c. Check for convergence
        if np.all(centers == new_centers):
            break
        centers = new_centers

    return centers, labels


def plotKmeans(data, axes, row: int, columnIndex: int, numberOfCenters: int):
    pts = np.asarray(data)
    centers, labels = find_clusters(pts, numberOfCenters)
    axes[row][columnIndex].scatter(pts[:, 0], pts[:, 1], c=labels, s=10, cmap="viridis")
    axes[row][columnIndex].scatter(centers[:, 0], centers[:, 1], c="red")


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


def showFFT(data, file_count, folders):
    fftX = np.linspace(0.0, 1.0 / (2.0 * (1.0 / 800.0)), file_count / 2)

    polLabels = []
    polFreq = []
    noPolLabels = []
    noPolFreq = []

    for i, y in enumerate(data):
        if "no pol" in folders[i]:
            noPolLabels.append(folders[i])
            noPolFreq.append(y)
        else:
            polLabels.append(folders[i])
            polFreq.append(y)

        _, axes = plt.subplots(nrows=1, ncols=2, sharex=True, sharey=True)

    for i, y in enumerate(polFreq):
        axes[0].plot(
            fftX, 2.0 / file_count * np.abs(y[: file_count // 2]), label=polLabels[i].replace("Event Chunks", "")
        )

    axes[0].set_xlim(2, 60)
    axes[0].legend()

    for i, y in enumerate(noPolFreq):
        axes[1].plot(
            fftX, 2.0 / file_count * np.abs(y[: file_count // 2]), label=noPolLabels[i].replace("Event Chunks", "")
        )

    axes[1].set_xlim(2, 60)
    axes[1].legend()
    plt.show()


# TODO: make sure this works
def plotSpectrum(y, Fs):
    n = len(y)  # length of the signal
    k = arange(n)
    T = n / Fs
    frq = k / T  # two sides frequency range
    frq = frq[range(n // 2)]  # one side frequency range

    Y = fft(y) / n  # fft computing and normalization
    Y = Y[range(n // 2)]

    plot(frq, abs(Y), "r")  # plotting the spectrum
    xlabel("Freq (Hz)")
    ylabel("|Y(freq)|")
