#!/usr/bin/ipython -i

from neuron import *
from nrn import *

import sys
nogui = '-nogui' in sys.argv

def create_comp(name='soma'):
    comp = h.Section(name)

    comp.nseg = 7
    comp.L = 9.26604
    comp.diam = 29.7838

    '''
    comp.insert('na')
    comp.gbar_na = 1000.0
    comp.ena = 60

    comp.insert('km')
    comp.gbar_km = 2.2
    comp.ek = -90

    comp.insert('kv')
    comp.gbar_kv = 100.0
    comp.ek = -90

    comp.insert('ca')
    comp.gbar_ca = 0.5
    comp.eca = 140.0

    comp.insert('kca')
    comp.gbar_kca = 3.0
    comp.ek = -90

    comp.insert('it')
    comp.gbar_it = 0.0003
    comp.eca = 140.0'''

    comp.insert('pas')
    comp.g_pas = 0.000142857142857
    comp.e_pas = -75

    comp.push()
    h.psection()

    return comp


def plot_timeseries(vdict, varlist):
    from pylab import plot, show, figure, title
    t = vdict['t']
    for n in varlist:
        figure()
        plot(t, vdict[n], label=n)
        title(n)


def create_dumps(section, varlist):
    recordings = {n: h.Vector() for n in varlist}

    for (vn, v) in recordings.iteritems():
        v.record(section(0.5).__getattribute__('_ref_' + vn))

    recordings['t'] = h.Vector()
    recordings['t'].record(h._ref_t)
    return recordings


def dump_to_file(vdict, varlist, fname='/tmp/nrn_natnernst.dat'):
    from numpy import savetxt, array

    vnames = ['t'] + varlist
    X = array([vdict[x].to_python() for x in vnames]).T
    savetxt(fname, X)


def run(tstop=10, dt=0.001):
    h.dt = dt
    h.finitialize()
    h.fcurrent()
    h.frecord_init()
    while h.t < tstop:
        h.fadvance()
        
        
def add_AMPAsyns(comp, gmax=0.5, tau1=0.5, tau2=1):

    
    gmax = gmax/1000.   # Set in nS and convert to muS
   
    AMPA = h.Exp2Syn(0.5, sec=comp) 
    AMPA.tau1 = tau1
    AMPA.tau2 = tau2
    
    
    return AMPA

comp0 = create_comp('soma0')
comp1 = create_comp('soma1')
comp2 = create_comp('soma2')
comp3 = create_comp('soma3')

h.celsius = 35

inputs = []

stim = h.IClamp(0.5, sec=comp0)
stim.delay = 100
stim.dur = 100
stim.amp = 0.1
inputs.append(stim)

ampa1 = add_AMPAsyns(comp1)

print ampa1

h('forall psection()')

varlist = ['v']
ds0 = create_dumps(comp0, varlist)
ds1 = create_dumps(comp1, varlist)

run(300, 0.001)

if not nogui:
    from pylab import show
    plot_timeseries(ds0, varlist)
    plot_timeseries(ds1, varlist)
    show()
    
dump_to_file(ds0, varlist, fname='c0.dat')
dump_to_file(ds1, varlist, fname='c1.dat')


if nogui:
    quit()
