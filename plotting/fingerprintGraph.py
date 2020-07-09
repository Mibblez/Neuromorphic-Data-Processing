"""
Fingerprint graphs are a visual display of event counts over time.
Y Axis: event counts in a time window
X Axis: time

CSV Format: on,off,both
"""

import os
import re
import argparse
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import getPlottingData
from getPlottingData import CsvData

file_to_plot = ''
x_lim = -1

def get_args():
    global file_to_plot, x_lim

    parser = argparse.ArgumentParser()
    parser.add_argument("aedat_csv_file", help='CSV containing AEDAT data to be plotted', type=str)
    parser.add_argument("--plot_xlim", '-x', help='Limit on the X-axis (seconds)', type=float)
    args = parser.parse_args()

    file_to_plot = args.aedat_csv_file

    if not os.path.exists(file_to_plot):
        quit(f'File does not exist: {file_to_plot}')
    elif os.path.isdir(file_to_plot):
        quit(f"'{file_to_plot}' is a directory. It should be a csv file")
    
    x_lim = args.plot_xlim

    if x_lim is not None and x_lim <= 0:
        quit('The argument --plot_xlim/-x must be greater than 0')

def plot_event_count(event_counts: list, t: list, line_color: str, plot_xlim: float, plot_title: str, save_fig: bool=True):
    plt.clf()

    plt.title(plot_title)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Event Count')

    plt.yscale('log', basey=10) # Use a log scale

    ax = plt.gca() # Get axis
    plt.grid()

    # Ensure that Y-axis ticks are displayed as whole numbers
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.yaxis.set_minor_formatter(mticker.NullFormatter())   # Disable minor tick markers

    # Set Y-axis tick spacing
    try:
        count_range = max(event_counts) - min(event_counts)
        major_spacing = round((count_range / 5), -1)
        ax.yaxis.set_major_locator(mticker.MultipleLocator(major_spacing))
        ax.yaxis.set_minor_locator(mticker.MultipleLocator(major_spacing / 2))
    except ValueError:
        print("WARNING: Could not set tick spacing. No events present?")

    # Plot lines with circles on the points
    plt.plot(t, event_counts, '-o', markersize=4, c=line_color)

    if x_lim != -1:
        ax.set_xlim([0, plot_xlim])

    plt.gcf().set_size_inches((11, 4.5))

    if save_fig:
        plt.savefig(os.path.join(f'{plot_title}.png'))
    else:
        plt.show()

if __name__ == '__main__':
    get_args()

    hz = ""
    voltage = ""
    waveform_type = ""
    degrees = ""

    file_name = os.path.basename(file_to_plot)

    # Try to grab frequency from filename
    try:
        hz = re.search("[0-9]{1,} ?[H|h][Z|z]", file_name)
        hz = hz.group()
    except AttributeError:
        hz = ""
    
    # Try to grab voltage from filename
    try:
        voltage = re.search('(\d+(?:\.\d+)?) ?v', file_name, re.IGNORECASE).group() + " "
    except AttributeError:
        voltage = ""
    
    # Try to grab waveform type from filename
    try:
        waveform_type = re.search('(burst|sine|square|triangle|noise)', file_name, re.IGNORECASE).group() + " "
    except AttributeError:
        waveform_type = ""
    
    # Try to grab polarizer angle from filename
    try:
        degrees = re.search("[0-9]{1,} ?deg", file_name, re.IGNORECASE).group()
        degrees = re.search("[0-9]{1,}", degrees).group()
        degrees = " " + degrees + " Degrees Polarized"
    except AttributeError:
        degrees = ""
    
    if hz == "" and degrees == "":
        print("WARNING: Could not infer polarizer angle or frequency from file name")

    config = getPlottingData.parseConfig()

    plot_data: CsvData = getPlottingData.read_aedat_csv(file_to_plot, 
                                                        config.reconstructionWindow,
                                                        config.maxEventCount)

    plot_event_count(plot_data.y_off, plot_data.time_windows, 'r', x_lim,
                    f"{waveform_type}{voltage}{hz}{degrees} OFF Events Fingerprint ({config.reconstructionWindow}μs Reconstruction Window)")
    plot_event_count(plot_data.y_on, plot_data.time_windows, 'g', x_lim,
                    f"{waveform_type}{voltage}{hz}{degrees} ON Events Fingerprint ({config.reconstructionWindow}μs Reconstruction Window)")
    plot_event_count(plot_data.y_all, plot_data.time_windows, 'b',x_lim,
                    f"{waveform_type}{voltage}{hz}{degrees} All Events Fingerprint ({config.reconstructionWindow}μs Reconstruction Window)")
