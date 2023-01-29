import argparse
import os

from sklearn.cluster import SpectralClustering
import numpy as np
import plotting_utils.get_plotting_data as get_plotting_data
from plotting_utils.get_plotting_data import DataStorage

import matplotlib
import matplotlib.pyplot as plt

from plotting_utils.plotting_helper import int_arg_not_negative, path_arg, file_arg, float_arg_positive_nonzero


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("aedat_csv_file", help="CSV containing AEDAT data to be plotted", type=file_arg)
    parser.add_argument(
        "--num_clusters",
        "-c",
        help="Sets number of clusters, defaulted to 6. Minimum value is 2",
        default=6,
        type=int,
    )
    parser.add_argument("--skip_rows", "-s", help="Skips N rows of the input CSV", default=0, type=int_arg_not_negative)
    parser.add_argument(
        "--max_time", "-t", help="Max time in microseconds", default=None, type=float_arg_positive_nonzero
    )
    parser.add_argument("--save_directory", "-d", help="Save file to directory", default=".", type=path_arg)

    args = parser.parse_args()

    if args.num_clusters < 2:
        parser.error("The minimum value for --num_clusters is 2")

    if args.max_time:
        # Convert time to seconds
        args.max_time = args.max_time * (10**-6)

    return args


def main(args: argparse.Namespace):
    get_args()
    matplotlib.use("Qt5Agg")

    data = get_plotting_data.SpatialCsvData.from_csv(
        args.aedat_csv_file, DataStorage.NONE, args.max_time, args.skip_rows
    )

    # Transform X and Y positions into the correct format for this plot -> [[X,Y], [X,Y], ...]
    plot_points = np.asarray(list(zip(data.x_positions, data.y_positions)))

    model = SpectralClustering(
        n_clusters=args.num_clusters, assign_labels="cluster_qr", affinity="rbf", eigen_solver="lobpcg"
    )

    labels = model.fit_predict(plot_points)
    plt.scatter(plot_points[:, 0], plot_points[:, 1], c=labels, s=10, cmap="viridis")

    file_name = os.path.basename(os.path.normpath(args.aedat_csv_file))  # Get file at end of path
    file_name = os.path.splitext(file_name)[0]  # Strip off file extension

    plt.savefig(
        os.path.join(args.save_directory, f"SpectralClustering-{file_name}.png"), bbox_inches="tight", pad_inches=0
    )


if __name__ == "__main__":
    args = get_args()
    main(args)
