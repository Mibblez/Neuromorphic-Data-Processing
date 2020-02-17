import csv
import os
from os import walk
from os import listdir
from os.path import isfile, join
import numpy as np
import re
import sklearn.model_selection as sk

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

def getMachineLearningData(num_frames):
    all_input_data = []     # numberOfFrames x 3
    all_output_data = []    # frequency

    folders = os.listdir("data/frequency")
    folders.sort(key=natural_keys)
    
    for folder_name in folders:
        onlyfiles = [f for f in listdir(f'data/frequency/{folder_name}') if isfile(join(f'data/frequency/{folder_name}', f))]

        for data_file in onlyfiles:
            with open(f'data/frequency/{folder_name}/{data_file}', 'r') as csvfile: 
                reader = csv.reader(csvfile, delimiter=',')
                name = folder_name.lower().replace("nopol","").replace("no pol","").replace("30deg","").replace("30 deg","").replace("hz","").replace(" ","").replace("eventchunks","").replace("foam","")
                print(name)
                input_group = []
                for i, row in enumerate(reader):
                    if i != 0:
                        input_group.append((int(row[0]), int(row[1]), int(row[2])))

                        if i % num_frames == 0:
                            all_input_data.append(np.array(input_group))
                            all_output_data.append(int(name))
                            input_group = []
    return np.array(all_input_data), np.array(all_output_data)

class WaveAndFreqData:
    waveform_train_output = []
    frequency_train_output = []
    waveform_test_output = []
    frequency_test_output = []
    train_input = []
    test_input = []

    def __init__(self, num_frames):
        all_input_data = []     # Number of frames * 3
        all_output_data = []    # Frequency

        folders = os.listdir('data/waveformsAndFrequency')
        folders.sort(key=natural_keys)

        for folder_name in folders:
            onlyfiles = [f for f in listdir(f'./data/waveformsAndFrequency/{folder_name}') if isfile(join(f'./data/waveformsAndFrequency/{folder_name}', f))]

            for data_file in onlyfiles:
                with open(f'./data/waveformsAndFrequency/{folder_name}/{data_file}', 'r') as csv_file:
                        
                    reader = csv.reader(csv_file, delimiter=',')
                    name = folder_name.lower()
                    print(name)
                    input_group = []

                    for i, row in enumerate(reader):
                        if i != 0:
                            input_group.append((int(row[0]), int(row[1]), int(row[2])))

                            if i % num_frames == 0:
                                all_input_data.append(np.array(input_group))
                                waveform_output = 0
                                if  'burst' in name:
                                    waveform_output = 0
                                elif 'sine' in name:
                                    waveform_output = 1
                                elif 'square' in name:
                                    waveform_output = 2
                                elif 'triangle' in name:
                                    waveform_output = 3
                                elif 'dc' in name:
                                    waveform_output = 4
                                elif 'noise' in name:
                                    waveform_output = 5

                                frequency_ouput = 0
                                if '500mv' in name:
                                    frequency_ouput = 0
                                elif '400mv' in name:
                                    frequency_ouput = 1
                                elif '300mv' in name:
                                    frequency_ouput = 2
                                elif '200mv' in name:
                                    frequency_ouput = 3
                                
                                all_output_data.append([waveform_output,frequency_ouput])
                                input_group = []
        
        self.train_input, self.test_input, train_output, test_output = sk.train_test_split(all_input_data, all_output_data, test_size=0.1, random_state = 42)

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

