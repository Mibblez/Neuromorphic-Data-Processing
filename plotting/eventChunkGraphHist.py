import os
import re
import math
from typing import List

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from natsort import natsorted, ns

import getPlottingData
import plotting_helper

def clean_folder_name(folder_name: str, data_set_type: str) -> str:
    # TODO: regex in folder_name_changes for deg and min and stuff?
    folder_name_changes = {"Event Chunks" : "", "nopol" : "NoPolarizer", "no pol" : "NoPolarizer",
                           "30deg" : "", "30 deg" : "", "15min" : "", "1hz" : ""}

    for occurrence, replacement in folder_name_changes.items():
        folder_name = folder_name.replace(occurrence, replacement)

    if data_set_type in ('frequency', 'waveformsAndFrequency'):
        folder_name = folder_name.replace('foam ', '')
    else:
        # Remove frequency from folder name (why?)
        match = re.search("[0-9]{1,} ?hz", folder_name)
        if match is not None:
            folder_name = folder_name.replace(match, '')

    return folder_name

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
            ax_var[j][i].tick_params(axis='x', which='major', labelsize=10, labelrotation=35)
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

config = getPlottingData.parseConfig()

folders = os.listdir(os.path.join('data', config.dataFolder))
folders = natsorted(folders, alg=ns.IGNORECASE)

