
import opencortex.build as oc
import numpy as np

nml_doc, network = oc.generate_network("L23_IV")

oc.include_neuroml2_cell_and_channels(nml_doc,'L23_NoHotSpot.cell.nml','L23_NoHotSpot')


iRange = np.arange(-0.1,0.8,0.1)

population_size = len(iRange)

pop = oc.add_population_in_rectangular_region(network,
                                              'L23_pop',
                                              'L23_NoHotSpot',
                                              population_size,
                                              0,0,0,
                                              1000,100,1000)
for i in range(iRange.size):
    stim_id = ("Stim_%i"%i)
    pg = oc.add_pulse_generator(nml_doc,
                           id=stim_id,
                           delay="50ms",
                           duration="250ms",
                           amplitude="%fnA"%iRange[i])

    oc.add_inputs_to_population(network,
                                stim_id,
                                pop,
                                pg.id,
                                all_cells=False,
                                only_cells=[i])

nml_file_name = '%s.net.nml'%network.id
oc.save_network(nml_doc, nml_file_name, validate=True)


oc.generate_lems_simulation(nml_doc, 
                            network, 
                            nml_file_name, 
                            duration =      350, 
                            dt =            0.1)