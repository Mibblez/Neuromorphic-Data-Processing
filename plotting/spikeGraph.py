"""
Spike graphs are a record of the acivity of a single pixel or a group of pixels.
Y Axis: ON events correspond to +1 and OFF events correspond to -1
X Axis: Time

CSV Format: on/off,x,y,timestamp
"""
import csv
from itertools import islice
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import math
import sys
import argparse
import os
import itertools
import re

file_to_plot = ''

def get_args():
    global file_to_plot

    parser = argparse.ArgumentParser()
    parser.add_argument("aedat_csv_file", help='CSV containing AEDAT data to be plotted', type=str)
    args = parser.parse_args()

    file_to_plot = args.aedat_csv_file

    if not os.path.exists(file_to_plot):
        quit(f'File does not exist: {file_to_plot}')

def get_activity_area(csv_file, pixel_x: int, pixel_y: int, area_size: int, max_points: int=sys.maxsize, time_limit: float=math.inf):
    points = []
    first_timestamp = 0

    with open(csv_file, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None) # Skip header

        first_row = next(reader, None)
        first_timestamp = int(first_row[3])

        if time_limit != math.inf:
            time_limit = time_limit * 1000000   # Convert to microseconds

        for row in itertools.chain([first_row], reader):
            x_pos = int(row[1])
            y_pos = 128 - int(row[2])

            timestamp = float(int(row[3]) - first_timestamp)
            if timestamp > time_limit:
                return points

            check_x = abs(x_pos - pixel_x)
            check_y = abs(y_pos - pixel_y)

            # Check if this event is inside the specified area
            if check_x < area_size and check_y < area_size:
                if row[0] in ['1', 'True']:
                    points.append([1, timestamp])
                else:
                    points.append([-1, timestamp])
                
                if len(points) == max_points:
                    return points

    return points

def get_activity_global(csv_file, max_points: int=sys.maxsize, time_limit: float=math.inf):
    points = []
    first_timestamp = 0

    with open(csv_file, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None) # Skip header

        first_row = next(reader, None)
        first_timestamp = int(first_row[3])

        if time_limit != math.inf:
            time_limit = time_limit * 1000000   # Convert to microseconds

        for row in itertools.chain([first_row], reader):
            timestamp = float(int(row[3]) - first_timestamp)
            if timestamp > time_limit:
                return points

            if row[0] in ['1', 'True']:
                points.append([1, timestamp])
            else:
                points.append([-1, timestamp])
            
            if len(points) == max_points:
                    return points

    return points

if __name__ == '__main__':
    get_args()
    
    file_path = file_to_plot
    
    points = get_activity_area(file_path, 30, 75, 4, time_limit=0.25)
    #points = get_activity_global(file_to_plot, time_limit=0.01)

    # Add lines to plot
    for point in points:
        timestamp_seconds = point[1] / 1000000  # Convert to seconds
        color = ''
        if point[0] == 1:
            color = 'g'
        else:
            color = 'r'
        plt.plot([timestamp_seconds, timestamp_seconds], [0, point[0]], color) # Add to points at the same X value to make vertical lines

    plt.ylim(-1.1, 1.1)

    hz = re.search("[0-9]{1,} ?Hz", file_path)
    hz = hz.group()

    title = hz
    if re.search('no ?pol', file_path):
        title = title + " Unpolarized"
    else:
        title = title + " Polarized"

    plt.title(title)
    plt.xlabel('Time (Seconds)')

    plt.gcf().set_size_inches((11, 4.5))

    ax = plt.gca() # Get axis

    # Set Y-axis tick spacing
    ax.yaxis.set_major_locator(mticker.MultipleLocator(1))

    # Increase X and Y tick size
    ax.tick_params(axis='both', which='major', labelsize=12)

    plt.axhline(0, color='black')

    # Get file name from path and remove extension
    file_name = os.path.basename(file_path)
    file_name = os.path.splitext(file_name)[0]

    plt.savefig(os.path.join(f'spike_Plot-{file_name}.png'), bbox_inches='tight', pad_inches=0)
