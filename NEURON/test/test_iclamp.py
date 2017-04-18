import sys
import pickle
import time

import numpy as np

sys.path.append("..")

import libcell as lb
import saveClass as sc

from neuron import h

from main import SIM_currentSteps

import os
os.chdir("..")

def run_iclamp(iRange, run, nogui, vFileName):

    # Data saving object
    data = sc.emptyObject()

    # Simulation general parameters
    data.dt = 0.025
    lb.h.dt = data.dt
    lb.h.steps_per_ms = 1.0/lb.h.dt
    data.st_onset = 200.0
    data.st_duration = 200.
    data.TSTOP = 400


    # Simulation CONTROL
    data.model = 'L23'


    data.ACTIVE = True
    data.ACTIVEdend = True
    data.ACTIVEdendNa = True
    data.ACTIVEdendCa = True
    data.ACTIVEaxonSoma = True
    data.ACTIVEhotSpot = False             ##### Note: no hot spots!!!
    data.SYN = False
    data.SPINES = False
    data.ICLAMP = True
    data.NMDA = False
    data.GABA = False
    data.BGROUND = False

    model = lb.L23()
    print("Created cell: %s"%model.__class__)

    if data.SPINES: lb.addSpines(model)
    if data.ACTIVE: lb.init_active(model, axon=data.ACTIVEaxonSoma,
                                 soma=data.ACTIVEaxonSoma, dend=data.ACTIVEdend,
                                 dendNa=data.ACTIVEdendNa, dendCa=data.ACTIVEdendCa) 
    if data.ACTIVEhotSpot: lb.hotSpot(model)

    #data.iclampLoc = ['dend', 0.5, 28]
    data.iclampLoc = ['soma', 0.5]
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

    h('count=0')
    h('forall {print "--------------- ", secname() \n count=count+1 } ')
    h('print "Number of sections: ", count')
    
    if run:
        data.vdata, data.vDdata, data.gdata, data.idata, data.caDdata, data.vsec = [], [], [], [], [], []
        data.rates = []


        data.recordDend = False
        data.recordSec = True

        data.iRange = iRange
        print("Running current clamp simulation with parameters:")
        for k in sorted(data.__dict__.keys()):
            print("    %s:\t\t%s"%(k, data.__dict__[k]))
        SIM_currentSteps(data, model, data.iRange, data.BGROUND)

        modelData = sc.emptyObject()
        lb.props(modelData)

        tstamp = time.strftime("sim%Y%b%d_%H%M%S")
        tstamp = 'temp'

        dataList = [data, modelData]
        fname = './test/'+tstamp+'.pkl'
        f = open(fname, 'wb')
        pickle.dump(dataList, f)
        f.close()


        times = data.taxis

        vFile = open(vFileName, "w")
        for i in range(len(times)):
            vFile.write('%s'%(times[i]/1000.0))
            for vd in data.vdata:
                vFile.write('\t%s'%(vd[i]/1000.0))
            vFile.write('\n')


        vFile.close()
        print('Written traces to: %s'%vFileName)

        if not nogui:

            import matplotlib.pyplot as plt
            fig = plt.figure() 


            for volts in data.vdata:
                plt.plot(times, volts)
            fig.show()


        print("Done!")

    return model
    
    
if __name__ == "__main__":
    
    vFileName = './test/voltage.dat'
    nogui = '-nogui' in sys.argv
    iRange = np.arange(-0.1,0.8,0.1)
    if '-one' in sys.argv:
        iRange = np.array([0.7])
        vFileName = './test/voltage.one.dat'
        
    model = run_iclamp(iRange, True, nogui, vFileName)