import numpy as np
import matplotlib.pyplot as plt
import csv
import os
from os import walk
from os import listdir
from os.path import isfile, join
from scipy.optimize import leastsq
from scipy.signal import savgol_filter
from scipy.signal import argrelextrema
from scipy import stats
import plotSpectrum
import getData
import scipy.fftpack
#folderName ="foam 12hz 30deg Event Chunks"
#folderName ="foam 26hz 30deg Event Chunks"
#folderName = "foam 18hz 30deg Event Chunks"
#folderName = "8hz_30deg Event Chunks"
#folderName ="8hz_nopol Event Chunks"
#folderName = "12hz_30deg Event Chunks"
#folderName = "18hz_30deg Event Chunks"
#folderName = "18hz_nopol Event Chunks"
#folderName = "26hz_30deg Event Chunks"
offFrequencies = []
onFrequencies = []
bothFrequencies = []
folders = os.listdir("data/")

#graphType = "savgol"
graphType = "hist"

for folderName in folders:
    
    #folderName = "26hz_nopol Event Chunks"
    y_on,y_off,y_all, fileCount,x= getData.getData(folderName)

    folderName = folderName.replace('Event Chunks', '')
    folderName = folderName.replace('no pol', "NoPolarizer")
    print(folderName)
    print(np.array(y_off).mean())
    yOffSmoothed = savgol_filter(y_off, 71, 3)
    yOnSmoothed  =  savgol_filter(y_on, 71, 3)
    yBothSmoothed = savgol_filter(y_all, 71,3)

    yf = scipy.fftpack.fft(yOffSmoothed)
    offFrequencies.append(yf)
    onFrequencies.append(scipy.fftpack.fft(yOnSmoothed))
    bothFrequencies.append(scipy.fftpack.fft(yBothSmoothed))

    f, axes = plt.subplots(nrows = 2, ncols = 3, sharex=False, sharey = False )
    f.set_size_inches(18.5, 10.5)

    if graphType == 'hist':
        axes[1][0].hist(y_off, bins=15, color='red',edgecolor='black', linewidth=1.2)
        axes[1][1].hist(y_on,bins=15, color='green',edgecolor='black', linewidth=1.2)
        axes[1][2].hist(y_all,bins=15, color='blue',edgecolor='black', linewidth=1.2)
    else:
        axes[1][0].set_ylim(yOffSmoothed.min(),yOffSmoothed.max()+10)
        axes[1][1].set_ylim(yOnSmoothed.min(),yOnSmoothed.max()+10)
        axes[1][2].scatter(x,yBothSmoothed,c='blue',picker=True, s=1)
        axes[1][0].scatter(x,yOffSmoothed,c='red',picker=True, s=1)
        axes[1][1].scatter(x,yOnSmoothed,c='green',picker=True, s=1)


    
    axes[0][0].scatter(x,y_off,c='red',picker=True,s=1)

    axes[1][0].title.set_text(folderName +" Off Events")
    axes[0][1].scatter(x,y_on,c='green',picker=True,s=1)
    axes[1][1].title.set_text(folderName +" On Events")

    axes[0][2].scatter(x,y_all,c='blue',picker=True,s=1)
    plt.title(folderName +" All Events")

    #plt.show()


plt.show()

def showFFT(data):
    fftX = np.linspace(0.0, 1.0/(2.0*(1.0 / 800.0)), fileCount/2)
    index = 0

    polLabels =[]
    polFreq = []
    noPolLabels = []
    noPolFreq = []

    for y in data:
        if("no pol" in folders[index] ):
            noPolLabels.append(folders[index])
            noPolFreq.append(y)
        else:
            polLabels.append(folders[index])
            polFreq.append(y)

        index+=1

    f, axes = plt.subplots(nrows = 1, ncols = 2, sharex=True, sharey = True )

    index = 0
    for y in polFreq:
        axes[0].plot(fftX, 2.0/fileCount * np.abs(y[:fileCount//2]), label= polLabels[index].replace('Event Chunks', ''))
        index+=1


    axes[0].set_xlim(2,60)
    axes[0].set_ylim(0,50)
    axes[0].legend()



    index = 0
    for y in noPolFreq:
        axes[1].plot(fftX, 2.0/fileCount * np.abs(y[:fileCount//2]), label= noPolLabels[index].replace('Event Chunks', ''))
        index+=1

    axes[1].set_xlim(2,60)
    axes[1].set_ylim(0,50)
    axes[1].legend()
    plt.show()

showFFT(offFrequencies)
showFFT(onFrequencies)
showFFT(bothFrequencies)

input()
        
