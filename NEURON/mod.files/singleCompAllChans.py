#!/usr/bin/ipython -i

from neuron import *
from nrn import *

def create_comp(name='soma'):
    comp = h.Section(name)

    comp.nseg = 7
    comp.L = 9.26604
    comp.diam = 29.7838

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
    comp.eca = 140.0

    comp.insert('pas')
    comp.g_pas = 0.000142857142857
    comp.e_pas = -75



    return comp


def plot_timeseries(vdict, varlist):
    from pylab import plot, show, figure, title
    t = vdict['t']
    for n in varlist:
        figure()
        plot(t, vdict[n], label=n)
        title(n)

    show()

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

comp = create_comp('soma')
h.celsius = 35

inputs = []

stim = h.IClamp(0.5, sec=comp)
stim.delay = 100
stim.dur = 100
stim.amp = -0.01
inputs.append(stim)

stim = h.IClamp(0.5, sec=comp)
stim.delay = 300
stim.dur = 100
stim.amp = 0.05
inputs.append(stim)



varlist = ['v']#, 'ica', 'cai']
ds = create_dumps(comp, varlist)

run(600, 0.001)

plot_timeseries(ds, varlist)
dump_to_file(ds, varlist)
