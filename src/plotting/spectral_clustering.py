import argparse
import os
import sys

from sklearn.cluster import SpectralClustering
import numpy as np
import plotting_utils.get_plotting_data as get_plotting_data
from plotting_utils.get_plotting_data import DataStorage

import matplotlib
import matplotlib.pyplot as plt

file_to_plot = ""
num_clusters = 6
max_time = -1
save_directory = ""


def get_args():
    global file_to_plot, num_clusters, max_time, save_directory

    parser = argparse.ArgumentParser()

    parser.add_argument("aedat_csv_file", help="CSV containing AEDAT data to be plotted", type=str)
    parser.add_argument(
        "--num_clusters", "-c", help="Sets number of clusters, defaulted to 6", action="store", type=int
    )
    parser.add_argument("--max_time", "-t", help="Max time in microseconds", type=float)
    parser.add_argument("--save_directory", "-d", help="Save file to directory", type=str)

    args = parser.parse_args()

    if args.save_directory is not None:
        if not os.path.exists(args.save_directory):
            sys.exit(f'Error: Specified path "{args.save_directory}" does not exist')
        else:
            save_directory = args.save_directory

    if args.num_clusters is not None:
        if args.num_clusters <= 1:
            parser.print_help()
            sys.exit("Error: Invalid clustering argument. Please provide a number greater than or equal to 2")
        else:
            num_clusters = args.num_clusters

    if args.max_time is not None:
        if args.max_time <= 0:
            parser.print_help()
            sys.exit("Error: Invalid max time. Please provide a positive number")
        else:
            max_time = args.max_time * (10**-6)
    else:
        parser.print_help()
        sys.exit("Error: Max time argument is required")

    file_to_plot = args.aedat_csv_file


if __name__ == "__main__":
    get_args()
    matplotlib.use("Qt5Agg")

    data = get_plotting_data.SpatialCsvData.from_csv(file_to_plot, DataStorage.NONE, max_time)

    # Transform X and Y positions into the correct format for this plot -> [[X,Y], [X,Y], ...]
    plot_points = np.asarray(list(zip(data.x_positions, data.y_positions)))

    model = SpectralClustering(
        n_clusters=num_clusters, assign_labels="cluster_qr", affinity="rbf", eigen_solver="lobpcg"
    )

    labels = model.fit_predict(plot_points)

    fig = plt.scatter(plot_points[:, 0], plot_points[:, 1], c=labels, s=10, cmap="viridis")

    file_name = os.path.basename(os.path.normpath(file_to_plot))  # Get file at end of path
    file_name = os.path.splitext(file_name)[0]  # Strip off file extension

    plt.savefig(
        os.path.join(save_directory, f"SpectralClustering-{file_name}.png"), bbox_inches="tight", pad_inches=0
    )
