"""
3D Plots are a visual display of events over time.
X/Y Axis: Event Position
Z Axis: time

CSV Format: On/Off,X,Y,Timestamp
"""

import argparse
import os
import sys

import matplotlib
import matplotlib.pyplot as plt

import plotting_utils.get_plotting_data as get_plotting_data
from plotting_utils.get_plotting_data import DataStorage
from plotting_utils.plotting_helper import float_arg_positive, path_arg, file_arg


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("aedat_csv_file", help="CSV containing AEDAT data to be plotted", type=file_arg)
    parser.add_argument(
        "--view",
        "-v",
        help="sets plot viewing angle [default, top, side, all]",
        action="store",
        type=str,
        choices=["default", "top", "side", "all"],
        default="default",
    )
    parser.add_argument(
        "--time_limit", "-t", help="Time limit for the Z-axis (seconds)", type=float_arg_positive, default=sys.maxsize
    )
    parser.add_argument("--save_directory", "-d", help="Save file to directory", type=path_arg, default=".")

    return parser.parse_args()


def main(args: argparse.Namespace):
    matplotlib.use("Qt5Agg")

    events = get_plotting_data.SpatialCsvData.from_csv(args.aedat_csv_file, DataStorage.COLOR, args.time_limit)

    fig = plt.figure()
    fig.set_size_inches(12, 10)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_xlabel("X Position")
    ax.set_ylabel("Y Position")
    ax.set_zlabel("Time (Seconds)")

    file_name = os.path.basename(os.path.normpath(args.aedat_csv_file))  # Get file at end of path
    file_name = os.path.splitext(file_name)[0]  # Strip off file extension

    if args.view in ["default", "all"]:
        ax.scatter(
            events.x_positions,
            events.y_positions,
            events.timestamps,
            c=events.polarities_color,
            marker=".",
            s=4,
            depthshade=False,
        )

        fig.savefig(
            os.path.join(args.save_directory, f"3D_Plot-{file_name}-default.png"), bbox_inches="tight", pad_inches=0
        )

    if args.view in ["side", "all"]:
        ax.scatter(
            events.x_positions,
            events.y_positions,
            events.timestamps,
            c=events.polarities_color,
            marker="H",
            s=4,
            depthshade=False,
        )
        ax.view_init(azim=0, elev=8)

        fig.savefig(
            os.path.join(args.save_directory, f"3D_Plot-{file_name}-side.png"), bbox_inches="tight", pad_inches=0
        )

    if args.view in ["top", "all"]:
        ax.scatter(
            events.x_positions,
            events.y_positions,
            events.timestamps,
            c=events.polarities_color,
            marker="H",
            s=4,
            depthshade=False,
        )
        ax.set_zticklabels([])
        ax.view_init(azim=-90, elev=87)

        fig.savefig(
            os.path.join(args.save_directory, f"3D_Plot-{file_name}-top.png"), bbox_inches="tight", pad_inches=0
        )

    plt.clf()


if __name__ == "__main__":
    args = get_args()
    main(args)
