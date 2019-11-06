from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import csv
from os import walk
from os import listdir
from os.path import isfile, join

def getEventChunkData(folderName):
    points = []
    first_timestamp = 0

    onlyfiles = [f for f in listdir("./eventChunkData/" + folderName) if isfile(join("./eventChunkData/" + folderName, f))]
    for file in onlyfiles:
        with open('./eventChunkData/'+folderName+"/" +file, 'r') as csvfile:
            
            reader = csv.reader(csvfile, delimiter=',')
            
            for i, row in enumerate(reader):

                # Skip header
                if i == 0:
                    continue

                if i == 1 and first_timestamp == 0:
                    first_timestamp = int(row[3])

                polarity = True if row[0] == "True" else False
                x_pos = int(row[1])
                y_pos = 128 - int(row[2])
                timestamp = int(row[3]) - first_timestamp

                points.append([polarity, x_pos, y_pos, timestamp])

    return points

events = getEventChunkData("coarse-12hz-30deg-Event-Chunks")

all_x = []
all_y = []
all_time = []
color= []

for event in events:
    all_x.append(event[1])
    all_y.append(event[2])
    all_time.append(event[3])
    if event[0] is True:
        color.append("g")
    else:
        color.append("r")



fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(all_x, all_y, all_time, c=color, marker='.', s=3, depthshade=False)

ax.set_xlabel('X Position')
ax.set_ylabel('Y Position')
ax.set_zlabel('Time (μs)')

fig.set_size_inches(12, 10)

plt.show()
