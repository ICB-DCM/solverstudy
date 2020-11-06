# load every working model from the model collection into workspace

import sys
import os
import importlib
import pandas as pd
import numpy as np

import libsbml
from C import DIR_MODELS_REGROUPED, DIR_MODELS_AMICI, DIR_MODELS

# import the model_summary table to add information about the model
model_info = pd.read_csv(os.path.join(DIR_MODELS, 'model_summary.tsv'),
                         sep='\t')

def load_specific_model(model_name, explicit_model):

    # path to one specific model
    model_output_dir = os.path.join(
        DIR_MODELS_AMICI, model_name, explicit_model)

    # load specific model
    sys.path.insert(0, os.path.abspath(model_output_dir))
    model_module = importlib.import_module(explicit_model)
    model = model_module.getModel()

    return model

def get_submodel(submodel_path):
    # load the amici model
    # add model path
    amici_model_path = os.path.join(DIR_MODELS, submodel_path)
    sys.path.insert(0, os.path.abspath(amici_model_path))
    # import the module, get the model
    amici_model_name = amici_model_path.split('/')[-1]
    amici_model_module = importlib.import_module(amici_model_name)
    amici_model = amici_model_module.getModel()

    # get information about the model from the tsv table
    model_row = model_info.loc[model_info['amici_path'] == submodel_path]
    amici_model.setTimepoints(np.linspace(model_row.loc['start_time'].values,
                                          model_row.loc['end_time'].values,
                                          model_row.loc['n_timepoints'].values))

    # import the sbml model
    sbml_path = os.path.join(DIR_MODELS, model_row.loc['regrouped_path'].values)
    sbml_model = (libsbml.readSBML(sbml_path)).getModel()

    return amici_model, sbml_model

def get_submodel_list(model_name):
    sbml_files = [
        os.path.abspath(sbml_file) for sbml_file in
        sorted(os.listdir(os.path.join(DIR_MODELS_REGROUPED, model_name)))
    ]
    sbml_model_list = [libsbml.readSBML(sbml_file).getModel()
                       for sbml_file in sbml_files]

    amici_folders = [
        os.path.abspath(amici_folder) for amici_folder in
        sorted(os.listdir(os.path.join(DIR_MODELS_AMICI, model_name)))
    ]
    amici_model_list = [load_specific_model(amici_folder, amici_folder)
                        for amici_folder in amici_folders]

    return amici_model_list, sbml_model_list
