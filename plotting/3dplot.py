"""
3D Plots are a visual display of events over time.
X/Y Axis: Event Position
Z Axis: time

CSV Format: On/Off,X,Y,Timestamp
"""

import argparse
import os
import csv
import itertools

import matplotlib.pyplot as plt

import getPlottingData

file_to_plot = ''
view = None

def get_args():
    global file_to_plot, view

    parser = argparse.ArgumentParser()

    parser.add_argument("aedat_csv_file", help='CSV containing AEDAT data to be plotted', type=str)
    parser.add_argument('--view_angle', '-v', help='sets plot viewing angle [default, top, side, all]', action='store', type=str)

    args = parser.parse_args()

    file_to_plot = args.aedat_csv_file

    viewing_angles = ['default', 'top', 'side', 'all']

    if args.view_angle is not None:
        view = args.view_angle.lower()
        if view not in viewing_angles:
            quit('Invalid view. Use one of the following: [default, top, side, all]')
    else:
        print('usage: 3dplot.py [-h] [--view_angle VIEW_ANGLE] aedat_csv_file')
        print('3dplot.py: error: the following arguments are required: view_angle')
        quit('Use one of the following view angles: [default, top, side, all]')


if __name__ == '__main__':
    get_args()
    events = getPlottingData.get_spatial_csv_data(file_to_plot)

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
    fig.set_size_inches(12, 10)
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('X Position')
    ax.set_ylabel('Y Position')
    ax.set_zlabel('Time (μs)')

    file_name = os.path.basename(os.path.normpath(file_to_plot))    # Get file at end of path
    file_name = os.path.splitext(file_name)[0]                      # Strip off file extension

    if view in ['default', 'all']:
        ax.scatter(all_x, all_y, all_time, c=color, marker='.', s=4, depthshade=False)

        fig.savefig(os.path.join(f'3D_Plot-{file_name}-default.png'), bbox_inches='tight', pad_inches=0)


    if view in ['side', 'all']:
        ax.scatter(all_x, all_y, all_time, c=color, marker='H', s=4, depthshade=False)
        ax.view_init(azim=0, elev=8)

        fig.savefig(os.path.join(f'3D_Plot-{file_name}-side.png'), bbox_inches='tight', pad_inches=0)


    if view in ['top', 'all']:
        ax.scatter(all_x, all_y, all_time, c=color, marker='H', s=4, depthshade=False)
        ax.set_zticklabels([])
        ax.view_init(azim=-90, elev=87)

        fig.savefig(os.path.join(f'3D_Plot-{file_name}-top.png'), bbox_inches='tight', pad_inches=0)

    plt.clf()
