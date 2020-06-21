"""
Fingerprint graphs are a visual display of event counts over time.
Y Axis: event counts in a time window
X Axis: time

CSV Format: on,off,both
"""

import os
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import getPlottingData

plot_xlim = 1.05
save_fig = False # Save figure if true, else show plot

def plot_event_count(event_counts: list, t: list, line_color: str, plot_title: str):
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
    count_range = max(event_counts) - min(event_counts)
    major_spacing = round((count_range / 5), -1)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(major_spacing))
    ax.yaxis.set_minor_locator(mticker.MultipleLocator(major_spacing / 2))

    # Plot lines with circles on the points
    plt.plot(t, event_counts, '-o', markersize=4, c=line_color)

    ax.set_xlim([0, plot_xlim])

    plt.gcf().set_size_inches((11, 4.5))

    if save_fig:
        plt.savefig(os.path.join(f'{plot_title}.png'))
    else:
        plt.show()

hz = 40
folder_name = f"no_pol/Front{hz}_Rear0 Event Chunks"

config = getPlottingData.parseConfig()
plot_data = getPlottingData.getData(os.path.join(config.dataFolder, folder_name),
                                    config.reconstructionWindow, config.maxEventCount)

on_event_counts = plot_data[0]
off_event_counts = plot_data[1]
both_event_counts = plot_data[2]
time = plot_data[4]

plot_event_count(off_event_counts, time, 'r',
                 f"{hz}hz Not Polarized OFF Events Fingerprint ({config.reconstructionWindow}μs Reconstruction Window)")
plot_event_count(on_event_counts, time, 'g',
                 f"{hz}hz Not Polarized ON Events Fingerprint ({config.reconstructionWindow}μs Reconstruction Window)")
plot_event_count(both_event_counts, time, 'b',
                 f"{hz}hz Not Polarized Both Events Fingerprint ({config.reconstructionWindow}μs Reconstruction Window)")
