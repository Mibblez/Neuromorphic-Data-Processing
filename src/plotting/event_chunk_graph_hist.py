import os
import re
import math
import glob
import argparse
import sys
from typing import List

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from natsort import natsorted, ns

import plotting_utils.get_plotting_data as get_plotting_data
from plotting_utils.get_plotting_data import CsvData

import plotting_utils.plotting_helper as plotting_helper


def get_args() -> get_plotting_data.EventChunkConfig:
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    required_args = parser.add_argument_group("required unless using a config file")
    flags = parser.add_argument_group("flags")

    parser.add_argument("data_folder", type=str, help="Directory containing AEDAT data to be plotted")

    parser.add_argument("--config", "-c", type=str, help="Path to a config file")

    required_args.add_argument(
        "--data_set_type",
        "-d",
        type=str,
        choices=["w", "f", "wf", "b"],
        help="The type of data to be plotted where:\n"
        "w = waveforms\n"
        "f = frequencies\n"
        "wf = waveforms and frequencies\n"
        "b = backgrounds",
    )

    required_args.add_argument("--plot_constant", "-pc", type=str, help="The variable that is constant on the graph")

    required_args.add_argument(
        "--reconstruction_window", "-rw", type=int, help="The reconstruction window used to generate the csv files (µs)"
    )

    flags.add_argument("--show_figures", "-s", action="store_true", help="Show figures instead of displaying them")

    flags.add_argument("--plot_variance", "-pv", action="store_true", help="Calculate variance values")

    flags.add_argument("--plot_fwhm", "-pf", action="store_true", help="Calculate variance values")

    flags.add_argument("--log_values", "-l", action="store_true", help="Takes the log of all values")

    parser.add_argument(
        "--graph_type",
        "-g",
        type=str,
        default="hist",
        choices=["hist", "wavelets", "kmeans", "smooth"],
        help="The type of graph to be plotted",
    )

    parser.add_argument(
        "--fwhm_multiplier",
        "-fm",
        type=float,
        default=2.355,
        help="Used to change FHWM(2.355) to standard deviation(1)",
    )

    parser.add_argument(
        "--max_event_count", "-mc", type=int, default=sys.maxsize, help="The maximum event count to read from the file"
    )

    parser.add_argument(
        "--gaussian_min_y",
        "-gmin",
        type=float,
        default=0.0,
        choices=plotting_helper.FloatRangeArg(0.0, 1.0),
        help="Minimum value on the gaussian y axis",
    )

    parser.add_argument(
        "--gaussian_max_y",
        "-gmax",
        type=float,
        default=1.0,
        choices=plotting_helper.FloatRangeArg(0.0, 1.0),
        help="Maximum value on the gaussian y axis",
    )

    args = parser.parse_args()

    # Make sure the data folder exists
    if not os.path.isdir(args.data_folder):
        parser.error(f'argument data_folder: provided directory "{args.data_folder}" does not exist')

    # data_set_type, plot_constant, and reconstruction_window are not required when --config is used
    if not args.config and (
        args.data_set_type is None or args.plot_constant is None or args.reconstruction_window is None
    ):
        parser.error(
            "the following arguments are required: "
            "--data_set_type/-d, --plot_constant/-pc, --reconstruction_window/-rw"
        )

    # The config argument cannot be used with data_set_type, plot_constant, or reconstruction_window
    if args.config and (args.data_set_type or args.plot_constant or args.reconstruction_window):
        parser.error(
            "the argument --config/-c conflicts with "
            "--data_set_type/-d, --plot_constant/-pc, and --reconstruction_window/-rw"
        )

    if args.config:
        # Make sure the config file exists
        if not os.path.isfile(args.config):
            parser.error(f"argument --config/-c: provided file {args.config} does not exist")

        return get_plotting_data.parseConfig(args.config, args.data_folder)

    # TODO: custom type like with gaussian min and max?
    if args.max_event_count <= 0:
        parser.error(
            f"argument --max_event_count/-mc: invalid value: {args.max_event_count} " "(must be greater than 0)"
        )

    return get_plotting_data.EventChunkConfig(
        args.graph_type,
        args.data_folder,
        not args.show_figures,
        args.plot_variance,
        args.fwhm_multiplier,
        args.log_values,
        args.plot_fwhm,
        args.data_set_type,
        args.plot_constant,
        args.max_event_count,
        args.reconstruction_window,
        args.gaussian_min_y,
        args.gaussian_max_y,
    )


