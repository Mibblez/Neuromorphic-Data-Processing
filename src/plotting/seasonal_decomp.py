from pandas import read_csv, DataFrame
from matplotlib import pyplot as plt
from typing import List
from plotting_utils.plotting_helper import check_aedat_csv_format
from plotting_utils.plotting_helper import file_arg, path_arg, int_arg_positive_nonzero
import matplotlib
import statsmodels.api as sm
import argparse
import os


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("aedat_csv_file", help="CSV containing AEDAT data to be plotted", type=file_arg)
    parser.add_argument(
        "--event_type",
        "-e",
        help="The type of events to plot",
        action="store",
        type=str,
        choices=["on", "off", "combined"],
        required=True,
    )
    parser.add_argument(
        "--num_rows",
        "-n",
        help="The number of rows of data to include in the plot",
        type=int_arg_positive_nonzero,
        required=True,
    )
    parser.add_argument(
        "--skip_rows",
        "-s",
        help="Skip n number of rows from the beginning of the csv file ",
        type=int_arg_positive_nonzero,
        default=0,
    )
    parser.add_argument(
        "--period", "-p", help="The period for the seasonal decomposition", type=int_arg_positive_nonzero, default=100
    )
    parser.add_argument("--save_directory", "-d", help="Save file to directory", type=path_arg)

    args = parser.parse_args()
    args.event_type = args.event_type.capitalize() + " Count"

    return args


def seasonal_decomp(
    csv_path: str, columns_to_plot: List[str], num_rows: int, seasonal_period: int = 100, plot_title=None, skip_rows=0
) -> List[DataFrame]:
    df = read_csv(csv_path, nrows=num_rows + skip_rows + 1)

    column_titles_found = list(df)

    if not check_aedat_csv_format(column_titles_found, columns_to_plot):
        raise ValueError(f"Found header: {column_titles_found}\nExpected header to include: {columns_to_plot}")

    decomposition_results = []
    for column in columns_to_plot:
        events_to_plot = df[column]

        if plot_title is not None:
            # The name of the dataframe will be used as the plot title
            events_to_plot.name = f"{plot_title} {column}"

        decomposition_results.append(sm.tsa.seasonal_decompose(events_to_plot[skip_rows:], period=seasonal_period))

    return decomposition_results


def main(args: argparse.Namespace):

    matplotlib.use("Qt5Agg")

    # Auto generate plot title from csv_filename
    plot_title = os.path.splitext(os.path.basename(os.path.normpath(args.aedat_csv_file)))[0]

    decomposition = seasonal_decomp(
        args.aedat_csv_file, [args.event_type], args.num_rows, args.period, plot_title, args.skip_rows
    )[0]
    decomposition.plot()

    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(16, 10)

    plt.tight_layout(pad=1.10)
    plt.savefig(f"{plot_title}-{args.event_type.replace(' ', '-')}.png")
    plt.clf()


if __name__ == "__main__":
    args = get_args()
    main(args)
