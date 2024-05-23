import csv
import os
from os import listdir
from os.path import isfile, join
import glob
import numpy as np
import sklearn.model_selection as sk
from natsort import natsorted, ns

from plotting_utils import filename_regex
from plotting_utils.plotting_helper import check_aedat_csv_format


# TODO: cleanup
def getMachineLearningData(num_frames: int, base_folder: str):
    all_input_data = []  # numberOfFrames x 3
    all_output_data = []  # frequency

    folders = os.listdir(f"data/{base_folder}")
    folders = natsorted(folders, alg=ns.IGNORECASE)

    for folder_name in folders:
        only_files = [
            f
            for f in listdir(f"data/{base_folder}/{folder_name}")
            if isfile(join(f"data/{base_folder}/{folder_name}", f))
        ]

        for data_file in only_files:
            with open(f"data/{base_folder}/{folder_name}/{data_file}", "r") as csvfile:
                reader = csv.reader(csvfile, delimiter=",")

                # Waveform files
                if "burst" in folder_name:
                    file_class = 0
                elif "sine" in folder_name:
                    file_class = 1
                elif "square" in folder_name:
                    file_class = 2
                elif "triangle" in folder_name:
                    file_class = 3
                elif "dc" in folder_name:
                    file_class = 4
                elif "noise" in folder_name:
                    file_class = 5
                # This must be a frequency file. Use the frequency as the class
                else:
                    file_class = (
                        folder_name.lower()
                        .replace("nopol", "")
                        .replace("no pol", "")
                        .replace("30deg", "")
                        .replace("30 deg", "")
                        .replace("hz", "")
                        .replace(" ", "")
                        .replace("eventchunks", "")
                        .replace("foam", "")
                    )

                print(file_class)
                input_group = []
                for i, row in enumerate(reader):
                    if i != 0:
                        input_group.append((int(row[0]), int(row[1]), int(row[2])))

                        if i % num_frames == 0:
                            all_input_data.append(np.array(input_group))
                            all_output_data.append(file_class)
                            input_group = []
    return np.array(all_input_data), np.array(all_output_data)


def getMachineLearningDataTexture(num_frames: int, base_folder: str):
    all_input_data = []  # numberOfFrames x 3
    all_output_data = []  # frequency

    folders = os.listdir(f"data/{base_folder}")
    folders = natsorted(folders, alg=ns.IGNORECASE)

    for folder_name in folders:
        only_files = [
            f
            for f in listdir(f"data/{base_folder}/{folder_name}")
            if isfile(join(f"data/{base_folder}/{folder_name}", f))
        ]

        for data_file in only_files:
            with open(f"data/{base_folder}/{folder_name}/{data_file}", "r") as csvfile:
                reader = csv.reader(csvfile, delimiter=",")

                # Texture files
                if "120G" in folder_name:
                    file_class = 0
                elif "150G" in folder_name:
                    file_class = 1
                elif "180G" in folder_name:
                    file_class = 2
                elif "240G" in folder_name:
                    file_class = 3
                elif "320G" in folder_name:
                    file_class = 4
                elif "400G" in folder_name:
                    file_class = 5
                elif "600G" in folder_name:
                    file_class = 6
                elif "800G" in folder_name:
                    file_class = 7
                elif "1000G" in folder_name:
                    file_class = 8
                elif "1500G" in folder_name:
                    file_class = 9
                elif "2500G" in folder_name:
                    file_class = 10
                elif "3000G" in folder_name:
                    file_class = 11
                # This must be a frequency file. Use the frequency as the class
                else:
                    print("WARNING: Unrecognized folder")
                    continue
                print(f"{data_file} in {folder_name} is class {file_class}")
                input_group = []
                for i, row in enumerate(reader):
                    if i != 0:
                        input_group.append((int(row[0]), int(row[1]), int(row[2])))

                        if i % num_frames == 0:
                            all_input_data.append(np.array(input_group))
                            all_output_data.append(file_class)
                            input_group = []
    return np.array(all_input_data), np.array(all_output_data)