def clean_file_name(file_name: str, data_set_type: str) -> str:
    # Regex for name changes
    file_name_changes = {
        "Event Chunks": "",
        "no ?pol": "NoPolarizer",
        "30 ?deg": "",
        "15min": "",
        "1hz": "",
        "-+": " ",
        " +": " ",
    }

    for occurrence, replacement in file_name_changes.items():
        file_name = re.sub(occurrence, replacement, file_name)

    if data_set_type in ("frequency", "waveformsAndFrequency"):
        file_name = file_name.replace("foam ", "")
    else:
        # Remove frequency from folder name (why?)
        match = re.search("[0-9]+ ?[hH]z", file_name)
        if match is not None:
            file_name = file_name.replace(match[0], "")

    return file_name


def plot_bars(ax_var: np.ndarray, event_lists: List, labels: List, titles: List, title_extra: str) -> np.ndarray:
    if len(event_lists) != 6 or len(titles) != 6:
        raise ValueError("event_lists and titles parameters must have a length of 6")

    # Extend labels list to needed length
    if len(labels) == 2:
        labels.extend([labels[1], labels[1]])
        labels.insert(0, labels[0])
        labels.insert(0, labels[0])
    elif len(labels) == 1:
        for _ in range(5):
            labels.append(labels[0])
    else:
        raise ValueError("labels parameter must be of length 1 or 2")

    labels_iter = iter(labels)
    event_lists_iter = iter(event_lists)
    titles_iter = iter(titles)
    colors_iter = iter(["tab:blue", "tab:blue", "tab:blue", "red", "red", "red"])

    # Populate subplots
    for i in range(2):
        for j in range(3):
            ax_var[j][i].tick_params(axis="x", which="major", labelsize=10, labelrotation=35)
            axesVar[j][i].bar(next(labels_iter), next(event_lists_iter), color=next(colors_iter))
            axesVar[j][i].set_title(next(titles_iter) + title_extra)

    return ax_var


class OnOffBothLines:
    on: matplotlib.lines.Line2D = None
    off: matplotlib.lines.Line2D = None
    both: matplotlib.lines.Line2D = None


class OnOffBothFloat:
    on: float = None
    off: float = None
    both: float = None


class WaveformsLines:
    sine: List[OnOffBothLines] = []
    square: List[OnOffBothLines] = []
    burst: List[OnOffBothLines] = []
    triangle: List[OnOffBothLines] = []
    dc: List[OnOffBothLines] = []

    def __init__(self):
        self.sine = []
        self.square = []
        self.burst = []
        self.triangle = []

    def waveform_off_events_to_list(self, i: int) -> List:
        return [self.sine[i].off, self.square[i].off, self.burst[i].off, self.triangle[i].off]

    def waveform_on_events_to_list(self, i: int) -> List:
        return [self.sine[i].on, self.square[i].on, self.burst[i].on, self.triangle[i].on]

    def waveform_both_events_to_list(self, i: int) -> List:
        return [self.sine[i].both, self.square[i].both, self.burst[i].both, self.triangle[i].both]

    def single_motion_to_list(self, motion_pattern: str, event_type: str) -> List:
        if motion_pattern not in ["sine", "square", "burst", "triangle", "dc"]:
            raise ValueError("Error in single_motion_to_list. Unknown motion pattern")

        if event_type not in ["on", "off", "both"]:
            raise ValueError("Error in single_motion_to_list. Unknown event type")

        motion_list = getattr(self, motion_pattern)
        data = []

        for val in motion_list:
            data.append(getattr(val, event_type))

        return data


