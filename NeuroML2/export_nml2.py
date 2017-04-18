from pyneuroml.neuron import export_to_neuroml2

import sys
import os

os.chdir("../NEURON/test")
sys.path.append(".")

export_to_neuroml2("load_l23.hoc", 
                   "../NeuroML2/L23_morph.cell.nml", 
                   includeBiophysicalProperties=False,
                   known_rev_potentials={"na":60,"k":-90,"ca":140})
