import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib
from scipy.stats import norm
import csv
import os
from os import walk
from os import listdir
from os.path import isfile, join
from scipy.optimize import leastsq
from scipy.signal import savgol_filter
from scipy.signal import argrelextrema
import plotSpectrum
import getPlottingData
import scipy.fftpack
import pywt
import pywt.data
import math
from natsort import natsorted, ns
import plotting_helper
from typing import List

class OnOffBothLines:
    on:matplotlib.lines.Line2D = None
    off:matplotlib.lines.Line2D = None
    both:matplotlib.lines.Line2D = None

class Waveforms:
    sine: List[OnOffBothLines] =[]
    square: List[OnOffBothLines] = []
    burst: List[OnOffBothLines] = []
    triangle: List[OnOffBothLines] = []
    dc: List[OnOffBothLines] = []


if not os.path.exists(os.path.join("results","EventChunkGraphs")):
    os.makedirs(os.path.join("results","EventChunkGraphs"))
    os.makedirs(os.path.join("results","EventChunkGraphs","Dots"))



offFrequencies = []
onFrequencies = []
bothFrequencies = []

offGuas=[]
offLabel = []

onGuas=[]
onLabel = []

bothGuas=[]
bothLabel = []



titles = ['Approximation', ' Horizontal detail',
          'Vertical detail', 'Diagonal detail']

#graphType = "savgol"
graphType = "hist"
#graphType = "wavelets"
#graphType = "kmeans"
#graphType = "smooth"

plotVariance = True
plotFWHM = True
logValues = False
differentFrequencies = True # different frequencies =True or backgrounds= False
waveformsAndFrequency = True
plotWaveformsOrFrequency = "waveforms"
saveFigures = True

#variance Arrays
allOffVarPol =[]
allOnVarPol = []
allBothVarPol = []
allOffVarNoPol =[]
allOnVarNoPol = []
allBothVarNoPol = []
polLabels = []
noPolLabels = []


#FWHM Arrays
allOffFWHMPol =[]
allOnFWHMPol = []
allBothFWHMPol = []
allOffFWHMNoPol =[]
allOnFWHMNoPol = []
allBothFWHMNoPol = []

#Kmeans Arrays
allKMeansPolOn = []
allKMeansPolOff = []
allKMeansPolBoth = []
allKMeansNoPolOn = []
allKMeansNoPolOff = []
allKMeansNoPolBoth = []
#allKMeansNoPolLabels = []

waveforms = Waveforms()