class WaveformsNumbers:
    sine: List[OnOffBothFloat] = []
    square: List[OnOffBothFloat] = []
    burst: List[OnOffBothFloat] = []
    triangle: List[OnOffBothFloat] = []
    dc: List[OnOffBothFloat] = []

    def __init__(self):
        self.sine = []
        self.square = []
        self.burst = []
        self.triangle = []

    def waveform_off_to_list(self, i: int) -> List:
        return [self.sine[i].off, self.square[i].off, self.burst[i].off, self.triangle[i].off]

    def waveform_on_to_list(self, i: int) -> List:
        return [self.sine[i].on, self.square[i].on, self.burst[i].on, self.triangle[i].on]

    def waveform_both_to_list(self, i: int) -> List:
        return [self.sine[i].both, self.square[i].both, self.burst[i].both, self.triangle[i].both]


# Make results directory if it doesn't exist
if not os.path.exists(os.path.join("results", "EventChunkGraphs")):
    os.makedirs(os.path.join("results", "EventChunkGraphs"))
    os.makedirs(os.path.join("results", "EventChunkGraphs", "Dots"))
elif not os.path.exists(os.path.join("results", "EventChunkGraphs", "Dots")):
    os.makedirs(os.path.join("results", "EventChunkGraphs", "Dots"))

offFrequencies = []
onFrequencies = []
bothFrequencies = []

offGuas = []
offLabel = []

onGuas = []
onLabel = []

bothGuas = []
bothLabel = []

saveFigures = True

# Variance Arrays
allOffVarPol: List[float] = []
allOnVarPol: List[float] = []
allBothVarPol: List[float] = []
allOffVarNoPol: List[float] = []
allOnVarNoPol: List[float] = []
allBothVarNoPol: List[float] = []
polLabels: List[float] = []
noPolLabels: List[float] = []

# FWHM Arrays
allOffFWHMPol = []
allOnFWHMPol = []
allBothFWHMPol = []
allOffFWHMNoPol = []
allOnFWHMNoPol = []
allBothFWHMNoPol = []

waveforms = WaveformsLines()
waveformsNoPolLines = WaveformsLines()
waveformsPolVariance = WaveformsNumbers()
waveformsNoPolVariance = WaveformsNumbers()
waveformsFWHM = WaveformsNumbers()
waveformsNoPolFWHM = WaveformsNumbers()

config = get_args()

# Get all csv files inside of the data folder
csv_paths = glob.glob(os.path.join("data", config.dataFolder, "**/*.csv"), recursive=True)
csv_paths = natsorted(csv_paths, alg=ns.IGNORECASE)

