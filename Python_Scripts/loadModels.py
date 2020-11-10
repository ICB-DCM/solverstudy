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
    if 'amici_path_final' in model_info.keys():
        model_row = model_info.loc[model_info['amici_path_final'] == submodel_path]
    else:
        model_row = model_info.loc[model_info['amici_path'] == submodel_path]
    id = int(model_row.index.values)
    # get the timepoints according to the model info dataframe
    amici_model.setTimepoints(np.linspace(
        float(model_row.loc[id, 'start_time']),
        float(model_row.loc[id, 'end_time']),
        int(model_row.loc[id, 'n_timepoints'])
    ))

    # import the sbml model
    sbml_path = os.path.join(DIR_MODELS, model_row.loc[id, 'regrouped_path'])
    sbml_model = (libsbml.readSBML(sbml_path)).getModel()

    return amici_model, sbml_model

def get_submodel_list(model_name):
    # get information about the model from the tsv table
    model_rows = model_info.loc[model_info['short_id'] == model_name]
    submodel_paths = [final_path
                      for final_path in model_rows['amici_path_final']
                      if str(final_path) not in ('', 'nan')]

    # collect the submodels
    sbml_model_list = []
    amici_model_list = []
    for submodel_path in submodel_paths:
        amici_model, sbml_model = get_submodel(submodel_path)
        sbml_model_list.append(sbml_model)
        amici_model_list.append(amici_model)

    return amici_model_list, sbml_model_list
