import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from matplotlib import pyplot
import matplotlib
from matplotlib.ticker import ScalarFormatter, FormatStrFormatter
import getPlottingData
import os
from os import walk
from os import listdir
from os.path import isfile, join
import matplotlib.ticker as mticker

# TODO: automatically streatch graph along x-axis 
folderName = "5hz Pol (1200 Reconstruction Window)"
config = getPlottingData.parseConfig()
test =  getPlottingData.getData(os.path.join(config.dataFolder,folderName), config.reconstructionWindow, config.maxEventCount)

all_event_counts = test[2]
x = test[4]

plt.title(folderName)
plt.plot(x, all_event_counts, '-o')

pyplot.yscale('log', basey=10)

ax = plt.gca()

ax.yaxis.set_major_formatter(ScalarFormatter())
ax.yaxis.set_minor_formatter(mticker.ScalarFormatter())

plt.xlabel('Time (seconds)')
plt.ylabel('Event Count')

plt.show()