for csv_path in csv_paths:
    d: CsvData = get_plotting_data.read_aedat_csv(csv_path, config.reconstructionWindow, config.maxEventCount)

    if config.logValues:
        onAvg = np.array(d.y_on).mean()
        offAvg = np.array(d.y_off).mean()
        allAvg = np.array(d.y_all).mean()

        y_zip = zip(d.y_on, d.y_off, d.y_all)
        for i, (on_count, off_count, all_count) in enumerate(y_zip):
            if on_count == 0:
                d.y_on[i] = math.log10(onAvg)
            else:
                d.y_on[i] = math.log10(on_count)

            if off_count == 0:
                d.y_off[i] = math.log10(offAvg)
            else:
                d.y_off[i] = math.log10(off_count)

            if all_count == 0:
                d.y_all[i] = math.log10(allAvg)
            else:
                d.y_all[i] = math.log10(all_count)

    # Strip path and extension from the csv file. Will be used to name/save figures
    csv_filename = os.path.basename(csv_path)
    csv_filename = os.path.splitext(csv_filename)[0]

    csv_filename = clean_file_name(csv_filename, config.dataSetType)
    print(csv_filename)

    f, axes = plt.subplots(nrows=2, ncols=3, sharex=False, sharey=False)
    f.set_size_inches(15, 9.5)
    f.tight_layout()

    lines = OnOffBothLines()

    # Off events
    current_line = plotting_helper.plot_hist(d.y_off, axes, 1, 0, "red", config.logValues)
    current_line.remove()
    offGuas.append(current_line)
    lines.off = current_line

    # On Events
    current_line = plotting_helper.plot_hist(d.y_on, axes, 1, 1, "green", config.logValues)
    current_line.remove()
    onGuas.append(current_line)
    lines.on = current_line

    # On & Off Events
    current_line = plotting_helper.plot_hist(d.y_all, axes, 1, 2, "blue", config.logValues)
    current_line.remove()
    bothGuas.append(current_line)
    lines.both = current_line

    if config.dataSetType == "waveformsAndFrequency":
        if "NoPolarizer" in csv_filename:
            if "sine" in csv_filename:
                waveformsNoPolLines.sine.append(lines)
            elif "square" in csv_filename:
                waveformsNoPolLines.square.append(lines)
            elif "triangle" in csv_filename:
                waveformsNoPolLines.triangle.append(lines)
            elif "burst" in csv_filename:
                waveformsNoPolLines.burst.append(lines)
        else:
            if "sine" in csv_filename:
                waveforms.sine.append(lines)
            elif "square" in csv_filename:
                waveforms.square.append(lines)
            elif "triangle" in csv_filename:
                waveforms.triangle.append(lines)
            elif "burst" in csv_filename:
                waveforms.burst.append(lines)

    offLabel.append(csv_filename + " Off Events")
    onLabel.append(csv_filename + " On Events")
    bothLabel.append(csv_filename + " All Events")

    # Format & add data to scatter sub-plots
    axes[0][0].scatter(d.time_windows, d.y_off, c="red", picker=True, s=1)
    axes[1][0].title.set_text(csv_filename + " Off Events")
    axes[0][1].scatter(d.time_windows, d.y_on, c="green", picker=True, s=1)
    axes[1][1].title.set_text(csv_filename + " On Events")
    axes[0][2].scatter(d.time_windows, d.y_all, c="blue", picker=True, s=1)

    plt.title(csv_filename + " All Events")

    if "NoPolarizer" in csv_filename:
        noPolLabels.append(csv_filename.replace("NoPolarizer", ""))
    else:
        polLabels.append(csv_filename)

    if config.plotVariance:
        onOffBoth = OnOffBothFloat()
        onOffBoth.off = np.var(d.y_off)
        onOffBoth.on = np.var(d.y_on)
        onOffBoth.both = np.var(d.y_all)

        if "NoPolarizer" in csv_filename:
            if config.dataSetType == "waveformsAndFrequency":
                if "sine" in csv_filename:
                    waveformsNoPolVariance.sine.append(onOffBoth)
                elif "square" in csv_filename:
                    waveformsNoPolVariance.square.append(onOffBoth)
                elif "triangle" in csv_filename:
                    waveformsNoPolVariance.triangle.append(onOffBoth)
                elif "burst" in csv_filename:
                    waveformsNoPolVariance.burst.append(onOffBoth)
            else:
                allOffVarNoPol.append(np.var(d.y_off))
                allOnVarNoPol.append(np.var(d.y_on))
                allBothVarNoPol.append(np.var(d.y_all))
        else:
            if config.dataSetType == "waveformsAndFrequency":
                if "sine" in csv_filename:
                    waveformsPolVariance.sine.append(onOffBoth)
                elif "square" in csv_filename:
                    waveformsPolVariance.square.append(onOffBoth)
                elif "triangle" in csv_filename:
                    waveformsPolVariance.triangle.append(onOffBoth)
                elif "burst" in csv_filename:
                    waveformsPolVariance.burst.append(onOffBoth)
            else:
                allOffVarPol.append(np.var(d.y_off))
                allOnVarPol.append(np.var(d.y_on))
                allBothVarPol.append(np.var(d.y_all))

    if config.plotFWHM:
        # if FWHMmultiplier is 2.355 it will polt the FWHM
        # if is 1 it will plot the standard deviation
        onOffBoth = OnOffBothFloat()
        onOffBoth.off = config.FWHMMultiplier * np.std(d.y_off)
        onOffBoth.on = config.FWHMMultiplier * np.std(d.y_on)
        onOffBoth.both = config.FWHMMultiplier * np.std(d.y_all)

        if "NoPolarizer" in csv_filename:
            if config.dataSetType == "waveformsAndFrequency":
                if "sine" in csv_filename:
                    waveformsNoPolFWHM.sine.append(onOffBoth)
                elif "square" in csv_filename:
                    waveformsNoPolFWHM.square.append(onOffBoth)
                elif "triangle" in csv_filename:
                    waveformsNoPolFWHM.triangle.append(onOffBoth)
                elif "burst" in csv_filename:
                    waveformsNoPolFWHM.burst.append(onOffBoth)
            else:
                allOffFWHMNoPol.append(config.FWHMMultiplier * np.std(d.y_off))
                allOnFWHMNoPol.append(config.FWHMMultiplier * np.std(d.y_on))
                allBothFWHMNoPol.append(config.FWHMMultiplier * np.std(d.y_all))
        else:
            if config.dataSetType == "waveformsAndFrequency":
                if "sine" in csv_filename:
                    waveformsFWHM.sine.append(onOffBoth)
                elif "square" in csv_filename:
                    waveformsFWHM.square.append(onOffBoth)
                elif "triangle" in csv_filename:
                    waveformsFWHM.triangle.append(onOffBoth)
                elif "burst" in csv_filename:
                    waveformsFWHM.burst.append(onOffBoth)
            else:
                allOffFWHMPol.append(config.FWHMMultiplier * np.std(d.y_off))
                allOnFWHMPol.append(config.FWHMMultiplier * np.std(d.y_on))
                allBothFWHMPol.append(config.FWHMMultiplier * np.std(d.y_all))

    if saveFigures:
        plt.savefig(os.path.join("results", "EventChunkGraphs", "Dots", f"{csv_filename}Dots.png"))
        plt.close()