data_folder = 'waveformsAndFrequency'
folders = os.listdir(f'data/{data_folder}')
folders = natsorted(folders, alg=ns.IGNORECASE)
for folderName in folders:
    
    #folderName = "26hz_nopol Event Chunks"
    y_on,y_off,y_all, fileCount,x= getPlottingData.getData(f'{data_folder}/{folderName}')  

    if logValues:
        onAvg = np.array(y_on).mean()
        offAvg = np.array(y_off).mean()
        allAvg = np.array(y_all).mean()
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
    folderName = folderName.replace('30deg','')
    folderName = folderName.replace('30 deg','')
    if differentFrequencies:
        folderName = folderName.replace('foam ','')
    else:
        folderName = folderName.replace('10hz ','')
        folderName = folderName.replace('10 hz ','')
        folderName = folderName.replace('18hz ','')
        folderName = folderName.replace('18 hz ','')
    print(folderName)
   
    f, axes = plt.subplots(nrows = 2, ncols = 3, sharex=False, sharey = False )
    f.set_size_inches(15, 9.5)
    f.tight_layout()

    if graphType == 'hist':

        lines = OnOffBothLines()

        # Off events
        l = plotting_helper.plot_hist(y_off, axes, 1, 0, 'red', logValues)
        l.remove()
        offGuas.append(l)
        lines.off = l

        # On Events
        l = plotting_helper.plot_hist(y_on, axes, 1, 1, 'green', logValues)
        l.remove()
        onGuas.append(l)
        lines.on = l

        # On & Off Events
        l = plotting_helper.plot_hist(y_all, axes, 1, 2, 'blue', logValues)
        l.remove()
        bothGuas.append(l)
        lines.both = l

        if differentFrequencies:
            if "sine" in folderName:
                waveforms.sine.append(lines)
            elif "square"  in folderName:
                waveforms.square.append(lines)
            elif "triangle" in folderName:
                waveforms.triangle.append(lines)
            elif "burst" in folderName:
                waveforms.burst.append(lines)

            
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
    elif graphType == "smooth":
        axes[1][0].set_ylim(yOffSmoothed.min(),yOffSmoothed.max()+10)
        axes[1][1].set_ylim(yOnSmoothed.min(),yOnSmoothed.max()+10)
        axes[1][2].scatter(x,yBothSmoothed,c='blue',picker=True, s=1)
        axes[1][0].scatter(x,yOffSmoothed,c='red',picker=True, s=1)
        axes[1][1].scatter(x,yOnSmoothed,c='green',picker=True, s=1)

        yOffSmoothed = savgol_filter(y_off, 71, 3)
        yOnSmoothed  =  savgol_filter(y_on, 71, 3)
        yBothSmoothed = savgol_filter(y_all, 71,3)

        # Smooth data
        yf = scipy.fftpack.fft(yOffSmoothed)
        offFrequencies.append(yf)
        onFrequencies.append(scipy.fftpack.fft(yOnSmoothed))
        bothFrequencies.append(scipy.fftpack.fft(yBothSmoothed))
    
    offLabel.append(folderName + " Off Events")
    onLabel.append(folderName + " On Events")
    bothLabel.append(folderName + " All Events")

    axes[0][0].scatter(x,y_off,c='red',picker=True,s=1)

    axes[1][0].title.set_text(folderName +" Off Events")
    axes[0][1].scatter(x,y_on,c='green',picker=True,s=1)
    axes[1][1].title.set_text(folderName +" On Events")

    axes[0][2].scatter(x,y_all,c='blue',picker=True,s=1)
    plt.title(folderName +" All Events")
    

    if 'NoPolarizer' in folderName:
        noPolLabels.append(folderName.replace("NoPolarizer",""))
    else:
        polLabels.append(folderName) 


    if plotVariance:
        if 'NoPolarizer' in folderName:
            allOffVarNoPol.append(np.var(y_off))
            allOnVarNoPol.append(np.var(y_on))
            allBothVarNoPol.append(np.var(y_all))
        else:
            allOffVarPol.append(np.var(y_off))
            allOnVarPol.append(np.var(y_on))
            allBothVarPol.append(np.var(y_all))

    if plotFWHM:
        if 'NoPolarizer' in folderName:
            allOffFWHMNoPol.append(2.355*np.std(y_off))
            allOnFWHMNoPol.append(2.355*np.std(y_on))
            allBothFWHMNoPol.append(2.355*np.std(y_all))
        else:
            allOffFWHMPol.append(2.355*np.std(y_off))
            allOnFWHMPol.append(2.355*np.std(y_on))
            allBothFWHMPol.append(2.355*np.std(y_all))
    
    if saveFigures:
        plt.savefig(os.path.join("results","EventChunkGraphs","Dots",folderName+'Dots.png'))


if saveFigures == False:
    plt.show()

