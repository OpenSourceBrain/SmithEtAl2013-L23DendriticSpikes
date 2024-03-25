# ----------------------------------------------------------
# Main simulation control
#
# Tiago Branco, MRC Laboratory of Molecular Biology, 2013
# email: tbranco@mrc-lmb.cam.ac.uk
# ----------------------------------------------------------

import numpy as np
import pickle
import time

################################################################################
#     Removing dependency on Brian 1 as the class used, OfflinePoissonGroup is not compatible
#     with recent versions of Numpy. Using slightly modified OfflinePoissonGroup here.
#     See https://github.com/OpenSourceBrain/SmithEtAl2013-L23DendriticSpikes/issues/3
#
######import brian as br

from numpy.random import exponential, randint
from numpy import ones, cumsum, sum, isscalar

## Copied from https://github.com/brian-team/brian/blob/master/brian/directcontrol.py#L450
#  and changed: T * totalrate * 2  -> int(T * totalrate * 2)
class OfflinePoissonGroup(object): # This is weird, there is only an init method
    def __init__(self, N, rates, T):
        """
        Generates a Poisson group with N spike trains and given rates over the
        time window [0,T].
        """
        if isscalar(rates):
            rates = rates * ones(N)
        totalrate = sum(rates)
        isi = exponential(1 / totalrate, int(T * totalrate * 2))
        spikes = cumsum(isi)
        spikes = spikes[spikes <= T]
        neurons = randint(0, N, len(spikes))
        self.spiketimes = list(zip(neurons, spikes))

################################################################################

import libcell as lb
import saveClass as sc

#----------------------------------------------------------------------------
# Functions and Classes
def initOnsetSpikes():
    model.ncAMPAlist[0].event(data.st_onset)

def initSpikes():
    for s in data.etimes:
        model.ncAMPAlist[int(s[0])].event(float(s[1]))
        if data.NMDA: model.ncNMDAlist[int(s[0])].event(float(s[1]))
    if data.GABA == True:
        for s in data.itimes:
            model.ncGABAlist[int(s[0])].event(float(s[1]))

def storeSimOutput(data, v,vD,i,g,r,ca, vSec):
        data.vdata.append(v)
        data.vDdata.append(vD)
        data.idata.append(i)
        data.gdata.append(g)
        data.rates.append(r)
        data.caDdata.append(ca)
        data.vsec.append(vSec)

# Synapse location functions
def genRandomLocs(data, model, nsyn):
    locs = []
    for s in np.arange(0,nsyn):
        dend = np.random.randint(low=0, high=len(model.dends))
        pos = np.random.uniform()
        locs.append([dend, pos])
    return locs

# Input generation functions
def genPoissonInput(nsyn, rate, duration, onset):
    times = np.array([])
    while len(times.shape)<1 or times.shape[0]<2:
        P =  OfflinePoissonGroup(nsyn, rate, duration)
        times = np.array(P.spiketimes)
    times[:,1] = times[:,1] * 1000 + onset
    rates = 1./np.diff(np.array(P.spiketimes)[:,1]).mean()
    return times, rates

def genRandomFixedInput(nsyn, tInterval, onset):
    times = np.zeros([nsyn, 2])
    times[:,0] = np.arange(0, nsyn)
    np.random.shuffle(times[:,0])
    times[:,1] = np.arange(0, nsyn*tInterval, tInterval) + onset
    return times

def addBground(data, nsyn, Snsyn, rate, sTimes):
    P =  OfflinePoissonGroup(nsyn, rate, data.TSTOP)
    bTimes = np.array(P.spiketimes)
    bTimes[:,0] = bTimes[:,0] + Snsyn
    bTimes[:,1] = bTimes[:,1] * 1000
    times = np.vstack((bTimes, sTimes))
    return times

