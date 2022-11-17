from pandas import read_csv, DataFrame
from matplotlib import pyplot as plt
from typing import List
import matplotlib
import statsmodels.api as sm
import argparse
import sys
import os

file_to_plot = ""
event_type = ""
num_rows = -1
skip_rows = 0
period = 100
save_directory = ""


def get_args():
    global file_to_plot, event_type, num_rows, skip_rows, period, save_directory

    parser = argparse.ArgumentParser()

    parser.add_argument("aedat_csv_file", help="CSV containing AEDAT data to be plotted", type=str)
    parser.add_argument(
        "--event_type", "-e", help="The type of events to plot [on, off, combined]", action="store", type=str
    )
    parser.add_argument("--num_rows", "-n", help="The number of rows of data to include in the plot", type=int)
    parser.add_argument("--skip_rows", "-s", help="Skip n number of rows from the beginning of the csv file ", type=int)
    parser.add_argument("--period", "-p", help="The period for the seasonal decomposition", type=int, default=100)
    parser.add_argument("--save_directory", "-d", help="Save file to directory", type=str)

    args = parser.parse_args()

    if args.save_directory is not None:
        if not os.path.exists(args.save_directory):
            sys.exit(f'Error: Specified path "{args.save_directory}" does not exist')
        else:
            save_directory = args.save_directory

    file_to_plot = args.aedat_csv_file

    if args.num_rows is not None:
        if args.num_rows > 0:
            num_rows = args.num_rows
        else:
            parser.print_help()
            sys.exit("Error: Arg num_rows must be greater than 0")
    else:
        parser.print_help()
        sys.exit("Error: Arg num_rows is required")

    if args.skip_rows is not None:
        if args.skip_rows > 0:
            skip_rows = args.skip_rows
        else:
            parser.print_help()
            sys.exit("Error: Arg skip_rows must be greater than 0")

    if args.period is not None:
        if args.period > 0:
            period = args.period
        else:
            parser.print_help()
            sys.exit("Error: Arg period must be greater than 0")

    if args.event_type is not None:
        event_type = args.event_type.lower()
        if event_type not in ("on", "off", "combined"):
            parser.print_help()
            sys.exit("Error: Invalid event type. Use one of the following: [on, off, combined]")
        event_type = event_type.capitalize() + " Count"
    else:
        parser.print_help()
        sys.exit("Error: Arg event_type is required")


def seasonal_decomp(
    csv_path: str, columns: List[str], num_rows: int, seasonal_period: int = 100, plot_title=None, skip_rows=0
) -> List[DataFrame]:
    df = read_csv(csv_path, nrows=num_rows + skip_rows + 1)
    decomposition_results = []

    for column in columns:
        events_to_plot = df[column]

        if plot_title is not None:
            # The name of the dataframe will be used as the plot title
            events_to_plot.name = f"{plot_title} {column}"

        decomposition_results.append(sm.tsa.seasonal_decompose(events_to_plot[skip_rows:], period=seasonal_period))

    return decomposition_results


if __name__ == "__main__":
    get_args()

    matplotlib.use("Qt5Agg")

    # Auto generate plot title from csv_filename
    plot_title = os.path.splitext(os.path.basename(os.path.normpath(file_to_plot)))[0]

    decomposition = seasonal_decomp(file_to_plot, [event_type], num_rows, period, plot_title, skip_rows)[0]
    decomposition.plot()

    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(16, 10)

    plt.tight_layout(pad=1.10)
    plt.savefig(f"{plot_title}-{event_type.replace(' ', '-')}.png")
    plt.clf()
