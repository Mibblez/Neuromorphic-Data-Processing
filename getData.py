import csv
from os import walk
from os import listdir
from os.path import isfile, join
import numpy as np

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
            allCount =0
            onCount = 0
            offCount = 0
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                if(row[0] == "True"):
                    onCount +=1
                else:
                    offCount +=1
                allCount+=1
            allCount-=1
            offCount-=1
            if allCount ==-1:
                allCount = 0
            if offCount == -1:
                offCount = 0
            x.append(fileCount)
            y_all.append(allCount)
            y_off.append(offCount)
            y_on.append(onCount)

    N= fileCount
    return y_on,y_off,y_all,N,x