if graphType == "hist":
    
    if waveformsAndFrequency:
        if plotWaveformsOrFrequency == "waveforms":
            f, axes = plt.subplots(nrows = 3, ncols = 2, sharex=False, sharey = False )
            f.set_size_inches(10, 15)
            offEvents = [waveforms.sine[0].off, waveforms.square[0].off, waveforms.burst[0].off,waveforms.triangle[0].off]
            onEvents = [waveforms.sine[0].on, waveforms.square[0].on, waveforms.burst[0].on,waveforms.triangle[0].on]
            bothEvents = [waveforms.sine[0].both, waveforms.square[0].both, waveforms.burst[0].both,waveforms.triangle[0].both]
            plotting_helper.showAllGuas(offEvents, ["Sine","Square","Burst","Triangle"],0, "Off Events 200mV", axes)
            plotting_helper.showAllGuas(onEvents, ["Sine","Square","Burst","Triangle"],1, "On Events 200mV", axes)
            plotting_helper.showAllGuas(bothEvents, ["Sine","Square","Burst","Triangle"],2, "Combined Events 200mV", axes)
            if saveFigures:
                plt.savefig(os.path.join("results","EventChunkGraphs",'CenterGaus 200mV.png'))  
            else:
                plt.show()

            f, axes = plt.subplots(nrows = 3, ncols = 2, sharex=False, sharey = False )
            f.set_size_inches(10, 15)
            offEvents = [waveforms.sine[1].off, waveforms.square[1].off, waveforms.burst[1].off,waveforms.triangle[1].off]
            onEvents = [waveforms.sine[1].on, waveforms.square[1].on, waveforms.burst[1].on,waveforms.triangle[1].on]
            bothEvents = [waveforms.sine[1].both, waveforms.square[1].both, waveforms.burst[1].both,waveforms.triangle[1].both]
            plotting_helper.showAllGuas(offEvents, ["Sine","Square","Burst","Triangle"],0, "Off Events 300mV", axes)
            plotting_helper.showAllGuas(onEvents, ["Sine","Square","Burst","Triangle"],1, "On Events 300mV", axes)
            plotting_helper.showAllGuas(bothEvents, ["Sine","Square","Burst","Triangle"],2, "Combined Events 300mV", axes)
            if saveFigures:
                plt.savefig(os.path.join("results","EventChunkGraphs",'CenterGaus 300mV.png'))  
            else:
                plt.show()
            
            f, axes = plt.subplots(nrows = 3, ncols = 2, sharex=False, sharey = False )
            f.set_size_inches(10, 15)
            offEvents = [waveforms.sine[2].off, waveforms.square[2].off, waveforms.burst[2].off,waveforms.triangle[2].off]
            onEvents = [waveforms.sine[2].on, waveforms.square[2].on, waveforms.burst[2].on,waveforms.triangle[2].on]
            bothEvents = [waveforms.sine[2].both, waveforms.square[2].both, waveforms.burst[2].both,waveforms.triangle[2].both]
            plotting_helper.showAllGuas(offEvents, ["Sine","Square","Burst","Triangle"],0, "Off Events 400mV", axes)
            plotting_helper.showAllGuas(onEvents, ["Sine","Square","Burst","Triangle"],1, "On Events 400mV", axes)
            plotting_helper.showAllGuas(bothEvents, ["Sine","Square","Burst","Triangle"],2, "Combined Events 400mV", axes)
            if saveFigures:
                plt.savefig(os.path.join("results","EventChunkGraphs",'CenterGaus 400mV.png'))  
            else:
                plt.show()
            
            f, axes = plt.subplots(nrows = 3, ncols = 2, sharex=False, sharey = False )
            f.set_size_inches(10, 15)
            offEvents = [waveforms.sine[3].off, waveforms.square[3].off, waveforms.burst[3].off,waveforms.triangle[3].off]
            onEvents = [waveforms.sine[3].on, waveforms.square[3].on, waveforms.burst[3].on,waveforms.triangle[3].on]
            bothEvents = [waveforms.sine[3].both, waveforms.square[3].both, waveforms.burst[3].both,waveforms.triangle[3].both]
            plotting_helper.showAllGuas(offEvents, ["Sine","Square","Burst","Triangle"],0, "Off Events 500mV", axes)
            plotting_helper.showAllGuas(onEvents, ["Sine","Square","Burst","Triangle"],1, "Off Events 500mV", axes)
            plotting_helper.showAllGuas(bothEvents, ["Sine","Square","Burst","Triangle"],2, "Off Events 500mV", axes)
            if saveFigures:
                plt.savefig(os.path.join("results","EventChunkGraphs",'CenterGaus 500mV.png'))  
            else:
                plt.show()
    else:
        f, axes = plt.subplots(nrows = 3, ncols = 2, sharex=False, sharey = False )
        f.set_size_inches(10, 15)
    
        
        plotting_helper.showAllGuas(offGuas, np.copy(offLabel),0, "Off Events", axes)
        plotting_helper.showAllGuas(onGuas, np.copy(onLabel),1, "On Events", axes)
        plotting_helper.showAllGuas(bothGuas, np.copy(bothLabel),2, "Both Events", axes)
        if saveFigures:
            plt.savefig(os.path.join("results","EventChunkGraphs",'Gaus.png'))  
        else:
            plt.show()
        f, axes = plt.subplots(nrows = 3, ncols = 2, sharex=False, sharey = False )
        f.set_size_inches(10, 15)


        plotting_helper.centerAllGuas(offGuas,0,offLabel, "Off Events",axes)
        plotting_helper.centerAllGuas(onGuas,1, onLabel, "On Events",axes)
        plotting_helper.centerAllGuas(bothGuas,2, bothLabel, "Both Events",axes)
        if saveFigures:
            plt.savefig(os.path.join("results","EventChunkGraphs",'CenterGaus.png'))  
        else:
            plt.show()
    
            
