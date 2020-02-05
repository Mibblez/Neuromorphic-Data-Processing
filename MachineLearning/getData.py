import csv
import os
from os import walk
from os import listdir
from os.path import isfile, join
import numpy as np
import re

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]



def getData(folderName):
    onlyfiles = [f for f in listdir("./data/" +folderName) if isfile(join("./data/" + folderName, f))]

    fileCount = 0
    x = []
    y_on= []
    y_off = []
    y_all = []
    for file in onlyfiles:
        with open('./data/'+folderName+"/" +file, 'r') as csvfile:
            fileCount +=1
            reader = csv.reader(csvfile, delimiter=',')
            i =0
            for row in reader:
                if i != 0:
                    x.append((i-1) *1500*0.000001)
                    y_all.append(int(row[2]))
                    y_off.append(int(row[1]))
                    y_on.append(int(row[0]))
                i+=1
                
    N= fileCount
    return y_on,y_off,y_all,N,x


def getEventChunkData(folderName):
    points = []
    onlyfiles = [f for f in listdir("./eventChunkData/" +folderName) if isfile(join("./eventChunkData/" + folderName, f))]
    for file in onlyfiles:
        with open('./eventChunkData/'+folderName+"/" +file, 'r') as csvfile:
            
            reader = csv.reader(csvfile, delimiter=',')
            i =0
            for row in reader:
                if i != 0:
                    points.append([int(row[1]), 128-int(row[2])])
                i+=1
        return points  

def getMachineLearningData(numberOfFrames):
    allInputData = []#numberOfFrames x 3
    allOutputData = []#frequency

    folders = os.listdir("data/")
    folders.sort(key=natural_keys)
    
    for folderName in folders:
        onlyfiles = [f for f in listdir("./data/" +folderName) if isfile(join("./data/" + folderName, f))]

        for file in onlyfiles:
            with open('./data/'+folderName+"/" +file, 'r') as csvfile:
                    
                reader = csv.reader(csvfile, delimiter=',')
                i =0
                name = folderName.lower().replace("nopol","").replace("no pol","").replace("30deg","").replace("30 deg","").replace("hz","").replace(" ","").replace("eventchunks","").replace("foam","")
                print(name)
                inputGroup = []
                for row in reader:
                    if i != 0:
                        inputGroup.append((int(row[0]), int(row[1]), int(row[2])))

                        if i % numberOfFrames == 0:
                            allInputData.append(np.array(inputGroup))
                            allOutputData.append(int(name))
                            inputGroup = []
                    i+= 1
    return np.array(allInputData), np.array(allOutputData)

def getMachineLearningDataWaveforms(numberOfFrames):
    allInputData = []#numberOfFrames x 3
    allOutputData = []#frequency

    folders = os.listdir("waveforms/")
    folders.sort(key=natural_keys)
    
    for folderName in folders:
        onlyfiles = [f for f in listdir("./waveforms/" +folderName) if isfile(join("./waveforms/" + folderName, f))]

        for file in onlyfiles:
            with open('./waveforms/'+folderName+"/" +file, 'r') as csvfile:
                    
                reader = csv.reader(csvfile, delimiter=',')
                i =0
                name = folderName.lower().replace("-"," ").replace("nopol","").replace("no pol","").replace("30deg","").replace("30 deg","").replace("1hz","").replace("event chunks","").replace("foam","").replace("1Hz","").replace("500mv","").replace(" ","")
                print(name)
                inputGroup = []
                for row in reader:
                    if i != 0:
                        inputGroup.append((int(row[0]), int(row[1]), int(row[2])))

                        if i % numberOfFrames == 0:
                            allInputData.append(np.array(inputGroup))
                            if name == 'burst':
                                allOutputData.append(0)
                            elif name == 'sine':
                                allOutputData.append(1)
                            elif name == 'square':
                                allOutputData.append(2)
                            elif name == 'triangle':
                                allOutputData.append(3)
                            elif name == 'dc':
                                allOutputData.append(4)
                            elif name == 'noise':
                                allOutputData.append(5)
                            inputGroup = []
                    i+= 1
    return np.array(allInputData), np.array(allOutputData)

                    
def getMachineLearningDataWaveformsAndFrequency(numberOfFrames):
    allInputData = []#numberOfFrames x 3
    allOutputData = []#frequency

    folders = os.listdir("waveformsAndFrequency/")
    folders.sort(key=natural_keys)
    
    for folderName in folders:
        onlyfiles = [f for f in listdir("./waveformsAndFrequency/" +folderName) if isfile(join("./waveformsAndFrequency/" + folderName, f))]

        for file in onlyfiles:
            with open('./waveformsAndFrequency/'+folderName+"/" +file, 'r') as csvfile:
                    
                reader = csv.reader(csvfile, delimiter=',')
                i =0
                name = folderName.lower()
                print(name)
                inputGroup = []
                for row in reader:
                    if i != 0:
                        inputGroup.append((int(row[0]), int(row[1]), int(row[2])))

                        if i % numberOfFrames == 0:
                            allInputData.append(np.array(inputGroup))
                            waveformOutput = 0
                            if  'burst' in name:
                                waveformOutput =0
                            elif 'sine' in name:
                                waveformOutput = 1
                            elif 'square' in name:
                                waveformOutput = 2
                            elif 'triangle' in name:
                                waveformOutput = 3
                            elif 'dc' in name:
                                waveformOutput = 4
                            elif 'noise' in name:
                                waveformOutput = 5

                            frequencyOuput = 0
                            if '500mv' in name:
                                frequencyOuput = 0
                            elif '400mv' in name:
                                frequencyOuput = 1
                            elif '300mv' in name:
                                frequencyOuput = 2
                            elif '200mv' in name:
                                frequencyOuput = 3
                            
                            allOutputData.append([waveformOutput,frequencyOuput])
                            inputGroup = []
                    i+= 1
    return np.array(allInputData), np.array(allOutputData)

                