for folderName in folders:
    y_on, y_off, y_all, fileCount, x = getPlottingData.getData(
        os.path.join(config.dataFolder, folderName),
        config.reconstructionWindow,
        config.maxEventCount)

    if config.logValues:
        onAvg = np.array(y_on).mean()
        offAvg = np.array(y_off).mean()
        allAvg = np.array(y_all).mean()

        y_zip = zip(y_on, y_off, y_all)
        for i, (on_count, off_count, all_count) in enumerate(y_zip):
            if on_count == 0:
                y_on[i] = math.log10(onAvg)
            else:
                y_on[i] = math.log10(on_count)

            if off_count == 0:
                y_off[i] = math.log10(offAvg)
            else:
                y_off[i] = math.log10(off_count)

            if all_count == 0:
                y_all[i] = math.log10(allAvg)
            else:
                y_all[i] = math.log10(all_count)

    folderName = clean_folder_name(folderName, config.dataSetType)
    print(folderName)

    f, axes = plt.subplots(nrows=2, ncols=3, sharex=False, sharey=False)
    f.set_size_inches(15, 9.5)
    f.tight_layout()

    lines = OnOffBothLines()

    # Off events
    l = plotting_helper.plot_hist(y_off, axes, 1, 0, 'red', config.logValues)
    l.remove()
    offGuas.append(l)
    lines.off = l

    # On Events
    l = plotting_helper.plot_hist(y_on, axes, 1, 1, 'green', config.logValues)
    l.remove()
    onGuas.append(l)
    lines.on = l

    # On & Off Events
    l = plotting_helper.plot_hist(y_all, axes, 1, 2, 'blue', config.logValues)
    l.remove()
    bothGuas.append(l)
    lines.both = l

    if config.dataSetType == 'waveformsAndFrequency':
        if 'NoPolarizer' in folderName:
            if "sine" in folderName:
                waveformsNoPolLines.sine.append(lines)
            elif "square"  in folderName:
                waveformsNoPolLines.square.append(lines)
            elif "triangle" in folderName:
                waveformsNoPolLines.triangle.append(lines)
            elif "burst" in folderName:
                waveformsNoPolLines.burst.append(lines)
        else:
            if "sine" in folderName:
                waveforms.sine.append(lines)
            elif "square"  in folderName:
                waveforms.square.append(lines)
            elif "triangle" in folderName:
                waveforms.triangle.append(lines)
            elif "burst" in folderName:
                waveforms.burst.append(lines)

    offLabel.append(folderName + " Off Events")
    onLabel.append(folderName + " On Events")
    bothLabel.append(folderName + " All Events")

    # Format & add data to scatter sub-plots
    axes[0][0].scatter(x, y_off, c='red', picker=True, s=1)
    axes[1][0].title.set_text(folderName +" Off Events")
    axes[0][1].scatter(x, y_on, c='green', picker=True, s=1)
    axes[1][1].title.set_text(folderName +" On Events")
    axes[0][2].scatter(x, y_all, c='blue', picker=True, s=1)

    plt.title(folderName +" All Events")

    if 'NoPolarizer' in folderName:
        noPolLabels.append(folderName.replace("NoPolarizer", ""))
    else:
        polLabels.append(folderName)

    if config.plotVariance:
        onOffBoth = OnOffBothFloat()
        onOffBoth.off = np.var(y_off)
        onOffBoth.on = np.var(y_on)
        onOffBoth.both = np.var(y_all)

        if 'NoPolarizer' in folderName:
            if config.dataSetType == 'waveformsAndFrequency':
                if "sine" in folderName:
                    waveformsNoPolVariance.sine.append(onOffBoth)
                elif "square"  in folderName:
                    waveformsNoPolVariance.square.append(onOffBoth)
                elif "triangle" in folderName:
                    waveformsNoPolVariance.triangle.append(onOffBoth)
                elif "burst" in folderName:
                    waveformsNoPolVariance.burst.append(onOffBoth)
            else:
                allOffVarNoPol.append(np.var(y_off))
                allOnVarNoPol.append(np.var(y_on))
                allBothVarNoPol.append(np.var(y_all))
        else:
            if config.dataSetType == 'waveformsAndFrequency':
                if "sine" in folderName:
                    waveformsPolVariance.sine.append(onOffBoth)
                elif "square"  in folderName:
                    waveformsPolVariance.square.append(onOffBoth)
                elif "triangle" in folderName:
                    waveformsPolVariance.triangle.append(onOffBoth)
                elif "burst" in folderName:
                    waveformsPolVariance.burst.append(onOffBoth)
            else:
                allOffVarPol.append(np.var(y_off))
                allOnVarPol.append(np.var(y_on))
                allBothVarPol.append(np.var(y_all))

    if config.plotFWHM:
        # if FWHMmultiplier is 2.355 it will polt the FWHM
        # if is 1 it will plot the standard deviation
        onOffBoth = OnOffBothFloat()
        onOffBoth.off = config.FWHMMultiplier * np.std(y_off)
        onOffBoth.on = config.FWHMMultiplier * np.std(y_on)
        onOffBoth.both = config.FWHMMultiplier * np.std(y_all)

        if 'NoPolarizer' in folderName:
            if config.dataSetType == 'waveformsAndFrequency':
                if "sine" in folderName:
                    waveformsNoPolFWHM.sine.append(onOffBoth)
                elif "square"  in folderName:
                    waveformsNoPolFWHM.square.append(onOffBoth)
                elif "triangle" in folderName:
                    waveformsNoPolFWHM.triangle.append(onOffBoth)
                elif "burst" in folderName:
                    waveformsNoPolFWHM.burst.append(onOffBoth)
            else:
                allOffFWHMNoPol.append(config.FWHMMultiplier * np.std(y_off))
                allOnFWHMNoPol.append(config.FWHMMultiplier * np.std(y_on))
                allBothFWHMNoPol.append(config.FWHMMultiplier * np.std(y_all))
        else:
            if config.dataSetType == 'waveformsAndFrequency':
                if "sine" in folderName:
                    waveformsFWHM.sine.append(onOffBoth)
                elif "square"  in folderName:
                    waveformsFWHM.square.append(onOffBoth)
                elif "triangle" in folderName:
                    waveformsFWHM.triangle.append(onOffBoth)
                elif "burst" in folderName:
                    waveformsFWHM.burst.append(onOffBoth)
            else:
                allOffFWHMPol.append(config.FWHMMultiplier * np.std(y_off))
                allOnFWHMPol.append(config.FWHMMultiplier * np.std(y_on))
                allBothFWHMPol.append(config.FWHMMultiplier * np.std(y_all))

    if saveFigures:
        plt.savefig(os.path.join("results", "EventChunkGraphs", "Dots", f"{folderName}Dots.png"))
        plt.close()


if not saveFigures:
    plt.show()

