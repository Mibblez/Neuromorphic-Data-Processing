import csv
import os
from os import walk
from os import listdir
from os.path import isfile, join
import numpy as np
import json
from typing import List

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

    def __init__(self):
        self.graphType = 'hist'
        self.dataFolder =''
        self.saveFigures = False
        self.plotVariance = False
        self.FWHMMultiplier = 2.355
        self.logValues = False
        self.plotFWHM = False
        self.dataSetType ='waveformsAndFrequency'
        self.plotConstant = 'waveforms'
        self.maxEventCount = -1
        self.reconstructionWindow = 500
        self.gaussianMinY = 0
        self.gaussianMaxY = 1

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


def read_aedat_csv(csv_path: str, timeWindow: int, maxSize: int = -1) -> CsvData:
    x = []
    y_on = []
    y_off = []
    y_all = []

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file could not be found: {csv_path}")

    with open(csv_path, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # Skip header

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

#TODO: Return object and not array
def getData(folderName: str, timeWindow: int, maxSize: int = -1):
    onlyfiles = [f for f in listdir("./data/" + folderName) if isfile(join("./data/" + folderName, f))]

    fileCount = 0
    x = []
    y_on= []
    y_off = []
    y_all = []
    for file in onlyfiles:
        with open('./data/'+folderName+"/" +file, 'r') as csvfile:
            fileCount +=1
            reader = csv.reader(csvfile, delimiter=',')
            next(reader, None)#skip over header
            for i, row in enumerate(reader):
                x.append((i-1) *timeWindow*0.000001)
                #TODO: If timewindow is large this will not work
                # also machineLearning Get data might need this fix for outliers
                if int(row[2]) > 8000: # If camera bugs out and registers too many events, add like data
                    y_all.append(sum(y_all)/len(y_all))
                    y_off.append(sum(y_off)/len(y_off))
                    y_on.append(sum(y_on)/len(y_on))
                else:
                    y_all.append(int(row[2]))
                    y_off.append(int(row[1]))
                    y_on.append(int(row[0]))
                if i == maxSize:
                    break
                
    N= fileCount
    return y_on,y_off,y_all,N,x

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

def parseConfig(location: str = 'config.json') -> EventChunkConfig:
    config_json = json.loads(open(os.path.join("plotting",location)).read())
    config = EventChunkConfig()
    for i,key in  enumerate(config_json.keys()):
        setattr(config, key, config_json[key]) #assign all properties in json to config object
    return config
