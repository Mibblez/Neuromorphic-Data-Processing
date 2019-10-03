import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from scipy.stats import norm
import csv
import os
from os import walk
from os import listdir
from os.path import isfile, join
from scipy.optimize import leastsq
from scipy.signal import savgol_filter
from scipy.signal import argrelextrema
from sklearn.metrics import pairwise_distances_argmin
from scipy import stats
import plotSpectrum
import getData
import scipy.fftpack
import pywt
import pywt.data
import math

'''
add comments pls

for i, thing in enumerate(things):
     https://treyhunner.com/2016/04/how-to-loop-with-indexes-in-python/

'''
def find_clusters(X, n_clusters, rseed=2):
    # 1. Randomly choose clusters
    rng = np.random.RandomState(rseed)
    i = rng.permutation(X.shape[0])[:n_clusters]
    centers = X[i]
    
    while True:
        # 2a. Assign labels based on closest center
        labels = pairwise_distances_argmin(X, centers)
        
        # 2b. Find new centers from means of points
        new_centers = np.array([X[labels == i].mean(0)
                                for i in range(n_clusters)])
        
        # 2c. Check for convergence
        if np.all(centers == new_centers):
            break
        centers = new_centers
    
    return centers, labels

def plotKmeans(data, axes, columnIndex):
    pts = []
    i =0
    for point in data:
        pts.append([i,point])
        i+=1
    pts = np.asarray(pts)
    centers, labels = find_clusters(pts,10)
    axes[1][columnIndex].scatter(pts[:, 0], pts[:, 1], c=labels, s=50, cmap='viridis')
    axes[1][columnIndex].scatter(centers[:, 0], centers[:, 1], c='red')

offFrequencies = []
onFrequencies = []
bothFrequencies = []

offGuas=[]
offLabel = []

onGuas=[]
onLabel = []

bothGuas=[]
bothLabel = []

folders = os.listdir("data/")

titles = ['Approximation', ' Horizontal detail',
          'Vertical detail', 'Diagonal detail']

#graphType = "savgol"
graphType = "hist"
#graphType = "wavelets"
#graphType = "kmeans"
logValues = True
guassianFitHistogrms = True

