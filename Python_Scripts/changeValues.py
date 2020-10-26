# script for changing sbml information through sedml information

import libsedml
import libsbml
import os
import numpy as np


def changeValues(model, model_name, explicit_model, skip_indicator):

    # important paths
    if skip_indicator == 0:
        sedml_path = '../Models/all_models/' + model_name + '/' + model_name + '.sedml'
        sbml_path = '../Models/all_models/' + model_name + '/sbml_models/' + explicit_model + '.sbml'
    elif skip_indicator == 1:
        sedml_path = '../../Benchmarking_of_numerical_ODE_integration_methods/sedml_models/' + model_name + '/' + model_name + '.sedml'
        sbml_path = '../../Benchmarking_of_numerical_ODE_integration_methods/sedml_models/' + model_name + '/sbml_models/' + explicit_model + '.sbml'

    # do a case study if the sedml file exists or not (it doesn't exist for models of the BioModelsDatabase)
    if os.path.exists(sedml_path):

        # load SBML && SEDML models
        sbml_file = libsbml.readSBML(sbml_path)
        sedml_file = libsedml.readSedML(sedml_path)

        # old species settings of SBML model that have to be replaced
        all_properties = sbml_file.getModel()
        spcs = all_properties.getListOfSpecies()
        spcs_id = []
        spcs_num = []
        for iCount in range(0, len(spcs)):
            spcs_id.append(spcs[iCount].id)
            spcs_num.append(spcs[iCount].initial_concentration)

        # old parameter settings of SBML model that have to be replaced
        par_id = model.getParameterIds()
        par_id = list(par_id)
        for iCount in range(0, len(par_id)):
            try:
                a, b = par_id[iCount].split('_', 1)
                if a == 'amici':
                    par_id[iCount] = b
            except:
                'No split necessary!'
        par_num = model.getParameters()
        par_num = list(par_num)

        # old compartment settings of SBML model that have to be replaced
        all_properties = sbml_file.getModel()
        comp = all_properties.getListOfCompartments()
        comp_id = []
        comp_num = []
        for iCount in range(0, len(comp)):
            comp_id.append(comp[iCount].id)
            comp_num.append(comp[iCount].size)

        # new settings of SEDML parameters
        for iModels in range(0, sedml_file.getNumModels()):
            all_models = sedml_file.getModel(iModels)
            for iAttribute in range (0, all_models.getNumChanges()):
                all_changes = all_models.getChange(iAttribute)
                new_targ = all_changes.getTarget()
                new_val = all_changes.getNewValue()

                # decide for species or parameter
                div = new_targ.split('[')
                div = div[0]
                div = div.split(':')
                div = div[4]

                if div == 'species':
                    # parse right id out of new_targ string
                    id = new_targ.split('\'', )
                    id = id[1]

                    # counter
                    counter = 0

                    try:
                        # swap species settings
                        while id != spcs_id[counter]:
                            counter = counter + 1
                        spcs_num[counter] = new_val
                    except:
                        # species id from SEDML not in SBML
                        'Species-ID can be omitted'

                elif div == 'parameter':
                    # parse right id out of new_targ string
                    id = new_targ.split('\'',)
                    id = id[1]

                    # counter
                    counter = 0

                    try:
                        # swap parameter settings
                        while id != par_id[counter]:
                            counter = counter + 1
                        par_num[counter] = new_val
                    except:
                        # parameter id from SEDML not in SBML
                        'Parameter-ID can be omitted'

                elif div == 'compartment':
                    # parse right id out of new_targ string
                    id = new_targ.split('\'', )
                    id = id[1]

                    # counter
                    counter = 0

                    try:  # SBML model sometimes doesn't have the SEDML ID
                        # swap compartment settings
                        while id != comp_id[counter]:
                            counter = counter + 1
                        comp_num[counter] = new_val
                    except:
                        # species id from SEDML not in SBML
                        'Compartment-ID can be omitted'

        # transform par_num into an array
        par_num = np.asarray(par_num)
        p_num = []
        for iCount in range(0, len(par_num)):
            p_num.append(float(par_num[iCount]))

        # transform spcs_id into an array
        spcs_num = np.asarray(spcs_num)
        s_num = []
        for iCount in range(0, len(spcs_num)):
            s_num.append(float(spcs_num[iCount]))

        # replace old vector by new one
        model.setParameters(p_num)
        model.setInitialStates(s_num)

    else:
        'Model is part of the BioModelsDatabase!'

    return model