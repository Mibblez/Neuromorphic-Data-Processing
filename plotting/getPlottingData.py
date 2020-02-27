import csv
import os
from os import walk
from os import listdir
from os.path import isfile, join
import numpy as np

def getData(folderName):
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

            for i, row in enumerate(reader):
                if i != 0:
                    x.append((i-1) *1500*0.000001)
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
                    if i == 10000:
                                break
                
    N= fileCount
    return y_on,y_off,y_all,N,x


def getEventChunkData(folderName):
    points = []
    onlyfiles = [f for f in listdir("./eventChunkData/" +folderName) if isfile(join("./eventChunkData/" + folderName, f))]
    for file in onlyfiles:
        with open('./eventChunkData/'+folderName+"/" +file, 'r') as csvfile:
            
            reader = csv.reader(csvfile, delimiter=',')
            for i, row in enumerate(reader):
                if i != 0:
                    points.append([int(row[1]), 128-int(row[2])])
            
        return points  