if plotVariance:
    figureVar, axesVar = plt.subplots(nrows = 3, ncols = 2, sharex=False, sharey = False )
    figureVar.set_size_inches(10, 15)
    axesVar[0][0].set_title("Off Events Polarized Variance" + (" Log" if logValues else ""), fontsize=10)
    axesVar[0][0].bar(polLabels, allOffVarPol)
    axesVar[0][0].tick_params(axis='x', which='major', labelsize=10, labelrotation=35)

    axesVar[1][0].set_title("On Events Polarized Variance" + (" Log" if logValues else ""), fontsize=10)
    axesVar[1][0].bar(polLabels, allOnVarPol)
    axesVar[1][0].tick_params(axis='x', which='major', labelsize=10, labelrotation=35)

    axesVar[2][0].set_title("Both Events Polarized Variance" + (" Log" if logValues else ""), fontsize=10)
    axesVar[2][0].bar(polLabels, allBothVarPol)
    axesVar[2][0].tick_params(axis='x', which='major', labelsize=10, labelrotation=35)

    axesVar[0][1].set_title("Off Events Not Polarized Variance" + (" Log" if logValues else ""), fontsize=10)
    axesVar[0][1].bar(noPolLabels, allOffVarNoPol, color='red')
    axesVar[0][1].tick_params(axis='x', which='major', labelsize=10, labelrotation=35)

    axesVar[1][1].set_title("On Events Not Polarized Variance" + (" Log" if logValues else ""), fontsize=10)
    axesVar[1][1].bar(noPolLabels, allOnVarNoPol, color='red')
    axesVar[1][1].tick_params(axis='x', which='major', labelsize=10, labelrotation=35)

    axesVar[2][1].set_title("Both Events Not Polarized Variance" + (" Log" if logValues else ""), fontsize=10)
    axesVar[2][1].bar(noPolLabels, allBothVarNoPol, color='red')
    axesVar[2][1].tick_params(axis='x', which='major', labelsize=10, labelrotation=35)

    plt.subplots_adjust(left=.125, bottom=0.1, right=.91, top=.9, wspace=.3, hspace=.4)
    #figureVar.xticks(range(len(allOffVarPol)), polLabels)
    if saveFigures:
        plt.savefig(os.path.join("results","EventChunkGraphs","variance.png"))
    else:
        plt.show()

if plotFWHM:
    figureVar, axesVar = plt.subplots(nrows = 3, ncols = 2, sharex=False, sharey = False )
    figureVar.set_size_inches(10, 15)
    axesVar[0][0].set_title("Off Events Polarized FWHM" + (" Log" if logValues else ""), fontsize=10)
    axesVar[0][0].bar(polLabels, allOffFWHMPol)
    axesVar[0][0].tick_params(axis='x', which='major', labelsize=10, labelrotation=35)

    axesVar[1][0].set_title("On Events Polarized FWHM" + (" Log" if logValues else ""), fontsize=10)
    axesVar[1][0].bar(polLabels, allOnFWHMPol)
    axesVar[1][0].tick_params(axis='x', which='major', labelsize=10, labelrotation=35)

    axesVar[2][0].set_title("Both Events Polarized FWHM" + (" Log" if logValues else ""), fontsize=10)
    axesVar[2][0].bar(polLabels, allBothFWHMPol)
    axesVar[2][0].tick_params(axis='x', which='major', labelsize=10, labelrotation=35)

    axesVar[0][1].set_title("Off Events Not Polarized FWHM" + (" Log" if logValues else ""), fontsize=10)
    axesVar[0][1].bar(noPolLabels, allOffFWHMNoPol, color='red')
    axesVar[0][1].tick_params(axis='x', which='major', labelsize=10, labelrotation=35)

    axesVar[1][1].set_title("On Events Not Polarized FWHM" + (" Log" if logValues else ""), fontsize=10)
    axesVar[1][1].bar(noPolLabels, allOnFWHMNoPol, color='red')
    axesVar[1][1].tick_params(axis='x', which='major', labelsize=10, labelrotation=35)

    axesVar[2][1].set_title("Both Events Not Polarized FWHM" + (" Log" if logValues else ""), fontsize=10)
    axesVar[2][1].bar(noPolLabels, allBothFWHMNoPol, color='red')
    axesVar[2][1].tick_params(axis='x', which='major', labelsize=10, labelrotation=35)

    plt.subplots_adjust(left=.125, bottom=0.1, right=.91, top=.9, wspace=.3, hspace=.4)
    #figureVar.xticks(range(len(allOffVarPol)), polLabels)
    if saveFigures:
        plt.savefig(os.path.join("results","EventChunkGraphs","FWHM.png"))
    else:
        plt.show()

if graphType == "smooth":
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
        #axes[0].set_ylim(0,50)
        axes[0].legend()



        index = 0
        for y in noPolFreq:
            axes[1].plot(fftX, 2.0/fileCount * np.abs(y[:fileCount//2]), label= noPolLabels[index].replace('Event Chunks', ''))
            index+=1

        axes[1].set_xlim(2,60)
        #axes[1].set_ylim(0,50)
        axes[1].legend()
        plt.show()

    showFFT(offFrequencies)
    showFFT(onFrequencies)
    showFFT(bothFrequencies)

if saveFigures == False:
    input()