if not saveFigures:
    plt.show()

if config.dataSetType == "waveformsAndFrequency":
    if config.plotConstant == "waveforms":
        labels = ["Sine", "Square", "Burst", "Triangle"]
        labelsNoPol = ["Sine NoPolarizer", "Square NoPolarizer", "Burst NoPolarizer", "Triangle NoPolarizer"]
        speeds = ["200mV"]

        for i, speed in enumerate(speeds):
            f, axes = plt.subplots(nrows=3, ncols=2, sharex=False, sharey=False)
            f.set_size_inches(10, 15)

            offEvents = waveforms.waveform_off_events_to_list(i)
            onEvents = waveforms.waveform_on_events_to_list(i)
            bothEvents = waveforms.waveform_both_events_to_list(i)

            # FIXME: crashes if no unpol data in folder (too bad!)
            offEventsNoPol = waveformsNoPolLines.waveform_off_events_to_list(i)
            onEventsNoPol = waveformsNoPolLines.waveform_on_events_to_list(i)
            bothEventsNoPol = waveformsNoPolLines.waveform_both_events_to_list(i)

            plotting_helper.showAllGuas(offEvents, labels, 0, f"Off Events {speed}", axes, config)
            plotting_helper.showAllGuas(onEvents, labels, 1, f"On Events {speed}", axes, config)
            plotting_helper.showAllGuas(bothEvents, labels, 2, f"Combined Events {speed}", axes, config)

            plotting_helper.showAllGuas(offEventsNoPol, labelsNoPol, 0, f"Off Events {speed}", axes, config)
            plotting_helper.showAllGuas(onEventsNoPol, labelsNoPol, 1, f"On Events {speed}", axes, config)
            plotting_helper.showAllGuas(bothEventsNoPol, labelsNoPol, 2, f"Combined Events {speed}", axes, config)

            if saveFigures:
                plt.savefig(os.path.join("results", "EventChunkGraphs", f"showAllGuasWaveforms{speed}.png"))
                plt.close()
            else:
                plt.show()

            f, axes = plt.subplots(nrows=3, ncols=2, sharex=False, sharey=False)
            f.set_size_inches(10, 15)

            plotting_helper.centerAllGuas(offEvents, 0, labels, "Off Events", axes, config)
            plotting_helper.centerAllGuas(onEvents, 1, labels, "On Events", axes, config)
            plotting_helper.centerAllGuas(bothEvents, 2, labels, "Both Events", axes, config)

            plotting_helper.centerAllGuas(offEventsNoPol, 0, labelsNoPol, "Off Events", axes, config)
            plotting_helper.centerAllGuas(onEventsNoPol, 1, labelsNoPol, "On Events", axes, config)
            plotting_helper.centerAllGuas(bothEventsNoPol, 2, labelsNoPol, "Both Events", axes, config)

            if saveFigures:
                plt.savefig(os.path.join("results", "EventChunkGraphs", "CenterGaus.png"))
                plt.close()
            else:
                plt.show()
    else:
        labels = ["200mV", "300mV", "400mV", "500mV"]
        labelsNoPol = ["200mV NoPolarizer", "300mV NoPolarizer", "400mV NoPolarizer", "500mV NoPolarizer"]
        f, axes = plt.subplots(nrows=3, ncols=2, sharex=False, sharey=False)
        f.set_size_inches(10, 15)

        offEvents = waveforms.single_motion_to_list("sine", "off")
        onEvents = waveforms.single_motion_to_list("sine", "on")
        bothEvents = waveforms.single_motion_to_list("sine", "both")

        offEventsNoPol = waveformsNoPolLines.single_motion_to_list("sine", "off")
        onEventsNoPol = waveformsNoPolLines.single_motion_to_list("sine", "on")
        bothEventsNoPol = waveformsNoPolLines.single_motion_to_list("sine", "both")

        plotting_helper.showAllGuas(offEvents, labels, 0, "Off Events " + "Sine", axes, config)
        plotting_helper.showAllGuas(onEvents, labels, 1, "On Events " + "Sine", axes, config)
        plotting_helper.showAllGuas(bothEvents, labels, 2, "Combined Events " + "Sine", axes, config)

        plotting_helper.showAllGuas(offEventsNoPol, labelsNoPol, 0, "Off Events " + "Sine", axes, config)
        plotting_helper.showAllGuas(onEventsNoPol, labelsNoPol, 1, "On Events " + "Sine", axes, config)
        plotting_helper.showAllGuas(bothEventsNoPol, labelsNoPol, 2, "Combined Events " + "Sine", axes, config)

        if saveFigures:
            plt.savefig(os.path.join("results", "EventChunkGraphs", "showAllGuasFrequencySine.png"))
            plt.close()
        else:
            plt.show()
