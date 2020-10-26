import os
import urllib.request
import shutil
import logging

from logging_util import LOGGER_NAME
from C import DIR_MODELS_SEDML, DIR_MODELS_BIOMODELS

logger = logging.getLogger(LOGGER_NAME)

BASE_URL = "https://www.ebi.ac.uk"
BASE_FOLDER = DIR_MODELS_SEDML


def download_specified_models_from_biomodels(model_ids, model_names):
    """
    Download all sbml models to xml files.
    """
    # download every single sbml model
    for iSBML in range(0, len(model_names)):
        # create an own folder for the model
        sbml_folder = os.path.join(
            BASE_FOLDER, model_names[iSBML], 'sbml_models')
        if not os.path.exists(sbml_folder):
            os.makedirs(sbml_folder)
        sbml_file = os.path.join(sbml_folder, model_names[iSBML] + '.sbml')
        # url to download sbml
        sbml_url = BASE_URL + "/biomodels/model/download/" + \
            model_ids[iSBML] + "?filename=" + model_ids[iSBML] + "_url.xml"
        # download sbml model
        download_sbml_model(sbml_url, sbml_file)


def download_sbml_model(sbml_url, sbml_file):
    """
    Download one sbml model from `sbml_url` to `sbml_file`.
    """
    logger.info(f"  Downloading sbml model from {sbml_url} to file "
                f"{sbml_file}.")
    try:
        with urllib.request.urlopen(sbml_url) as response, \
                open(sbml_file, 'wb') as f:
            shutil.copyfileobj(response, f)
    except Exception as e:
        logger.warning(f"Failed to download sbml model from {sbml_url}, {e}.")


def add_Froehlich2018():
    """Import Froehlich model from Github repository"""
    sbml_folder = os.path.join(BASE_FOLDER, 'Froehlich2018', 'sbml_models')
    if not os.path.exists(sbml_folder):
        os.makedirs(sbml_folder)
    sbml_file = os.path.join(sbml_folder, 'Froehlich2018.sbml')
    froehlich2018_url = 'https://raw.githubusercontent.com/ICB-DCM/' \
        'CS_Signalling_ERBB_RAS_AKT/master/FroehlichKes2018/' \
        'PEtab/CS_Signalling_ERBB_RAS_AKT_petab.xml'
    try:
        with urllib.request.urlopen(froehlich2018_url) as response, \
                open(sbml_file, 'wb') as f:
            shutil.copyfileobj(response, f)
    except Exception as e:
        logger.warning(
            f"Failed to download sbml model from {froehlich2018_url}, {e}.")


def add_BioModels_Folder(model_names):
    """Create a folder for all biomodels"""
    if not os.path.exists(DIR_MODELS_BIOMODELS):
        os.makedirs(DIR_MODELS_BIOMODELS)
    all_models = sorted(os.listdir(BASE_FOLDER))
    for model in all_models:
        if model in model_names or model == 'Froehlich2018':
            shutil.copytree(os.path.join(BASE_FOLDER, model),
                            os.path.join(DIR_MODELS_BIOMODELS, model))
