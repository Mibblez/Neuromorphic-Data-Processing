from os import listdir
from os.path import isfile, join
import argparse
import os
import csv

import matplotlib.pyplot as plt

show_plot = True
save_fig = False
file_to_plot = ''
view = None

def get_event_chunk_data(csv_file):
    points = []
    first_timestamp = 0

    with open(csv_file, 'r') as csvfile:
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

def get_args():
    global show_plot, save_fig, file_to_plot, view

    parser = argparse.ArgumentParser()

    parser.add_argument("aedat_csv_file", help='CSV containing AEDAT data to be plotted', type=str)
    parser.add_argument('--hide_plot', '-hp', help='prevents the plot from being shown', action='store_true')
    parser.add_argument('--save_fig', '-sf', help='saves the figure to disk', action='store_true')
    parser.add_argument('--view_angle', '-v', help='sets plot viewing angle [default, top, side]', action='store', type=str)

    args = parser.parse_args()

    show_plot = not args.hide_plot
    save_fig = args.save_fig
    file_to_plot = args.aedat_csv_file

    viewing_angles = ['default', 'top', 'side']

    if args.view_angle is not None:
        view = args.view_angle.lower()
        if view not in viewing_angles:
            print('Invalid view. Using default instead.')


if __name__ == '__main__':
    get_args()
    events = get_event_chunk_data(file_to_plot)

    all_x = []
    all_y = []
    all_time = []
    color = []

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
    ax.set_xlabel('X Position')
    ax.set_ylabel('Y Position')
    ax.set_zlabel('Time (μs)')

    if view == 'top':
        ax.scatter(all_x, all_y, all_time, c=color, marker='H', s=4, depthshade=False)
        ax.set_zticklabels([])
        ax.view_init(azim=-90, elev=87)
    elif view == 'side':
        ax.scatter(all_x, all_y, all_time, c=color, marker='H', s=4, depthshade=False)
        ax.view_init(azim=0, elev=8)
    else:
        ax.scatter(all_x, all_y, all_time, c=color, marker='.', s=4, depthshade=False)

    fig.set_size_inches(12, 10)

    file_name = os.path.basename(os.path.normpath(file_to_plot))    # Get file at end of path
    file_name = os.path.splitext(file_name)[0]                      # Strip off file extension

    if save_fig:
        plt.savefig(os.path.join(f'3D_Plot-{file_name}.png'))

    if show_plot:
        plt.show()
    else:
        plt.clf()
