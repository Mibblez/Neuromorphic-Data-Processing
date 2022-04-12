import imp
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, AutoMinorLocator
import argparse
import re
import os
from natsort import natsorted
import pandas as pd
import tqdm

csv_folder = None
debug_info = False


def get_args():
    global csv_folder, debug_info

    parser = argparse.ArgumentParser()
    parser.add_argument("csv_folder", help="Folder with CSV files to plot", type=str)
    parser.add_argument("--debug_info", '-d', help="Display debug info insead of a progress bar",
                        action='store_true')
    args = parser.parse_args()

    csv_folder = args.csv_folder

    if not os.path.exists(csv_folder) or not os.path.isdir(csv_folder):
        quit(f"The folder {csv_folder} does not exist")

    debug_info = args.debug_info


if __name__ == "__main__":
    get_args()

    # Resize plot
    plt.rcParams['figure.figsize'] = [11, 5.5]

    if debug_info:
        pbar = natsorted(os.listdir(csv_folder))
    else:
        pbar = tqdm.tqdm(natsorted(os.listdir(csv_folder)))

    # Iterate over sub-directories inside csv_folder
    for current_folder in pbar:
        if not os.path.isdir(os.path.join(csv_folder, current_folder)):
            continue

        hz = re.search("[0-9]{1,} ?[H|h][Z|z]", current_folder)

        if not hz:
            if debug_info:
                print(f"Could not parse frequency for folder '{current_folder}', skipping...")
            continue

        hz = hz.group()

        # Update progress bar if it is being used
        if type(pbar) == tqdm.std.tqdm:
            pbar.set_description(f"Processing {hz}")

        plot_x = []
        plot_y = []

        # Iterate over csv files in the current sub-directory
        files_in_current_folder = os.listdir(os.path.join(csv_folder, current_folder))
        for csv_filename in files_in_current_folder:
            if not csv_filename.endswith(".csv"):
                continue

            full_csv_path = os.path.join(csv_folder, current_folder, csv_filename)
            # print(full_csv_path)

            degrees = re.search("[0-9]{1,} ?deg", csv_filename, re.IGNORECASE)
            if degrees:
                degrees = int(re.search("[0-9]{1,}", degrees.group()).group())
            else:
                if debug_info:
                    print(f"Could not parse polarization angle for file '{full_csv_path}', skipping...")
                continue

            df = pd.read_csv(full_csv_path, header=0, usecols=['Timestamp'])

            # Length of the recording in microseconds
            recording_length = df['Timestamp'].values[-1] - df['Timestamp'].values[0]

            events_per_second = len(df) / (recording_length / 1000000)

            plot_x.append(degrees)
            plot_y.append(events_per_second)

        # Sort plot_x and plot_y based upon the order of plot_x
        plot_x, plot_y = [list(x) for x in zip(*sorted(zip(plot_x, plot_y), key=lambda pair: pair[0]))]

        plt.plot(plot_x, plot_y, label=hz, marker='o', markersize=4)

    plt.ylabel("Events/Second")
    plt.xlabel("Polarization Angle")
    plt.grid(which='major', axis='both')
    plt.grid(which='minor', axis='y', linestyle='dashed')

    # Place the legend outside of the plot
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    ax = plt.gca()
    ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax.set_ylim(bottom=0)

    plt.tight_layout()
    plt.show()
