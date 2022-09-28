import csv
import os
from os import listdir
from os.path import isfile, join
import numpy as np
import sklearn.model_selection as sk
from natsort import natsorted, ns


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


class WaveAndFreqData:
    waveform_train_output = []
    frequency_train_output = []
    waveform_test_output = []
    frequency_test_output = []
    train_input = []
    test_input = []

    def __init__(self, num_frames: int, base_folder: str):
        all_input_data = []  # Number of frames * 3
        all_output_data = []  # Frequency

        folders = os.listdir(f"data/{base_folder}")
        folders = natsorted(folders, alg=ns.IGNORECASE)

        for folder_name in folders:
            onlyfiles = [
                f
                for f in listdir(f"./data/{base_folder}/{folder_name}")
                if isfile(join(f"./data/{base_folder}/{folder_name}", f))
            ]

            for data_file in onlyfiles:
                with open(f"./data/{base_folder}/{folder_name}/{data_file}", "r") as csv_file:

                    reader = csv.reader(csv_file, delimiter=",")
                    name = folder_name.lower()
                    print(name)
                    input_group = []

                    for i, row in enumerate(reader):
                        if i != 0:
                            input_group.append((int(row[0]), int(row[1]), int(row[2])))

                            if i % num_frames == 0:
                                all_input_data.append(np.array(input_group))
                                waveform_output = 0
                                if "burst" in name:
                                    waveform_output = 0
                                elif "sine" in name:
                                    waveform_output = 1
                                elif "square" in name:
                                    waveform_output = 2
                                elif "triangle" in name:
                                    waveform_output = 3
                                elif "dc" in name:
                                    waveform_output = 4
                                elif "noise" in name:
                                    waveform_output = 5

                                frequency_ouput = 0
                                if "500mv" in name:
                                    frequency_ouput = 0
                                elif "400mv" in name:
                                    frequency_ouput = 1
                                elif "300mv" in name:
                                    frequency_ouput = 2
                                elif "200mv" in name:
                                    frequency_ouput = 3

                                all_output_data.append([waveform_output, frequency_ouput])
                                input_group = []

        # Split data into train/test sets
        self.train_input, self.test_input, train_output, test_output = sk.train_test_split(
            all_input_data, all_output_data, test_size=0.1, random_state=42
        )

        for item in train_output:
            self.waveform_train_output.append(item[0])
            self.frequency_train_output.append(item[1])

        for item in test_output:
            self.waveform_test_output.append(item[0])
            self.frequency_test_output.append(item[1])

        self.waveform_train_output = np.array(self.waveform_train_output)
        self.waveform_test_output = np.array(self.waveform_test_output)
        self.frequency_train_output = np.array(self.frequency_train_output)
        self.frequency_test_output = np.array(self.frequency_test_output)
        self.train_input = np.array(self.train_input)
        self.test_input = np.array(self.test_input)
