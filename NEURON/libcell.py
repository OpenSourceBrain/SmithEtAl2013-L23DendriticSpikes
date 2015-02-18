# ----------------------------------------------------------
# Library of cell classes and functions
#
# Tiago Branco, MRC Laboratory of Molecular Biology, 2013
# email: tbranco@mrc-lmb.cam.ac.uk
# ----------------------------------------------------------

import numpy as np
import neuron

from neuron import h
from neuron import load_mechanisms
from neuron import gui

load_mechanisms('/directory_where_mod_files_have_been_compiled')
h('objref nil')

# ----------------------------------------------------------
# MODELS
class L23(object):

    # Cell morphology is from cat, all lengths and diameters
    # are scaled to 70% to approximate it to mouse values

    def __init__(self):
        h('xopen("./L23.hoc")')
        props(self)
        self._geom()
        self._topol()
        self._changeLength()
        self._biophys()

    def _geom(self):
        self.axon = h.Section()
        self.axon.L = 300
        self.axon.diam = 1

    def _topol(self):            
        self.soma = h.soma
        self.dends = []
        for sec in h.allsec():
            self.dends.append(sec)
            sec.nseg = 7
        self.dends.pop()   # Remove soma from the list
        self.dends.pop()   # and the Axon
        for sec in self.dends:
            sec.diam = sec.diam * 0.7
        self.axon.connect(self.soma,1,0)
    
    def _biophys(self):
        for sec in h.allsec():
            sec.cm = self.CM
            sec.insert('pas')
            sec.e_pas = self.E_PAS
            sec.g_pas = 1.0/self.RM
            sec.Ra = self.RA

    def _changeLength(self):
        for sec in h.allsec():
            sec.L = sec.L * 0.7


# ----------------------------------------------------------
# INSTRUMENTATION FUNCTIONS
def props(model):

    # Passive properties
    model.CM = 1.0
    model.RM = 7000.0
    model.RA = 100.0 
    model.E_PAS = -75
    model.CELSIUS = 35

    # Active properties
    model.Ek = -90
    model.Ena = 60
    model.Eca = 140
    
    model.gna_axon = 1000
    model.gkv_axon = 100
    
    model.gna_soma = 1000
    model.gkv_soma = 100 
    model.gkm_soma = 2.2 
    model.gkca_soma = 3 
    model.gca_soma = 0.5 
    model.git_soma = 0.0003 
    
    model.gna_dend = 80
    model.gna_dend_hotSpot = 600
    model.gkv_dend = 3
    model.gkm_dend = 1
    model.gkca_dend = 3
    model.gca_dend = 0.5
    model.git_dend = 0.00015 
    model.gh_dend = 0

def init_active(model, axon=False, soma=False, dend=True, dendNa=False,
                dendCa=False):
    if axon:
        model.axon.insert('na'); model.axon.gbar_na = model.gna_axon
        model.axon.insert('kv'); model.axon.gbar_kv = model.gkv_axon
        model.axon.ena = model.Ena
        model.axon.ek = model.Ek

    if soma:
        model.soma.insert('na'); model.soma.gbar_na = model.gna_soma
        model.soma.insert('kv'); model.soma.gbar_kv = model.gkv_soma
        model.soma.insert('km'); model.soma.gbar_km = model.gkm_soma
        model.soma.insert('kca'); model.soma.gbar_kca = model.gkca_soma
        model.soma.insert('ca'); model.soma.gbar_ca = model.gca_soma
        model.soma.insert('it'); model.soma.gbar_it = model.git_soma
        #model.soma.insert('cad');
        model.soma.ena = model.Ena
        model.soma.ek = model.Ek
        model.soma.eca = model.Eca

    if dend:
        for d in model.dends:
            d.insert('na'); d.gbar_na = model.gna_dend*dendNa
            d.insert('kv'); d.gbar_kv = model.gkv_dend
            d.insert('km'); d.gbar_km = model.gkm_dend
            d.insert('kca'); d.gbar_kca = model.gkca_dend
            d.insert('ca'); d.gbar_ca = model.gca_dend*dendCa
            d.insert('it'); d.gbar_it = model.git_dend*dendCa
            #d.insert('cad')
            d.ena = model.Ena
            d.ek = model.Ek
            d.eca = model.Eca

def add_somaStim(model, p=0.5, onset=20, dur=1, amp=0):
    model.stim = h.IClamp(model.soma(p))
    model.stim.delay = onset
    model.stim.dur = dur
    model.stim.amp = amp    # nA
    
