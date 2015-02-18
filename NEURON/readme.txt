The code builds a model of a layer 2/3 pyramidal cell and distributes inhibitory and excitatory synapses randomly across the dendritic tree. There is a set of background synapses activated continuously, and a set of signal synapses activated at st_onset for st_duration. All synapses are activated with independent Poisson trains of spikes at the desired mean rates. Note that because there is no short-term plasticity, the same total rate of synaptic activation can be achieved with different combinations of synapse number and rate, with smaller numbers of synapses increasing the simulation speed. Within certain boundaries, mainly determined by the degree of spatial coverage of the dendritic tree, this does not affect the simulation results.

The code is written in Python except for the cell morphology, and requires standard libraries such as numpy and matplotlib, plus Brian (http://briansimulator.org/) for generating Poisson trains. The main file saves a pickle temp.pkl file with all the simulation data, including the simulation parameters, and an example of how to read it and plot the data is given in analysis.py. Running the current code in main.py followed by analysis.py reproduces Extended Data Figure 10e of Smith et al. 2013. The reproduction is not perfect because of differences in the background synaptic input. Currently the simulation reads synapse location and respective timings of activation from files for reproducing the figure. There are comments in the code showing where this can be changed back to random input.
 

The zip archive contains the following files:

# simulation code
libcell.py - library with classes and functions for creating and intrumenting neurons
main.py - setups and runs the simulation, plus several auxiliary functions
analysis.py - loads simulation data and plots traces
saveClass.py - dummy class for saving data
L23.hoc - cell morphology

# synapse locations and timings 
Elocs.npy - locations of excitatory synapses
Ilocs.npy - locations of inhibitory synapses
etimes.npy - activation timings for excitatory synapses
itimes.npy - activation timings for inhibitory synapses

# mechanism files
mod.files - directory containing .mod files with mechanisms for ion channels and synapses. Compile using nrnivmodl and update compilation directory in load_mechanisms at the top of libcell.py




