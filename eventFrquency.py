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

for folderName in os.listdir("data/"):
    print(folderName)
    #folderName = "26hz_nopol Event Chunks"
    y_on,y_off,y_all, fileCount,x= getData.getData(folderName)

    yOffSmoothed = savgol_filter(y_off, 51, 10)
    yOnSmoothed  =  savgol_filter(y_on, 51, 10)
    yBothSmoothed = savgol_filter(y_all, 51, 10)
    #freq = np.fft.fft(yhat)
    #print(freq)

    #plt.scatter(x,freq,c='blue',s=1)
    #plt.show()

    #maxInd = argrelextrema(yhat, np.greater)
    #print(yhat[maxInd])
    #freqs = np.fft.fftfreq(len(yhat))

    #print(stats.shapiro(y_off))
    #plt.hist(y_off, bins="auto")
    #plt.show()
    yf = scipy.fftpack.fft(yOffSmoothed)
    xf = np.linspace(0.0, 1.0/(2.0*(1.0 / 800.0)), fileCount/2)

    plt.plot(xf, 2.0/fileCount * np.abs(yf[:fileCount//2]))
    axes = plt.gca()
    axes.set_xlim(2,100)
    axes.set_ylim(0,200)
    plt.show()

    f, axes = plt.subplots(nrows = 2, ncols = 3, sharex=True, sharey = True )
    f.set_size_inches(18.5, 10.5)
    axes[1][0].scatter(x,yOffSmoothed,c='red',picker=True, s=1)
    axes[0][0].scatter(x,y_off,c='red',picker=True,s=1)
    axes[1][0].title.set_text(folderName +" Off Events")


    axes[1][1].scatter(x,yOnSmoothed,c='green',picker=True, s=1)
    axes[0][1].scatter(x,y_on,c='green',picker=True,s=1)
    plt.title(folderName +" On Events")

    axes[1][2].scatter(x,yBothSmoothed,c='blue',picker=True, s=1)
    axes[0][2].scatter(x,y_all,c='blue',picker=True,s=1)
    plt.title(folderName +" All Events")

    plt.show()




    #plt.scatter(x,yhat,c='blue',s=1)

    #f = plt.figure()    
    #f, axes = plt.subplots(nrows = 2, ncols = 1, sharex=True, sharey = True)
    #axes[0].scatter(x,y_off,c='red')
    #axes[1].scatter(x,y_on,c='green')
    #plt.title('Scatter plot pythonspot.com')
    #plt.xlabel('x')
    #plt.ylabel('y')
    #plt.show()
     
        
