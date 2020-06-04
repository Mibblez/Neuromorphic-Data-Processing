import os
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import getPlottingData

hz = 40
folder_name = f"no_pol/Front{hz}_Rear0 Event Chunks"
plot_name = f"{hz}hz Not Polarized Fingerprint (1200μs Reconstruction Window)"
save_fig = True
show_fig = False

config = getPlottingData.parseConfig()
plot_data = getPlottingData.getData(os.path.join(config.dataFolder, folder_name), config.reconstructionWindow, config.maxEventCount)

all_event_counts = plot_data[2]
x = plot_data[4]

plt.title(plot_name)
plt.plot(x, all_event_counts, '-o', markersize=4)

plt.yscale('log', basey=10)

ax = plt.gca()

ax.yaxis.set_major_formatter(ScalarFormatter())
ax.yaxis.set_minor_formatter(mticker.ScalarFormatter())

plt.xlabel('Time (seconds)')
plt.ylabel('Event Count')

plt.gcf().set_size_inches((10, 4.5))

if save_fig:
    plt.savefig(os.path.join(f'{plot_name}.png'))

if show_fig:
    plt.show()
