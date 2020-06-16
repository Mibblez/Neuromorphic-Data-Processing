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

hz = 40
folder_name = f"pol/Front{hz}_Rear0_1P336_2P254 Event Chunks"
plot_name = f"{hz}hz Polarized OFF Events Fingerprint (1200μs Reconstruction Window)"

save_fig = True # Save figure if true, else show plot

config = getPlottingData.parseConfig()
plot_data = getPlottingData.getData(os.path.join(config.dataFolder, folder_name), config.reconstructionWindow, config.maxEventCount)

on_event_counts = plot_data[0]
off_event_counts = plot_data[1]
all_event_counts = plot_data[2]

# Time
x = plot_data[4]

plt.title(plot_name)
plt.plot(x, off_event_counts, '-o', markersize=4, c='r') # Plot lines with circles on the points

plt.yscale('log', basey=10)

ax = plt.gca() # Get axis

# Ensure that Y axis ticks are displayed as whole numbers
ax.yaxis.set_major_formatter(ScalarFormatter())
ax.yaxis.set_minor_formatter(mticker.ScalarFormatter())

plt.xlabel('Time (seconds)')
plt.ylabel('Event Count')

plt.gcf().set_size_inches((10, 4.5))

if save_fig:
    plt.savefig(os.path.join(f'{plot_name}.png'))
else:
    plt.show()
