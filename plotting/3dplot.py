from os import listdir
from os.path import isfile, join
import argparse
import os
import csv

import matplotlib.pyplot as plt

show_plot = True
save_fig = False
folder_to_plot = ''

def get_event_chunk_data(folder):
    points = []
    first_timestamp = 0

    only_files = [f for f in listdir(folder) if isfile(join(folder, f))]
    for file in only_files:
        with open(os.path.join(folder, file), 'r') as csvfile:
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
    global show_plot, save_fig, folder_to_plot, view

    parser = argparse.ArgumentParser()

    parser.add_argument("folder", help='folder containing event chunks to be plotted', type=str)
    parser.add_argument('--hide_plot', '-hp', help='prevents the plot from being shown', action='store_true')
    parser.add_argument('--save_fig', '-sf', help='saves the figure to disk', action='store_true')
    parser.add_argument('--view', '-v', help='sets plot viewing angle [default, top, side]', action='store', type=str)

    args = parser.parse_args()

    show_plot = not args.hide_plot
    save_fig = args.save_fig
    folder_to_plot = args.folder

    viewing_angles = ['default', 'top', 'side']
    view = args.view.lower()

    if view is not None and view not in viewing_angles:
        print('Invalid view. Using default instead.')
        view = None


if __name__ == '__main__':
    get_args()
    events = get_event_chunk_data(folder_to_plot)

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
    ax.scatter(all_x, all_y, all_time, c=color, marker='.', s=3, depthshade=False)

    ax.set_xlabel('X Position')
    ax.set_ylabel('Y Position')
    ax.set_zlabel('Time (μs)')

    if view == 'top':
        ax.set_zticklabels([])
        ax.view_init(azim=-90, elev=90)
    elif view == 'side':
        ax.view_init(azim=0, elev=8)

    fig.set_size_inches(12, 10)

    folder_name = os.path.basename(os.path.dirname(folder_to_plot))

    if save_fig:
        plt.savefig(os.path.join(f'3D_Plot-{folder_name}.png'))

    if show_plot:
        plt.show()
    else:
        plt.clf()
