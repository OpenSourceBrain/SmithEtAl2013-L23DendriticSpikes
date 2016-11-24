
import opencortex.build as oc

nml_doc, network = oc.generate_network("L23_IV")

oc.include_neuroml2_cell_and_channels(nml_doc,'L23_NoHotSpot.cell.nml','L23_NoHotSpot')

population_size = 2

pop = oc.add_population_in_rectangular_region(network,
                                              'L23_pop',
                                              'L23_NoHotSpot',
                                              population_size,
                                              0,0,0,
                                              1000,100,1000)
                                   
                                              
pgIzh = oc.add_pulse_generator(nml_doc,
                       id="Stim0",
                       delay="100ms",
                       duration="300ms",
                       amplitude="0.5nA")
                       
oc.add_inputs_to_population(network,
                            "Stim0",
                            popIzh,
                            pgIzh.id,
                            all_cells=False)

nml_file_name = '%s.net.nml'%network.id
oc.save_network(nml_doc, nml_file_name, validate=True)


oc.generate_lems_simulation(nml_doc, 
                            network, 
                            nml_file_name, 
                            duration =      500, 
                            dt =            0.005)