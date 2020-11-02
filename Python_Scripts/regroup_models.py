"""
Imports the SED-ML models and the SBML models from Biomodels and regroups them
according to model properties (state variables, reactions, model name)
in a newly created folder structure.
One folder then corresponds to one benchmark model, with possibly multiple SBML
files belonging to one benchmark model.
"""

# Note: libsedml must be imported before libsbml for whatever reason

import libsedml
import libsbml
import os
import shutil

from C import (DIR_MODELS_SEDML, DIR_MODELS_FINAL)
from setTime_BioModels import timePointsBioModels


# get all models
def regroup_models():
    list_directory_sedml = sorted(os.listdir(DIR_MODELS_SEDML))
    for sedml_model in list_directory_sedml:
        # important paths
        sedml_folder = os.path.join(DIR_MODELS_SEDML, sedml_model)
        sedml_file = os.path.join(sedml_folder, f'{sedml_model}.sedml')

        sbml_folder = os.path.join(sedml_folder, 'sbml_models')
        sbml_files = [os.path.join(sbml_folder, sbml_model)
                      for sbml_model in sorted(os.listdir(sbml_folder))]

        if os.path.exists(sedml_file):
            benchmark_models = _check_submodels(sedml_file, sbml_files)
        else:
            # only one sbml file, a benchmark model on its own. Copy.
            benchmark_model = os.path.join(DIR_MODELS_FINAL, sedml_model)
            if not os.path.exists(benchmark_model):
                os.mkdir(benchmark_model)
            try:
                shutil.copy(sbml_files[0],
                            os.path.join(benchmark_model,
                                         os.listdir(sbml_folder)[0]))
            except IndexError:
                print('Empty model folder for model ' + sedml_model)

            # get the simulation times and write them to csv file
            sim_start, sim_end, num_timep, _ = timePointsBioModels(sedml_model)

def _check_submodels(sedml_file, sbml_files):
    """Checks which sbml models of one sedml group belong together"""
    sedml_info = libsedml.readSedML(sedml_file)
    for sbml_file in sbml_files:
        sbml_info = libsbml.readSBML(sbml_file)
        sbml_model = sbml_info.getModel()
        species = sbml_model.getListOfSpecies()
        reactions = sbml_model.getListOfReactions()

    return


regroup_models()
