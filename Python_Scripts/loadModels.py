# load every working model from the model collection into workspace

import sys
import os
import importlib

import libsbml
from C import DIR_MODELS_FINAL, DIR_MODELS_AMICI


def load_specific_model(model_name, explicit_model):

    # path to one specific model
    model_output_dir = os.path.join(
        DIR_MODELS_AMICI, model_name, explicit_model)

    # load specific model
    sys.path.insert(0, os.path.abspath(model_output_dir))
    model_module = importlib.import_module(explicit_model)
    model = model_module.getModel()

    return model


def get_model_list(model_name):
    sbml_files = [
        os.path.abspath(sbml_file) for sbml_file in
        sorted(os.listdir(os.path.join(DIR_MODELS_FINAL, model_name)))
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