def getMachineLearningDataBackground(num_frames: int, base_folder: str):
    all_input_data = []  # numberOfFrames x 3
    all_output_data = []  # frequency

    folders = os.listdir(f"data/{base_folder}")
    folders = natsorted(folders, alg=ns.IGNORECASE)

    for folder_name in folders:
        only_files = [
            f
            for f in listdir(f"data/{base_folder}/{folder_name}")
            if isfile(join(f"data/{base_folder}/{folder_name}", f))
        ]

        for data_file in only_files:
            with open(f"data/{base_folder}/{folder_name}/{data_file}", "r") as csvfile:
                reader = csv.reader(csvfile, delimiter=",")

                # Texture files
                if "Black_Paper" in folder_name:
                    file_class = 0
                elif "White_Paper" in folder_name:
                    file_class = 1
                elif "Cream_Paper" in folder_name:
                    file_class = 2
                elif "Gray_Paper" in folder_name:
                    file_class = 3
                # This must be a background file. Use the background as the class
                else:
                    print("WARNING: Unrecognized folder")
                    continue
                print(f"{data_file} in {folder_name} is class {file_class}")
                input_group = []
                for i, row in enumerate(reader):
                    if i != 0:
                        input_group.append((int(row[0]), int(row[1]), int(row[2])))

                        if i % num_frames == 0:
                            all_input_data.append(np.array(input_group))
                            all_output_data.append(file_class)
                            input_group = []
    return np.array(all_input_data), np.array(all_output_data)


class WaveAndFreqData:
    waveform_id_dict = {"burst": 0, "sine": 1, "square": 2, "triangle": 3, "dc": 4, "noise": 5}
    frequency_id_dict = {"500mv": 0, "400mv": 1, "300mv": 2, "200mv": 3}

    def __init__(self, num_frames: int, base_folder: str):
        all_input_data = []
        all_output_data = []

        # Create a natsorted list of all csv files inside of base_folder
        data_files = natsorted(glob.glob(f"{base_folder}/**/*.csv", recursive=True), alg=ns.IGNORECASE)

        for data_file in data_files:
            with open(data_file) as csv_file:
                basename = os.path.basename(data_file).lower()

                # Determine the file's waveform
                waveform = filename_regex.parse_waveform(basename)
                if waveform not in self.waveform_id_dict:
                    print(f"Could not identify waveform type. Skipping file '{data_file}'...")
                    continue
                waveform_id = self.waveform_id_dict[waveform]

                # Determine the file's frequency
                frequency_id = -1
                for freq in self.frequency_id_dict:
                    if freq in basename:
                        frequency_id = self.frequency_id_dict[freq]
                        break
                if frequency_id == -1:
                    print(f"Could not identify frequency. Skipping file '{data_file}'...")
                    continue

                reader = csv.reader(csv_file, delimiter=",")

                # Ensure csv file contains the correct data, as specified by the header
                header = next(reader, None)
                if not check_aedat_csv_format(header, ["On Count", "Off Count", "Combined Count"]):
                    print(f"CSV file '{data_file}' appears to be of an incorrect format. Header is '{header}'")
                    continue

                input_data_group = []
                for row in reader:
                    # Convert each row of the csv into a list of ints
                    input_data_group.append((int(row[0]), int(row[1]), int(row[2])))

                    # Append data to ML data lists once input_data_group reaches desired size
                    if len(input_data_group) == num_frames:
                        all_input_data.append(input_data_group)
                        all_output_data.append([waveform_id, frequency_id])
                        input_data_group = []

        # Split data into train/test sets
        train_input, test_input, train_output, test_output = sk.train_test_split(
            all_input_data, all_output_data, test_size=0.1, random_state=42
        )

        # Split train_output into waveform_train_output and frequency_train_output
        waveform_train_output = []
        frequency_train_output = []
        for item in train_output:
            waveform_train_output.append(item[0])
            frequency_train_output.append(item[1])

        # Split test_output into waveform_test_output and frequency_test_output
        waveform_test_output = []
        frequency_test_output = []
        for item in test_output:
            waveform_test_output.append(item[0])
            frequency_test_output.append(item[1])

        self.waveform_train_output = np.array(waveform_train_output)
        self.waveform_test_output = np.array(waveform_test_output)
        self.frequency_train_output = np.array(frequency_train_output)
        self.frequency_test_output = np.array(frequency_test_output)
        self.train_input = np.array(train_input)
        self.test_input = np.array(test_input)
