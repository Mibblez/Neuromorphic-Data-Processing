import csv
import os
from os import walk
from os import listdir
from os.path import isfile, join
import numpy as np
import json
import itertools
from typing import List
import sys
import math
from types import FunctionType

class EventChunkConfig:

    graphType:str
    '''hist, wavelets, kmeans, smooth buts lets be honest. its just hist '''

    saveFigures: bool
    ''' Saves the figures if set to True, Shows the figures if False '''

    dataFolder:str
    '''The folder where the data is'''
    plotVariance:bool
    '''If true will calculate the variance values '''
    plotFWHM:bool
    '''If true will calculate the FWHM '''

    FWHMMultiplier:float
    ''' Used to change FHWM(2.355) to standard deviation(1)'''

    logValues:bool
    '''Logs all the values if true '''

    dataSetType:str
    ''' waveforms, frequency, waveformsAndFrequency, or backgrounds'''

    plotConstant:str
    ''' The variable that is constant on the graph '''

    maxEventCount:int
    ''' The max event count to read from the file '''
    
    reconstructionWindow:int
    ''' The settings used to generate the csv files'''

    gaussianMinY:float

    gaussianMaxY:float

    def __init__(self, graph_type='hist', data_folder='', save_figures=False, plot_variance=False,
                 fwhm_multiplier=2.355, log_values=False, plot_fwhm=False,
                 data_set_type='waveformsAndFrequency', plot_constant='waveforms', max_event_count=-1,
                 reconstruction_window=500, gaussian_min_y=0, gaussian_max_y=1
                 ):
        self.graphType = graph_type
        self.dataFolder = data_folder
        self.saveFigures = save_figures
        self.plotVariance = plot_variance
        self.FWHMMultiplier = fwhm_multiplier
        self.logValues = log_values
        self.plotFWHM = plot_fwhm
        self.dataSetType = data_set_type
        self.plotConstant = plot_constant
        self.maxEventCount = max_event_count
        self.reconstructionWindow = reconstruction_window
        self.gaussianMinY = gaussian_min_y
        self.gaussianMaxY = gaussian_max_y


# TODO: rename to CsvChunkData
class CsvData:
    file_name: str
    time_windows: List[int]
    y_on: List[int]
    y_off: List[int]
    y_all: List[int]

    def __init__(self, file_name: str, time_windows: List[int], y_on: List[int], y_off: List[int], y_all: List[int]):
        self.file_name = file_name
        self.time_windows = time_windows
        self.y_on = y_on
        self.y_off = y_off
        self.y_all = y_all


class SpatialCsvData():
    def __init__(self, polarity_as_bool: bool, polarity_as_color: bool):
        self.polarities: List[bool] = []
        self.polarities_color: List[str] = []
        self.x_positions: List[int] = []
        self.y_positions: List[int] = []
        self.timestamps: List[int] = []

        self.__polarity_storage_callbacks: List[FunctionType] = []

        if polarity_as_color:
            self.__polarity_storage_callbacks.append(self.__store_polarity_color)

        if polarity_as_bool:
            self.__polarity_storage_callbacks.append(self.__store_polarity_bool)

    def __store_polarity_bool(self, timestamp):
        self.polarities.append(timestamp)

    def __store_polarity_color(self, timestamp):
        self.polarities_color.append('g' if timestamp == 1 else 'r')

    def from_csv(csv_file: str, polarity_as_bool: bool, polarity_as_color: bool,
                 time_limit: int = sys.maxsize):
        first_timestamp = 0
        if time_limit != sys.maxsize:
            time_limit = int(time_limit * 1000000)  # Convert to microseconds

        spatial_csv_data = SpatialCsvData(polarity_as_bool, polarity_as_color)

        with open(csv_file, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            header = next(reader, None)  # Grab header

            # Make sure CSV is the correct format
            if header != ['On/Off', 'X', 'Y', 'Timestamp']:
                raise ValueError("CSV may not be the correct format.\n"
                                 "Header should be On/Off,X,Y,Timestamp")

            first_row = next(reader, None)
            first_timestamp = int(first_row[3])

            for row in itertools.chain([first_row], reader):
                timestamp = int(row[3]) - first_timestamp

                if timestamp > time_limit:
                    break

                polarity = row[0] in ['1', 'True']
                x_pos = int(row[1])
                y_pos = 128 - int(row[2])

                spatial_csv_data.append_row(polarity, x_pos, y_pos, timestamp)

        return spatial_csv_data

    def append_row(self, polarity: bool, x: int, y: int, timestamp: int):
        self.x_positions.append(x)
        self.y_positions.append(y)
        self.timestamps.append(timestamp)

        for polarity_func in self.__polarity_storage_callbacks:
            polarity_func(polarity)


# TODO: indicate that this is for chunk CSVs
def read_aedat_csv(csv_path: str, timeWindow: int, maxSize: int = -1) -> CsvData:
    x = []
    y_on = []
    y_off = []
    y_all = []

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file could not be found: {csv_path}")

    with open(csv_path, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        header = next(reader, None)  # Grab header
        
        # Make sure CSV is the correct format
        for entry in header:
            if 'count' not in entry.lower():
                raise ValueError(f"CSV may not be the correct format.\nHeader entries should indicate that the columns contain event counts")

        for i, row in enumerate(reader):
            x.append((i-1) * timeWindow * 0.000001)
            #TODO: If timewindow is large this will not work
            # also machineLearning Get data might need this fix for outliers
            if int(row[2]) > 8000: # If camera bugs out and registers too many events, use like data instead
                y_on.append(sum(y_on)/len(y_on))
                y_off.append(sum(y_off)/len(y_off))
                y_all.append(sum(y_all)/len(y_all))
            else:
                y_on.append(int(row[0]))
                y_off.append(int(row[1]))
                y_all.append(int(row[2]))
            if i == maxSize:
                break

    return CsvData(csv_path, x, y_on, y_off, y_all)


def getEventChunkData(folderName: str):
    points = []
    onlyfiles = [f for f in listdir("./eventChunkData/" +folderName) if isfile(join("./eventChunkData/" + folderName, f))]
    for file in onlyfiles:
        with open('./eventChunkData/'+folderName+"/" +file, 'r') as csvfile:
            
            reader = csv.reader(csvfile, delimiter=',')
            for i, row in enumerate(reader):
                if i != 0:
                    points.append([int(row[1]), 128-int(row[2])])
            
        return points       

def parseConfig(location: str = 'plotting/config.json', data_folder=None) -> EventChunkConfig:
    config_json = json.loads(open(location).read())
    config = EventChunkConfig()
    for i,key in  enumerate(config_json.keys()):
        setattr(config, key, config_json[key]) #assign all properties in json to config object

    # HACK
    if data_folder:
        setattr(config, "dataFolder", data_folder)

    return config
