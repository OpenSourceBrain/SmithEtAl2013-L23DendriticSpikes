# ----------------------------------------------------------
# Basic data display
#
# Tiago Branco, MRC Laboratory of Molecular Biology, 2013
# email: tbranco@mrc-lmb.cam.ac.uk
# ----------------------------------------------------------

import matplotlib
import numpy as np
import pickle
import matplotlib.pyplot as plt
from numpy.fft import *

#----------------------------------------------------------------------------
# Functions and Classes
class dataLoad:
    def __init__(self, input_path):
        input_file = open(input_path, 'rb')
        dataList = pickle.load(input_file)
        input_file.close()
        self.data = dataList[0]
        self.modelData = dataList[1]

def getSynTimes(dend, trial):
    locs = sim1.data.Elocs[:,0]
    times = sim1.data.all_Etimes[trial]
    i = (locs==dend).nonzero()   # Get synapses in dend
    i = np.ravel(i)
    synTimes = []
    for syn in i:
        ti = (times[:,0]==syn).nonzero()
        ti = np.ravel(ti)
        synTimes.append(times[ti,1])
    return synTimes

def plotSynTimes(synTimes):
    for item in synTimes:
        plt.plot(item, -80*np.ones(len(item)), 'k|')

def getNMDAi(dend, trial):
    locs = sim1.data.Elocs[:,0]
    nmda = sim1.data.idata[0][trial]
    i = (locs==dend).nonzero()   # Get synapses in dend
    i = np.ravel(i)
    NMDAi = []
    for syn in i:
        NMDAi.append(nmda[syn])
    return NMDAi

def plotNMDAi(NMDAi):
    for syn in NMDAi:
        plt.plot(sim1.data.taxis, syn*100)

def getTotalCa(dend, trial):
    ica = sim1.data.caDdata[0][trial][dend]
    NMDAi = getNMDAi(dend, trial)
    inmda = np.sum(np.array(NMDAi), 0)
    #totalCa = ica + inmda*0.1
    totalCa = ica # Hack for iNa
    kernel = np.exp(-sim1.data.taxis/50.)
    caT = np.convolve(kernel, -totalCa)
    return totalCa, caT.real 

def plotFigure(dends, trials):
    tr = 0
    ncol = len(trials)
    nrow = len(dends)+1
    t = sim1.data.taxis
    for trial in trials:
        plt.subplot2grid((nrow, ncol), (0,tr))
        plt.plot(t, sim1.data.vdata[0][trial], 'k')
        plt.text(0,0,str(trial))
        plt.ylim(-85,85)
        plt.xlim(150,550)
        #plt.axis('off')
        p = 1
        for dend in dends:
            synTimes = getSynTimes(dend,trial)
            totalCa, caT = getTotalCa(dend, trial)
            caT = caT[0:len(totalCa)]
            plt.subplot2grid((nrow, ncol), (p,tr))
            #plt.plot(t, sim1.data.vdata[0][trial],'k')
            plt.plot(t, sim1.data.vDdata[0][trial][dend],'b')
            plotSynTimes(synTimes)
            #plt.plot(t, caT*30, 'r')
            plt.plot(t, -totalCa/600*100-90, 'r')
            plt.ylim(-200,50)
            plt.xlim(150,550)
            plt.text(0,0,str(dend))
            #plt.axis('off')
            p = p+1            
        tr = tr+1 

#----------------------------------------------------------------------------
# Load data
sim1 = dataLoad('./temp.pkl')

#----------------------------------------------------------------------------
# Plot data
trials = [3]
dendList = [98, 71]
fig = plt.figure(); plotFigure(dendList, trials)
fig.show()














