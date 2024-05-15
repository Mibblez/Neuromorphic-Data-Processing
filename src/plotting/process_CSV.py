"""""
This script takes a folder full of CSV files in the form ON, OFF, BOTH
and calcualtes selected stats for use in a Neural Network.
This version of the script only operates on the BOTH column

"""

import csv
import os
import argparse
from plotting_utils import filename_regex
from plotting_utils.plotting_helper import path_arg


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("csv_folder", help="Folder with CSV files to plot", type=path_arg)

    parser.add_argument("--save_directory", "-s", help="Save file to directory", type=path_arg)

    parser.add_argument("-background", "-bg", help="Background used for the cpatures", type=str, required=True)

    args = parser.parse_args()

    return args


def process_csv_files(directory: str, output_file: str, target: str, subdivisions: int = 5):
    files = [file for file in os.listdir(directory) if file.endswith(".csv")]

    with open(output_file, "w", newline="") as csvfile:
        fieldnames = ["File", "Target", "1% Max", "1% Min", "Average", "Total"]
        for j in range(subdivisions):
            fieldnames.extend(
                [
                    f"1% Max Subdivision {j+1}",
                    f"1% Min Subdivision {j+1}",
                    f"Average Subdivision {j+1}",
                    f"Total Subdivision {j+1}",
                ]
            )
        fieldnames.extend(["Hz", "Intensity", "Threshold", "Retarder Angle"])
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for file_name in files:
            hz = filename_regex.parse_frequency(file_name, "Hz ")
            intensity = filename_regex.parse_intensity(file_name, "int ")
            thresh = filename_regex.parse_nthreshold(file_name, "T")
            retAngle = filename_regex.parse_retAngle(file_name, "R")

            with open(os.path.join(directory, file_name), "r") as csv_file:
                csv_reader = csv.reader(csv_file)
                next(csv_reader)  # skip the header row
                data = list(csv_reader)

                column_data = []

                for row in data:
                    column_data.append(float(row[2]))  # only consider the third column

                # Calculate statistics for entire file
                column_data.sort()
                n = len(column_data)
                one_percent_index = int(0.01 * n)
                one_percent_max = column_data[-one_percent_index - 1]
                one_percent_min = column_data[one_percent_index]
                average = sum(column_data) / n
                total = sum(column_data)

                # Initialize dictionary to store statistics
                statistics = {
                    "File": file_name,
                    "1% Max": one_percent_max,
                    "1% Min": one_percent_min,
                    "Average": average,
                    "Total": total,
                }

                # Divide data into subdivisions and calculate statistics
                subdivision_size = len(data) // subdivisions
                for j in range(subdivisions):
                    start_index = j * subdivision_size
                    end_index = (j + 1) * subdivision_size if j < subdivisions - 1 else len(data)
                    subdivision_data = [float(row[2]) for row in data[start_index:end_index]]

                    # Calculate statistics for subdivision
                    subdivision_data.sort()
                    n = len(subdivision_data)
                    one_percent_index = int(0.01 * n)
                    one_percent_max = subdivision_data[-one_percent_index - 1]
                    one_percent_min = subdivision_data[one_percent_index]
                    average = sum(subdivision_data) / n
                    total = sum(subdivision_data)

                    # Add subdivision statistics to the dictionary
                    statistics[f"1% Max Subdivision {j+1}"] = one_percent_max
                    statistics[f"1% Min Subdivision {j+1}"] = one_percent_min
                    statistics[f"Average Subdivision {j+1}"] = average
                    statistics[f"Total Subdivision {j+1}"] = total

                statistics["Target"] = target
                statistics["Hz"] = hz
                statistics["Intensity"] = intensity
                statistics["Threshold"] = thresh
                statistics["Retarder Angle"] = retAngle
                writer.writerow(statistics)


def main(args: argparse.Namespace):
    directory_path = args.csv_folder
    output_file_path = args.save_directory
    background = args.background
    process_csv_files(directory_path, output_file_path, background)


if __name__ == "__main__":
    args = get_args()
    main(args)
