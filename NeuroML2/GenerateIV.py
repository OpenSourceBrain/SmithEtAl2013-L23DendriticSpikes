import sys
import opencortex.core as oc
import numpy as np

def generate(cell_id, duration, reference, iRange):

    cell_file = '%s.cell.nml'%cell_id

    #cell_id = 'Cell0'
    #cell_file = 'L23_morph.cell.nml'

    nml_doc, network = oc.generate_network(reference, temperature='35degC')

    oc.include_neuroml2_cell_and_channels(nml_doc,cell_file,cell_id)



    population_size = len(iRange)

    pop = oc.add_population_in_rectangular_region(network,
                                                  'L23_pop',
                                                  cell_id,
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
                                duration, 
                                dt = 0.025)

    
if __name__ == "__main__":
    
    cell_id = 'L23_NoHotSpot'
    reference = "L23_IV"
    duration = 400
    iRange = np.arange(-0.1,0.8,0.1)
    
    if '-one' in sys.argv:
        iRange = np.array([0.5])
        reference = "L23_One"
        duration = 400
        
    generate(cell_id, duration, reference, iRange)