else:
    f, axes = plt.subplots(nrows=3, ncols=2, sharex=False, sharey=False)
    f.set_size_inches(10, 15)

    plotting_helper.showAllGuas(offGuas, offLabel, 0, "Off Events", axes, config)
    plotting_helper.showAllGuas(onGuas, onLabel, 1, "On Events", axes, config)
    plotting_helper.showAllGuas(bothGuas, bothLabel, 2, "Both Events", axes, config)

    if saveFigures:
        plt.savefig(os.path.join("results", "EventChunkGraphs", "Gaus.png"))
        plt.close()
    else:
        plt.show()

    f, axes = plt.subplots(nrows=3, ncols=2, sharex=False, sharey=False)
    f.set_size_inches(10, 15)

    plotting_helper.centerAllGuas(offGuas, 0, offLabel, "Off Events", axes, config)
    plotting_helper.centerAllGuas(onGuas, 1, onLabel, "On Events", axes, config)
    plotting_helper.centerAllGuas(bothGuas, 2, bothLabel, "Both Events", axes, config)

    if saveFigures:
        plt.savefig(os.path.join("results", "EventChunkGraphs", "CenterGaus.png"))
        plt.close()
    else:
        plt.show()

if config.plotVariance:
    if config.dataSetType == "waveformsAndFrequency":
        if config.plotConstant == "waveforms":
            labels = ["Sine", "Square", "Burst", "Triangle"]
            speeds = ["200mV"]
            for i, speed in enumerate(speeds):
                figureVar, axesVar = plt.subplots(nrows=3, ncols=2, sharex=False, sharey=False)
                figureVar.set_size_inches(10, 15)

                offEventsPol: List[float] = waveformsPolVariance.waveform_off_to_list(i)
                onEventsPol: List[float] = waveformsPolVariance.waveform_on_to_list(i)
                bothEventsPol: List[float] = waveformsPolVariance.waveform_both_to_list(i)

                offEventsNoPol: List[float] = waveformsNoPolVariance.waveform_off_to_list(i)
                onEventsNoPol: List[float] = waveformsNoPolVariance.waveform_on_to_list(i)
                bothEventsNoPol: List[float] = waveformsNoPolVariance.waveform_both_to_list(i)

                using_log_values = "Log" if config.logValues else ""

                axesVar = plot_bars(
                    axesVar,
                    [offEventsPol, onEventsPol, bothEventsPol, offEventsNoPol, onEventsNoPol, bothEventsNoPol],
                    [labels],
                    ["Off Events", "On Events", "Both Events", "Off Events Not", "On Events Not", "Both Events Not"],
                    f" Polarized Variance {speed} {using_log_values}",
                )

                plt.subplots_adjust(left=0.125, bottom=0.1, right=0.91, top=0.9, wspace=0.3, hspace=0.4)

                if saveFigures:
                    plt.savefig(os.path.join("results", "EventChunkGraphs", f"variance {speed}.png"))
                    plt.close()
                else:
                    plt.show()
    else:
        figureVar, axesVar = plt.subplots(nrows=3, ncols=2, sharex=False, sharey=False)
        figureVar.set_size_inches(10, 15)

        using_log_values = "Log" if config.logValues else ""

        axesVar = plot_bars(
            axesVar,
            [allOffVarPol, allOnVarPol, allBothVarPol, allOffVarNoPol, allOnVarNoPol, allBothVarNoPol],
            [polLabels, noPolLabels],
            ["Off Events", "On Events", "Both Events", "Off Events Not", "On Events Not", "Both Events Not"],
            f" Polarized Variance {using_log_values}",
        )

        plt.subplots_adjust(left=0.125, bottom=0.1, right=0.91, top=0.9, wspace=0.3, hspace=0.4)

        if saveFigures:
            plt.savefig(os.path.join("results", "EventChunkGraphs", "variance.png"))
            plt.close()
        else:
            plt.show()