if config.dataSetType == 'waveformsAndFrequency':
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
                plt.savefig(os.path.join("results", "EventChunkGraphs", 'CenterGaus.png'))
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
            plt.savefig(os.path.join("results", "EventChunkGraphs", 'showAllGuasFrequencySine.png'))
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
        plt.savefig(os.path.join("results", "EventChunkGraphs", 'Gaus.png'))
        plt.close()
    else:
        plt.show()

    f, axes = plt.subplots(nrows=3, ncols=2, sharex=False, sharey=False)
    f.set_size_inches(10, 15)

    plotting_helper.centerAllGuas(offGuas, 0, offLabel, "Off Events", axes, config)
    plotting_helper.centerAllGuas(onGuas, 1, onLabel, "On Events", axes, config)
    plotting_helper.centerAllGuas(bothGuas, 2, bothLabel, "Both Events", axes, config)

    if saveFigures:
        plt.savefig(os.path.join("results", "EventChunkGraphs", 'CenterGaus.png'))
        plt.close()
    else:
        plt.show()

if config.plotVariance:
    if config.dataSetType == 'waveformsAndFrequency':
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

                axesVar = plot_bars(axesVar,
                                    [offEventsPol, onEventsPol, bothEventsPol, offEventsNoPol, onEventsNoPol, bothEventsNoPol],
                                    [labels],
                                    ["Off Events", "On Events", "Both Events", "Off Events Not", "On Events Not", "Both Events Not"],
                                    f" Polarized Variance {speed} {using_log_values}")

                plt.subplots_adjust(left=.125, bottom=0.1, right=.91, top=.9, wspace=.3, hspace=.4)

                if saveFigures:
                    plt.savefig(os.path.join("results", "EventChunkGraphs", f"variance {speed}.png"))
                    plt.close()
                else:
                    plt.show()
    else:
        figureVar, axesVar = plt.subplots(nrows=3, ncols=2, sharex=False, sharey=False)
        figureVar.set_size_inches(10, 15)

        using_log_values = "Log" if config.logValues else ""

        axesVar = plot_bars(axesVar,
                            [allOffVarPol, allOnVarPol, allBothVarPol, allOffVarNoPol, allOnVarNoPol, allBothVarNoPol],
                            [polLabels, noPolLabels],
                            ["Off Events", "On Events", "Both Events", "Off Events Not", "On Events Not", "Both Events Not"],
                            f" Polarized Variance {using_log_values}")

        plt.subplots_adjust(left=.125, bottom=0.1, right=.91, top=.9, wspace=.3, hspace=.4)

        if saveFigures:
            plt.savefig(os.path.join("results", "EventChunkGraphs", "variance.png"))
            plt.close()
        else:
            plt.show()

if config.plotFWHM:
    figureVar, axesVar = plt.subplots(nrows=3, ncols=2, sharex=False, sharey=False)
    figureVar.set_size_inches(10, 15)

    logOrStandardDeviation = ("FWHM" if config.FWHMMultiplier == 2.355 else "Standard Deviation") + (" Log" if config.logValues else "")

    if config.dataSetType == 'waveformsAndFrequency':
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

                axesVar = plot_bars(axesVar,
                                    [offEventsPol, onEventsPol, bothEventsPol, offEventsNoPol, onEventsNoPol, bothEventsNoPol],
                                    [labels],
                                    ["Off Events", "On Events", "Both Events", "Off Events Not", "On Events Not", "Both Events Not"],
                                    f" Polarized {logOrStandardDeviation}")

                plt.subplots_adjust(left=.125, bottom=0.1, right=.91, top=.9, wspace=.3, hspace=.4)

                if saveFigures:
                    plt.savefig(os.path.join("results", "EventChunkGraphs", f"{logOrStandardDeviation}{speed}.png"))
                    plt.close()
                else:
                    plt.show()
    else:
        axesVar = plot_bars(axesVar,
                            [allOffFWHMPol, allOnFWHMPol, allBothFWHMPol, allOffFWHMNoPol, allOnFWHMNoPol, allBothFWHMNoPol],
                            [polLabels, noPolLabels],
                            ["Off Events", "On Events", "Both Events", "Off Events Not", "On Events Not", "Both Events Not"],
                            f" Polarized {logOrStandardDeviation}")

        plt.subplots_adjust(left=.125, bottom=0.1, right=.91, top=.9, wspace=.3, hspace=.4)

        if saveFigures:
            plt.savefig(os.path.join("results", "EventChunkGraphs", f"{logOrStandardDeviation}.png"))
            plt.close()
        else:
            plt.show()

if not saveFigures:
    input()