def add_dendStim(model, p=0.5, dend=10, onset=20, dur=1, amp=0):
    model.stim = h.IClamp(model.dends[dend](p))
    model.stim.delay = onset
    model.stim.dur = dur
    model.stim.amp = amp    # nA

def add_AMPAsyns(model, locs=[[0, 0.5]], gmax=0.5, tau1=0.5, tau2=1):
    model.AMPAlist = []
    model.ncAMPAlist = []
    gmax = gmax/1000.   # Set in nS and convert to muS
    for loc in locs:
        AMPA = h.Exp2Syn(float(loc[1]), sec=model.dends[int(loc[0])]) 
        AMPA.tau1 = tau1
        AMPA.tau2 = tau2
        NC = h.NetCon(h.nil, AMPA, 0, 0, gmax)
        model.AMPAlist.append(AMPA)
        model.ncAMPAlist.append(NC)

def add_NMDAsyns(model, locs=[[0, 0.5]], gmax=0.5, tau1=2, tau2=20):
    model.NMDAlist = []
    model.ncNMDAlist = []
    gmax = gmax/1000.   # Set in nS and convert to muS
    for loc in locs:
        NMDA = h.Exp2SynNMDA(float(loc[1]), sec=model.dends[int(loc[0])]) 
        NMDA.tau1 = tau1
        NMDA.tau2 = tau2
        NC = h.NetCon(h.nil, NMDA, 0, 0, gmax)
        x = float(loc[1])
        model.NMDAlist.append(NMDA)
        model.ncNMDAlist.append(NC)   

def add_GABAsyns(model, locs=[[0, 0.5]], gmax=0.5, tau1=0.1, tau2=4,
                     rev=-75):
    model.GABAlist = []
    model.ncGABAlist = []
    gmax = gmax/1000.   # Set in nS and convert to muS
    for loc in locs:
        GABA = h.Exp2Syn(float(loc[1]), sec=model.dends[int(loc[0])]) 
        GABA.tau1 = tau1
        GABA.tau2 = tau2
        GABA.e = rev
        NC = h.NetCon(h.nil, GABA, 0, 0, gmax)
        model.GABAlist.append(GABA)
        model.ncGABAlist.append(NC)

def addSpines(model):
    for sec in model.dends:
        sec.cm = model.CM*1.5
        sec.g_pas = 1.0/(model.RM/1.5)

def hotSpot(model):
    spot = np.ceil(7/2.)
    for section in model.dends:
        s = 0
        for seg in section:
            if s==spot:
                seg.gbar_na = model.gna_dend_hotSpot    
            else:
                seg.gbar_na = 0
            s+=1 

# ----------------------------------------------------------
# SIMULATION RUN
def simulate(model, t_stop=100, NMDA=False, recDend=False, recSec=False):
    trec, vrec = h.Vector(), h.Vector()
    gRec, iRec, vDendRec, caDendRec, vSecRec = [], [], [], [], []
    gNMDA_rec, iNMDA_rec = [], []
    trec.record(h._ref_t)
    vrec.record(model.soma(0.5)._ref_v)

    if NMDA:        
        for n in np.arange(0, len(model.NMDAlist)):
            loc = model.NMDAlist[n].get_loc()
            h.pop_section()                        
            gNMDA_rec.append(h.Vector())
            iNMDA_rec.append(h.Vector())
            gNMDA_rec[n].record(model.NMDAlist[n]._ref_g)
            iNMDA_rec[n].record(model.NMDAlist[n]._ref_i)
        gRec.append(gNMDA_rec)
        iRec.append(iNMDA_rec)
    if recDend:
        n = 0
        for dend in model.dends:
            vDendRec.append(h.Vector())
            caDendRec.append(h.Vector())
            vDendRec[n].record(dend(0.6)._ref_v)
            #caDendRec[n].record(dend(0.2)._ref_ica)
            caDendRec[n].record(dend(0.6)._ref_gna_na) # Hacked to get iNa
            n+=1
    if recSec:
        n = 0
        for sec in h.allsec():
            for seg in sec.allseg():
                vSecRec.append(h.Vector())
                vSecRec[n].record(seg._ref_v)
                n+=1

    h.celsius = model.CELSIUS
    h.finitialize(model.E_PAS)
    neuron.run(t_stop)
    return np.array(trec), np.array(vrec), np.array(vDendRec), gNMDA_rec, iNMDA_rec, np.array(caDendRec), np.array(vSecRec)




 












      
