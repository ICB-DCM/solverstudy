# load every working model from the model collection into workspace

import sys
import os
import importlib

from C import DIR_MODELS_AMICI


def load_specific_model(model_name, explicit_model):

    # path to one specific model
    model_output_dir = os.path.join(
        DIR_MODELS_AMICI, model_name, explicit_model)

    # load specific model
    sys.path.insert(0, os.path.abspath(model_output_dir))
    model_module = importlib.import_module(explicit_model)
    model = model_module.getModel()

    return model