# Simulation functions
def sim_oneRandomInput(data, model, Ensyn, Insyn, Erate, Irate, bGround=False):
    soma_v, gdata, idata, Erates, Irates, dend_v, dend_ca, vSec = [], [], [], [], [], [], [], []
    data.all_Etimes, data.all_Itimes = [], []
    ETIMES = np.load('./etimes.npy', allow_pickle=True, encoding='latin1')
    ITIMES = np.load('./itimes.npy', allow_pickle=True, encoding='latin1')

    for trial in np.arange(0, data.TRIALS):
        # Generate input
        data.etimes, erates = genPoissonInput(Ensyn, Erate, data.st_duration,
                                              data.st_onset)
        data.itimes, irates = genPoissonInput(Insyn, Irate, data.st_duration,
                                              data.st_onset)
        Erates.append(erates)
        Irates.append(irates)
        if bGround:
            data.etimes = addBground(data, data.bEnsyn, Ensyn, data.EbGroundRate,
                                     data.etimes)
            data.itimes = addBground(data, data.bInsyn, Insyn, data.IbGroundRate,
                                     data.itimes)

        # Hack for freezing the input
        # Comment out to get random times
        data.etimes = ETIMES[trial]
        data.itimes = ITIMES[trial]

        # Run
        fih = lb.h.FInitializeHandler(1, initSpikes)
        taxis, v, vD, g, i, ca , vsec = lb.simulate(model, t_stop=data.TSTOP,
                                      NMDA=data.NMDA, recDend=data.recordDend, recSec=data.recordSec)

        # Store data
        soma_v.append(v)
        dend_v.append(vD)
        dend_ca.append(ca)
        vSec.append(vsec)
        data.all_Etimes.append(data.etimes)
        data.all_Itimes.append(data.itimes)
        if data.NMDA == True:
            #idata.append(np.sum(np.array(i).min(1)))
            idata.append(np.array(i))
            gdata.append(np.sum(np.array(g).max(1)))
    return taxis, soma_v, dend_v, Erates, gdata, idata, dend_ca, vSec


def SIM_rateIteration(data, model, rRange, bGround):
    for rate in rRange:
        print('Running E rate %s'% rate)

        print("Running rateIteration simulation with parameters:")
        for k in sorted(data.__dict__.keys()):
            print("    %s:\t\t%s"%(k, data.__dict__[k]))

        data.taxis, v, vD, r, g, i, ca, vsec = sim_oneRandomInput(data, model, data.Ensyn, data.Insyn, Erate=rate, Irate=rate, bGround=bGround)
        storeSimOutput(data, v,vD,i,g,r,ca,vsec)


def SIM_currentSteps(data, model, iRange, bGround=False):
    soma_v, r, idata, gdata = [], [], [], []
    if bGround:
        data.etimes = addBground(data, data.bEnsyn, data.Ensyn, data.EbGroundRate,
                                 [0,0])
        data.itimes = addBground(data, data.bInsyn, data.Insyn, data.IbGroundRate,
                                 [0,0])
        fih = lb.h.FInitializeHandler(1, initSpikes)
    for step in iRange:
        print("Running current step simulation with parameters:")
        for k in sorted(data.__dict__.keys()):
            print("    %s:\t\t%s"%(k, data.__dict__[k]))
        model.stim.amp = step
        taxis, v, vD, g, i, ca, vsec = lb.simulate(model, t_stop=data.TSTOP,
                                         NMDA=data.NMDA, recDend=data.recordDend)
        if data.NMDA == True:
            idata.append(np.sum(np.array(i).min(1)))
            gdata.append(np.sum(np.array(g).max(1)))
        storeSimOutput(data, v,vD,idata,gdata,r=0,ca=ca,vSec=vsec)
    data.taxis = taxis

#----------------------------------------------------------------------------
# Data saving object
data = sc.emptyObject()