for folderName in folders:
    
    #folderName = "26hz_nopol Event Chunks"
    y_on,y_off,y_all, fileCount,x= getData.getData(folderName)

    onAvg = np.array(y_on).mean()
    offAvg = np.array(y_off).mean()
    allAvg = np.array(y_all).mean()

    if logValues:
        for i in range(len(y_on)):
            if y_on[i] == 0:
                y_on[i] = math.log10(onAvg)
            else:
                y_on[i] = math.log10(y_on[i])
        for i in range(len(y_off)):
            if y_off[i] == 0:
                y_off[i] = math.log10(offAvg)
            else:
                y_off[i] = math.log10(y_off[i])
        for i in range(len(y_all)):
            if y_all[i] == 0:
                y_all[i] = math.log10(allAvg)
            else:
                y_all[i] = math.log10(y_all[i])


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
    f.set_size_inches(15, 10.5)
    f.tight_layout()

    if graphType == 'hist':

        def paddBins(bins2):
            # pad left & right
            difference = bins2[1] - bins2[0]
            bins2= np.insert(bins2,0,bins2[0] -difference)
            bins2= np.insert(bins2,0,bins2[0] -(difference*2))
            bins2= np.insert(bins2,0,bins2[0] -(difference*3))
            bins2= np.insert(bins2,0,bins2[0] -(difference*4))

            bins2= np.append(bins2,bins2[len(bins2)-1]+difference )
            bins2= np.append(bins2,bins2[len(bins2)-1]+difference*2 )
            bins2= np.append(bins2,bins2[len(bins2)-1]+difference*3 )
            bins2= np.append(bins2,bins2[len(bins2)-1]+difference*4 )
            bins2= np.append(bins2,bins2[len(bins2)-1]+difference*5 )
            bins2= np.append(bins2,bins2[len(bins2)-1]+difference*6 )
            bins2= np.append(bins2,bins2[len(bins2)-1]+difference*7 )
            return bins2

        n, bins, patches = axes[1][0].hist(y_off, bins=25, color='red',edgecolor='black', linewidth=1.2, normed=1)

        if guassianFitHistogrms:
            bins= paddBins(bins)
            
            (mu, sigma) = norm.fit(y_off)
            y = mlab.normpdf( bins, mu, sigma)
            while(y[0] < 0.002):
                y =np.delete(y,0)
                bins = np.delete(bins,0)
            l = axes[1][0].plot(bins, y, linewidth=2)
            offGuas.append(l[0])
            offLabel.append(folderName + " Off Events")


        n, bins, patches =axes[1][1].hist(y_on,bins=25, color='green',edgecolor='black', linewidth=1.2, normed=1)
        if guassianFitHistogrms:
            bins= paddBins(bins)
            (mu, sigma) = norm.fit(y_on)
            y = mlab.normpdf( bins, mu, sigma)
            while(y[0] < 0.002):
                y =np.delete(y,0)
                bins = np.delete(bins,0)
            l = axes[1][1].plot(bins, y, linewidth=2)
            onGuas.append(l[0])
            onLabel.append(folderName + " On Events")
        n, bins, patches =axes[1][2].hist(y_all,bins=25, color='blue',edgecolor='black', linewidth=1.2, normed=1)
        if guassianFitHistogrms:
            bins =paddBins(bins)
            (mu, sigma) = norm.fit(y_all)
            y = mlab.normpdf( bins, mu, sigma)
            while(y[0] < 0.002):
                y =np.delete(y,0)
                bins = np.delete(bins,0)
            l = axes[1][2].plot(bins, y, linewidth=2)
            bothGuas.append(l[0])
            bothLabel.append(folderName + " Both Events")
    elif graphType == 'kmeans':
        
        plotKmeans(y_off, axes,0)
        plotKmeans(y_on, axes,1)
        plotKmeans(y_all, axes,2)

    elif graphType == "wavelets":
        data = []
        for i in range(fileCount):
            data.append([x[i], y_off[i]])
        print("")
        coeffs = pywt.dwt2(data, 'bior1.3')
        LL, (LH, HL, HH) = coeffs
        fig = plt.figure(figsize=(12, 3))
        for i, a in enumerate([LL, LH, HL, HH]):
            ax = fig.add_subplot(1, 4, i + 1)
            ax.imshow(a, interpolation="nearest", cmap=plt.cm.gray)
            ax.set_title(titles[i], fontsize=10)
            ax.set_xticks([])
            ax.set_yticks([])
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
    
    #print(coeff)
    #plt.show()


plt.show()




if graphType == "hist" and guassianFitHistogrms:
    f, axes = plt.subplots(nrows = 2, ncols = 3, sharex=False, sharey = False )
    f.set_size_inches(15, 10.5)
    f.tight_layout()
    def showAllGuas(lines, labels, axesIndex):
        
        i =0
        for line in lines:
            j =0
            shiftX = line._x[0]
            for x in line._x:
                line._x[j] = x - shiftX
                j+=1
            j=0
            shiftY = line._y[0]
            for y in line._y:
                line._y[j] = y - shiftY
                j+=1
            row = 0
            if "NoPolarizer" in labels[i]:
                row = 1
            axes[row][axesIndex].plot(line._x,line._y, label=labels[i])
            i+=1
        axes[0][axesIndex].legend(loc=1, prop={'size': 7})
        axes[1][axesIndex].legend(loc=1, prop={'size': 7})
    showAllGuas(offGuas, offLabel,0)
    showAllGuas(onGuas, onLabel,1)
    showAllGuas(bothGuas, bothLabel,2)
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

