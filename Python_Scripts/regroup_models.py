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

from C import (DIR_MODELS_SEDML, DIR_MODELS_FINAL)
from setTime_BioModels import setTimeBioModels


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
            sim_start, sim_end, num_time_points = setTimeBioModels(sedml_model)

def _check_submodels(sedml_file, sbml_files):
    """Checks which sbml models of one sedml group belong together"""
    return


regroup_models()
