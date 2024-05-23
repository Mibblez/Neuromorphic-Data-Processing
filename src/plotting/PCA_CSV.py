"""""
This script takes a folder full of CSV files in the form ON, OFF, BOTH
and performs Pricipal Component Analysis(PCA) for use in a Neural Network.

"""

import csv
import os
import argparse
from sklearn.decomposition import PCA
import numpy as np
from plotting_utils import filename_regex
from plotting_utils.plotting_helper import path_arg


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("csv_folder", help="Folder with CSV files to plot", type=path_arg)

    parser.add_argument("--save_directory", "-s", help="Save file to directory", type=path_arg)

    parser.add_argument("-background", "-bg", help="Background used for the cpatures", type=str, required=True)

    args = parser.parse_args()

    return args


def CSV_PCA(directory: str, output_file: str, target: str, subdivisions: int = 5, n_components: int = 3):
    files = [file for file in os.listdir(directory) if file.endswith(".csv")]

    with open(output_file, "w", newline="") as csvfile:
        fieldnames = ["File", "Target"]
        for i in range(n_components):  # For each principal component
            fieldnames.extend([f"PC_{i+1}"])
            for j in range(subdivisions):
                fieldnames.extend([f"PC_{i+1} Subdivision {j+1}"])
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
                data = np.array([list(map(float, row)) for row in csv_reader])

                # Run PCA on the entire dataset
                pca = PCA(n_components=n_components)
                pca.fit(data)
                components = pca.components_

                # Initialize dictionary to store PCA results
                statistics = {"File": file_name, "Target": target}

                for i in range(n_components):
                    statistics[f"PC_{i+1}"] = components[i].tolist()

                # Divide data into subdivisions and calculate PCA for each
                subdivision_size = len(data) // subdivisions
                for j in range(subdivisions):
                    start_index = j * subdivision_size
                    end_index = (j + 1) * subdivision_size if j < subdivisions - 1 else len(data)
                    subdivision_data = data[start_index:end_index]

                    # Run PCA on the subdivision
                    pca = PCA(n_components=n_components)
                    pca.fit(subdivision_data)
                    sub_components = pca.components_

                    for i in range(n_components):
                        statistics[f"PC_{i+1} Subdivision {j+1}"] = sub_components[i].tolist()

                # Add additional information
                statistics["Hz"] = hz
                statistics["Intensity"] = intensity
                statistics["Threshold"] = thresh
                statistics["Retarder Angle"] = retAngle

                # Write PCA results for the file
                writer.writerow(statistics)


def main(args: argparse.Namespace):
    directory_path = args.csv_folder
    output_file_path = args.save_directory
    background = args.background
    CSV_PCA(directory_path, output_file_path, background)


if __name__ == "__main__":
    args = get_args()
    main(args)
