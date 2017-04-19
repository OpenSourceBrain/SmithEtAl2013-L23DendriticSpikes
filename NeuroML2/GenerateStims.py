import sys

import opencortex.core as oc

import numpy as np

def generate(cell_id, duration, reference, bEnsyn):

    bInsyn = int(bEnsyn * 0.2)
    
    cell_file = '%s.cell.nml'%cell_id

    nml_doc, network = oc.generate_network(reference, temperature='35degC')

    oc.include_neuroml2_cell_and_channels(nml_doc,cell_file,cell_id)
    
    oc.include_neuroml2_file(nml_doc,'AMPA.synapse.nml')
    oc.include_neuroml2_file(nml_doc,'GABA.synapse.nml')
    oc.include_neuroml2_file(nml_doc,'NMDA.synapse.nml')

    ampa1 = oc.add_poisson_firing_synapse(nml_doc,
                                       id="ampa1",
                                       average_rate="50 Hz",
                                       synapse_id='AMPA')

    gaba1 = oc.add_poisson_firing_synapse(nml_doc,
                                       id="gaba1",
                                       average_rate="50 Hz",
                                       synapse_id='GABA')

    nmda1 = oc.add_poisson_firing_synapse(nml_doc,
                                       id="nmda1",
                                       average_rate="50 Hz",
                                       synapse_id='NMDA')


    pop = oc.add_single_cell_population(network,
                                        'L23_pop',
                                        cell_id)
                                                  
    
    
            
    oc.add_targeted_inputs_to_population(network, "bEsyn_a",
                                pop, ampa1.id, 
                                segment_group='dendrite_group',
                                number_per_cell = bEnsyn,
                                all_cells=True)
            
    oc.add_targeted_inputs_to_population(network, "bEsyn_n",
                                pop, nmda1.id, 
                                segment_group='dendrite_group',
                                number_per_cell = bEnsyn,
                                all_cells=True)
            
    oc.add_targeted_inputs_to_population(network, "bIsyn",
                                pop, gaba1.id, 
                                segment_group='dendrite_group',
                                number_per_cell = bInsyn,
                                all_cells=True)
                                

    nml_file_name = '%s.net.nml'%network.id
    oc.save_network(nml_doc, nml_file_name, validate=True)

    interesting_seg_ids = [0,200,1000,2000,2500,2949]

    to_plot = {'Some_voltages':[]}
    to_save = {'%s_voltages.dat'%cell_id:[]}

    for seg_id in interesting_seg_ids:
        to_plot.values()[0].append('%s/0/%s/%s/v'%(pop.id, pop.component,seg_id))
        to_save.values()[0].append('%s/0/%s/%s/v'%(pop.id, pop.component,seg_id))

    oc.generate_lems_simulation(nml_doc, 
                                network, 
                                nml_file_name, 
                                duration, 
                                dt = 0.025,
                               gen_plots_for_all_v = False,
                               plot_all_segments = False,
                               gen_plots_for_quantities = to_plot,   #  Dict with displays vs lists of quantity paths
                               gen_saves_for_all_v = False,
                               save_all_segments = False,
                               gen_saves_for_quantities = to_save)   #  Dict with file names vs lists of quantity paths)

    
if __name__ == "__main__":
    
    cell_id = 'L23_NoHotSpot'
    reference = "L23_Stim"
    duration = 200
        
    generate(cell_id, duration, reference, 100)
