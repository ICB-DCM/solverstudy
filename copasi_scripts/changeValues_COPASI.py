# script for changing sbml vectors through sedml vectors
from loadModels import *
import libsedml
import libsbml
import os
import numpy as np
from shutil import copy2
from loadModels import *


def changeValues_for_Copasi(model, model_name, explicit_model):

    # important paths
    biomodels_path = './sedml_models/' + model_name + '/sbml_models/' + explicit_model + '.xml'
    sedml_path = './sedml_models/' + model_name + '/' + model_name + '.sedml'
    sbml_path = './sedml_models/' + model_name + '/sbml_models/' + explicit_model + '.sbml'
    save_path = '../copasi_sim'

    # create folder
    if not os.path.exists(save_path + '/' + model_name + '/' + explicit_model):
        os.makedirs(save_path + '/' + model_name + '/' + explicit_model)


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
        par_id = list(par_id)                                                                         # probelm: some IDs get changed to 'amici_'
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
        comp = all_properties.getListOfCompartments()
        comp_id = []
        comp_num = []
        for iCount in range(0, len(comp)):
            comp_id.append(comp[iCount].id)
            comp_num.append(comp[iCount].size)

        # new settings of SEDML parameters
        for iModels in range(0, sedml_file.getNumModels()):
            all_models = sedml_file.getModel(iModels)
            for iAttribute in range(0, all_models.getNumChanges()):
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

                    try:                                                                    # SBML model sometimes doesn't have the SEDML ID
                        # swap species settings
                        while id != spcs_id[counter]:
                            counter = counter + 1
                        all_properties.getSpecies(counter).initial_concentration = float(new_val)
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
                        all_properties.getParameter(counter).value = float(new_val)
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
                        all_properties.getCompartment(counter).size = float(new_val)
                    except:
                        # species id from SEDML not in SBML
                        'Compartment-ID can be omitted'

        # save changed sbml files and the accompaniying sedml file
        libsbml.writeSBMLToFile(sbml_file, save_path + '/' + model_name + '/' + explicit_model + '/' + model_name + '.sbml')
        libsedml.writeSedMLToFile(sedml_file, save_path + '/' + model_name + '/' + explicit_model + '/' + model_name + '.sedml')

    elif os.path.exists(biomodels_path):
        'Model is part of the BioModelsDatabase! - no changes possible since no sedml file exists!'
        copy2(biomodels_path, save_path + '/' + model_name + '/' + explicit_model)

    else:
        print('Something with the paths went wrong!')
        sys.exit()




######## call function

# paths
correct_amici_models = '../sbml2amici/correct_amici_models_paper'
correct_amici_models_16 = '../sbml2amici/correct_amici_models_paper_16'

counter = 0
correct_models = sorted(os.listdir(correct_amici_models))
correct_models_16 = sorted(os.listdir(correct_amici_models_16))
correct_trajectories = correct_models + correct_models_16
for iModel in correct_trajectories:
    if iModel in correct_models:
        sbmls = sorted(os.listdir(correct_amici_models + '/' + iModel))
    elif iModel in correct_models_16:
        sbmls = sorted(os.listdir(correct_amici_models_16 + '/' + iModel))
    for iFile in sbmls:
        #iModel = 'aguda1999_fig5c'
        #iFile = 'model0_aguda1'
        model = load_specific_model(iModel, iFile)
        changeValues_for_Copasi(model, iModel, iFile)
        counter += 1
    print('Model: ' + iModel + ' done!')
print('Final Number : ' + str(counter))