if config.plotFWHM:
    figureVar, axesVar = plt.subplots(nrows=3, ncols=2, sharex=False, sharey=False)
    figureVar.set_size_inches(10, 15)

    logOrStandardDeviation = ("FWHM" if config.FWHMMultiplier == 2.355 else "Standard Deviation") + (
        " Log" if config.logValues else ""
    )

    if config.dataSetType == "waveformsAndFrequency":
        if config.plotConstant == "waveforms":
            speeds = ["200mV"]
            for i, speed in enumerate(speeds):
                labels = ["Sine", "Square", "Burst", "Triangle"]
                offEventsPol: List[float] = waveformsFWHM.waveform_off_to_list(i)
                onEventsPol: List[float] = waveformsFWHM.waveform_on_to_list(i)
                bothEventsPol: List[float] = waveformsFWHM.waveform_both_to_list(i)

                offEventsNoPol: List[float] = waveformsNoPolFWHM.waveform_off_to_list(i)
                onEventsNoPol: List[float] = waveformsNoPolFWHM.waveform_on_to_list(i)
                bothEventsNoPol: List[float] = waveformsNoPolFWHM.waveform_both_to_list(i)

                axesVar = plot_bars(
                    axesVar,
                    [offEventsPol, onEventsPol, bothEventsPol, offEventsNoPol, onEventsNoPol, bothEventsNoPol],
                    [labels],
                    ["Off Events", "On Events", "Both Events", "Off Events Not", "On Events Not", "Both Events Not"],
                    f" Polarized {logOrStandardDeviation}",
                )

                plt.subplots_adjust(left=0.125, bottom=0.1, right=0.91, top=0.9, wspace=0.3, hspace=0.4)

                if saveFigures:
                    plt.savefig(os.path.join("results", "EventChunkGraphs", f"{logOrStandardDeviation}{speed}.png"))
                    plt.close()
                else:
                    plt.show()
    else:
        axesVar = plot_bars(
            axesVar,
            [allOffFWHMPol, allOnFWHMPol, allBothFWHMPol, allOffFWHMNoPol, allOnFWHMNoPol, allBothFWHMNoPol],
            [polLabels, noPolLabels],
            ["Off Events", "On Events", "Both Events", "Off Events Not", "On Events Not", "Both Events Not"],
            f" Polarized {logOrStandardDeviation}",
        )

        plt.subplots_adjust(left=0.125, bottom=0.1, right=0.91, top=0.9, wspace=0.3, hspace=0.4)

        if saveFigures:
            plt.savefig(os.path.join("results", "EventChunkGraphs", f"{logOrStandardDeviation}.png"))
            plt.close()
        else:
            plt.show()

if not saveFigures:
    input()
