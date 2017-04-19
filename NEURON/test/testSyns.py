#!/usr/bin/ipython -i

from neuron import *
from nrn import *

import sys
nogui = '-nogui' in sys.argv

h('objref p')
h('p = new PythonObject()')

h('objref nil')

def create_comp(name='soma'):
    
    h('create %s'%name)
    h('access %s'%name)

    h('nseg = 7')
    h('L = 9.26604')
    h('diam = 29.7838')

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

    h('insert pas')
    h('g_pas = 0.000142857142857')
    h('e_pas = -70')

    
    
    return h.cas() 


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


def dump_to_file(vdict, varlist, fname='/tmp/nrn_natnernst.dat', ):
    from numpy import savetxt, array

    vnames = ['t'] + varlist
    X = array([[v/1000. for v in vdict[x].to_python()] for x in vnames]).T
    savetxt(fname, X)


def run(tstop=10, dt=0.001):
    h.dt = dt
    h.finitialize()
    h.fcurrent()
    h.frecord_init()
    while h.t < tstop:
        h.fadvance()
        
        
def add_AMPAsyns(gmax=0.5, tau1=0.5, tau2=1):

    print "Adding syn..."
    print h.secname()
    gmax = gmax/1000.   # Set in nS and convert to muS
   
    h('psection()')
    h('objref ampa')
    h('objref nc_ampa')
    h('soma1 ampa = new Exp2Syn(0.5)')
    h('ampa.tau1 = %s'%tau1)
    h('ampa.tau2 = %s'%tau2)
    h('soma0 nc_ampa = new NetCon(&v(0.5), ampa, 0.0, 0.0, %s)'%gmax)
    
    h('psection()')
    
    return h.ampa
        
        
def add_GABAsyns(gmax=0.5, tau1=0.1, tau2=4,
                     rev=-75):

    print "Adding syn..."
    print h.secname()
    gmax = gmax/1000.   # Set in nS and convert to muS
   
    h('psection()')
    h('objref gaba')
    h('objref nc_gaba')
    h('soma2 gaba = new Exp2Syn(0.5)')
    h('gaba.tau1 = %s'%tau1)
    h('gaba.tau2 = %s'%tau2)
    h('gaba.e = %s'%rev)
    h('soma0 nc_gaba = new NetCon(&v(0.5), gaba, 0.0, 0.0, %s)'%gmax)
    
    h('psection()')
    
    return h.gaba
        
        
def add_NMDAsyns(gmax=0.5, tau1=2, tau2=20):

    print "Adding syn..."
    print h.secname()
    gmax = gmax/1000.   # Set in nS and convert to muS
   
    h('psection()')
    h('objref nmda')
    h('objref nc_nmda')
    h('soma3 nmda = new Exp2SynNMDA(0.5)')
    h('nmda.tau1 = %s'%tau1)
    h('nmda.tau2 = %s'%tau2)
    h('soma0 nc_nmda = new NetCon(&v(0.5), nmda, 0.0, 0.0, %s)'%gmax)
    
    h('psection()')
    
    return h.nmda


comp0 = create_comp('soma0')
comp1 = create_comp('soma1')
comp2 = create_comp('soma2')
comp3 = create_comp('soma3')

h.celsius = 35

inputs = []

stim = h.IClamp(0.5, sec=comp0)
stim.delay = 100
stim.dur = 10
stim.amp = 0.2
inputs.append(stim)

stim = h.IClamp(0.5, sec=comp0)
stim.delay = 300
stim.dur = 10
stim.amp = 0.2
inputs.append(stim)

stim = h.IClamp(0.5, sec=comp1)
stim.delay = 200
stim.dur = 500
stim.amp = 0.06
inputs.append(stim)

stim = h.IClamp(0.5, sec=comp2)
stim.delay = 200
stim.dur = 500
stim.amp = 0.06
inputs.append(stim)

stim = h.IClamp(0.5, sec=comp3)
stim.delay = 200
stim.dur = 500
stim.amp = 0.06
inputs.append(stim)

ampa1 = add_AMPAsyns()
gaba1 = add_GABAsyns()
nmda1 = add_NMDAsyns()


h('forall psection()')

varlist = ['v']
ds0 = create_dumps(comp0, varlist)
ds1 = create_dumps(comp1, varlist)
ds2 = create_dumps(comp2, varlist)
ds3 = create_dumps(comp3, varlist)

run(400, 0.01)

if not nogui:
    from pylab import show
    plot_timeseries(ds0, varlist)
    plot_timeseries(ds1, varlist)
    plot_timeseries(ds2, varlist)
    plot_timeseries(ds3, varlist)
    show()
    
dump_to_file(ds0, varlist, fname='v0.dat')
dump_to_file(ds1, varlist, fname='v1.dat')
dump_to_file(ds2, varlist, fname='v2.dat')
dump_to_file(ds3, varlist, fname='v3.dat')


if nogui:
    quit()
