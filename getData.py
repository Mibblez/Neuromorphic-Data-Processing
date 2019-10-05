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
            reader = csv.reader(csvfile, delimiter=',')
            i =0
            for row in reader:
                if i != 0:
                    x.append(i-1)
                    y_all.append(int(row[2]))
                    y_off.append(int(row[1]))
                    y_on.append(int(row[0]))
                i+=1
                
    N= fileCount
    return y_on,y_off,y_all,N,x