def main(args=None):
    """Main"""


    # Simulation general parameters
    data.dt = 0.1
    lb.h.dt = data.dt
    lb.h.steps_per_ms = 1.0/lb.h.dt
    data.st_onset = 200.0
    data.st_duration = 200.
    data.TSTOP = 600
    data.TRIALS = 5
    data.Egmax = 1
    data.Igmax = 1
    data.Irev = -80
    data.Ensyn = 100
    data.Insyn = int(data.Ensyn*0.2)
    data.bEnsyn = 200
    data.bInsyn = int(data.bEnsyn*0.2)

    # Simulation CONTROL
    data.model = 'L23'
    data.locType = 'fixed'
    data.simType = 'rateIteration'
    data.fixedINPUT = False

    data.ACTIVE = True
    data.ACTIVEdend = True
    data.ACTIVEdendNa = True
    data.ACTIVEdendCa = True
    data.ACTIVEaxonSoma = True
    data.ACTIVEhotSpot = True
    data.SYN = True
    data.SPINES = False
    data.ICLAMP = False
    data.NMDA = True
    data.GABA = True
    data.BGROUND = True
    global model
    # Create neuron and add mechanisms
    if data.model == 'BS': model = lb.BS()
    if data.model == 'L23': model = lb.L23()
    if data.model == 'CELL': model = lb.CELL()
    if data.SPINES: lb.addSpines(model)
    if data.ACTIVE: lb.init_active(model, axon=data.ACTIVEaxonSoma,
                                 soma=data.ACTIVEaxonSoma, dend=data.ACTIVEdend,
                                 dendNa=data.ACTIVEdendNa, dendCa=data.ACTIVEdendCa)
    if data.ACTIVEhotSpot: lb.hotSpot(model)

    # Generate synapse locations
    if data.locType=='random':
        data.Elocs = genRandomLocs(data, model, data.Ensyn)
        data.Ilocs = genRandomLocs(data, model, data.Insyn)

    if data.locType=='fixed':
        loadElocs = np.load('./Elocs.npy')
        data.Elocs = loadElocs[0:data.Ensyn]
        loadIlocs = np.load('./Ilocs.npy')
        data.Ilocs = loadIlocs[0:data.Insyn]

    if data.BGROUND:
        data.bElocs = genRandomLocs(data, model, data.bEnsyn)
        data.bIlocs = genRandomLocs(data, model, data.bInsyn)
        data.Elocs = np.vstack((data.Elocs, data.bElocs))
        data.Ilocs = np.vstack((data.Ilocs, data.bIlocs))

        # Hack for freezing the background
        # Uncomment first 2 lines and comment out last 2 for
        # random background

        #data.bElocs = loadElocs[data.Ensyn+1:]
        #data.bIlocs = loadIlocs[data.Insyn+1:]
        data.Elocs = loadElocs
        data.Ilocs = loadIlocs

    # Insert synapses
    if data.SYN:
        lb.add_AMPAsyns(model, locs=data.Elocs, gmax=data.Egmax)
        if data.NMDA: lb.add_NMDAsyns(model, locs=data.Elocs, gmax=data.Egmax)
        if data.GABA: lb.add_GABAsyns(model, locs=data.Ilocs, gmax=data.Igmax,
                                  rev=data.Irev)

    # Insert IClamp
    data.iclampLoc = ['dend', 0.5, 28]
    data.iclampOnset = 50
    data.iclampDur = 250
    data.iclampAmp = 0

    if data.ICLAMP:
        if data.iclampLoc[0]=='soma':
            lb.add_somaStim(model, data.iclampLoc[1], onset=data.iclampOnset,
                            dur=data.iclampDur, amp=data.iclampAmp)
        if data.iclampLoc[0]=='dend':
            lb.add_dendStim(model, data.iclampLoc[1], data.iclampLoc[2],
                     onset=data.iclampOnset, dur=data.iclampDur, amp=data.iclampAmp)

    #----------------------------------------------------------------------------
    # Data storage lists
    data.vdata, data.vDdata, data.gdata, data.idata, data.caDdata, data.vsec = [], [], [], [], [], []
    data.rates = []

    #----------------------------------------------------------------------------
    # Run simulation

    # Specific parameters
    data.rateRange = np.arange(8,9,10)
    data.lagRange = np.arange(-100,110,10)
    data.iRange = np.arange(-0.1,0.2,0.1)
    data.singleRate = 51
    data.tInterval = 1
    data.EbGroundRate = 2
    data.IbGroundRate = 2
    data.recordDend = True
    data.recordSec = False

    if data.simType=='rateIteration':SIM_rateIteration(data, model, data.rateRange, data.BGROUND)
    if data.simType=='iSteps':SIM_currentSteps(data, model, data.iRange, data.BGROUND)


    #----------------------------------------------------------------------------
    # Save data
    modelData = sc.emptyObject()
    lb.props(modelData)

    tstamp = time.strftime("sim%Y%b%d_%H%M%S")
    tstamp = 'temp'

    dataList = [data, modelData]
    fname = './'+tstamp+'.pkl'
    f = open(fname, 'wb')
    pickle.dump(dataList, f)
    f.close()



if __name__ == "__main__":
    main()
