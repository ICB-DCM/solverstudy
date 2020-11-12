# load every working model from the model collection into workspace

import sys
import os
import importlib
import pandas as pd
import numpy as np

import libsbml
from C import DIR_MODELS_REGROUPED, DIR_MODELS_AMICI, DIR_MODELS


def get_submodel(submodel_path: str,
                 model_info: pd.DataFrame):
    """
    This function load an amici model module, if the (relative) path to the
    folder with this AMICI model module is provided.
    It extracts the respective sbml file from the list and returns it alongside
    with the model, if any postprecessing of the AMICI results is necessary
    """

    # load the amici model
    # add model path
    amici_model_path = os.path.join(DIR_MODELS, submodel_path)
    if os.path.abspath(amici_model_path) not in sys.path:
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


def get_submodel_list(model_name: str,
                      model_info: pd.DataFrame):
    """
    This function loads a list of amici model modules, which all belong to the
    same benchmark model, if a string with the id of the benchmark model id is
    provided.
    It also extracts the respective sbml files from the list and returns them
    with the models, if any postprecessing of the AMICI results is necessary
    """

    # get information about the model from the tsv table
    model_rows = model_info.loc[model_info['short_id'] == model_name]
    # only take accepted models
    model_rows = model_rows[model_rows['accepted']]
    submodel_paths = [path for path in model_rows['amici_path_final']]

    # collect the submodels
    sbml_model_list = []
    amici_model_list = []
    for submodel_path in submodel_paths:
        amici_model, sbml_model = get_submodel(submodel_path, model_info)
        sbml_model_list.append(sbml_model)
        amici_model_list.append(amici_model)

    return amici_model_list, sbml_model_list


def get_submodel_copasi(submodel_path: str,
                        model_info: pd.DataFrame):
    """
    This function loads a copasi file, if the (relative) path to the folder
    with this Copasi model is provided.
    It extracts the respective sbml file from the list and returns it alongside
    with the model, if any postprecessing of the Copasi results is necessary
    """

    # load the amici model
    copasi_file = os.path.join(DIR_MODELS, submodel_path)

    # if the amici import did not work, we don't want to consider this model
    if 'amici_path_final' in model_info.keys():
        model_row = model_info.loc[model_info['copasi_path'] == submodel_path]
        id = int(model_row.index.values)
        if model_row.loc[id, 'amici_path_final'] == '':
            return None

    return copasi_file


def get_submodel_list_copasi(model_name: str,
                             model_info: pd.DataFrame):
    """
    This function loads a list of Copasi model files, which all belong to the
    same benchmark model, if a string with the id of the benchmark model id is
    provided.
    It also extracts the respective sbml files from the list and returns them
    with the models, if any postprecessing of the Copasi results is necessary
    """

    # get information about the model from the tsv table
    model_rows = model_info.loc[model_info['short_id'] == model_name]
    # only take accepted models
    model_rows = model_rows[model_rows['accepted']]
    submodel_paths = [path for path in model_rows['copasi']]

    # collect the submodels
    copasi_file_list = []
    for submodel_path in submodel_paths:
        copasi_file = get_submodel_copasi(submodel_path, model_info)
        copasi_file_list.append(copasi_file)

    return [cps_file for cps_file in copasi_file_list if cps_file is not None]
