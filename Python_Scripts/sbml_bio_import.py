import os
import urllib.request
import shutil
import logging
from logging_util import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

BASE_URL = "https://www.ebi.ac.uk"
BASE_FOLDER = "../../Benchmarking_of_numerical_ODE_integration_methods/sedml_models"


def download_specific_sbml_biomodels_from_biomodelsDatabase(model_ids, model_names, base_folder=BASE_FOLDER):
    """
    Download all sbml models to xml files.
    """
    # download every single sbml model
    for iSBML in range(0, len(model_names)):
        # create an own folder for the model
        if not os.path.exists(base_folder + "/" + model_names[iSBML]):
            os.makedirs(base_folder + "/" + model_names[iSBML])
        if not os.path.exists(base_folder + "/" + model_names[iSBML] + "/sbml_models"):
            os.makedirs(base_folder + "/" + model_names[iSBML] + "/sbml_models")
        sbml_file = base_folder + "/" + model_names[iSBML] + "/sbml_models/" + model_names[iSBML] + ".xml"
        # url to download sbml
        sbml_url = BASE_URL + "/biomodels/model/download/" + model_ids[iSBML] + "?filename=" + model_ids[iSBML] + "_url.xml"
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
        logger.warn(f"Failed to download sbml model from {sbml_url}, {e}.")


def add_Froehlich2018():
    # import Froehlich model from Github repository
    if not os.path.exists(BASE_FOLDER + '/Froehlich2018/sbml_models'):
        os.makedirs(BASE_FOLDER + '/Froehlich2018/sbml_models')
    froehlich2018_url = 'https://raw.githubusercontent.com/ICB-DCM/CS_Signalling_ERBB_RAS_AKT/master/FroehlichKes2018/PEtab/CS_Signalling_ERBB_RAS_AKT_petab.xml'
    try:
        with urllib.request.urlopen(froehlich2018_url) as response, \
                open(BASE_FOLDER + '/Froehlich2018/sbml_models/Froehlich2018.xml', 'wb') as f:
            shutil.copyfileobj(response, f)
    except Exception as e:
        logger.warn(f"Failed to download sbml model from {froehlich2018_url}, {e}.")


def add_BioModels_Folder(model_names):
    # create a folder for all biomodels
    if not os.path.exists('../../Benchmarking_of_numerical_ODE_integration_methods/BioModelsDatabase_models'):
        os.makedirs('../../Benchmarking_of_numerical_ODE_integration_methods/BioModelsDatabase_models')
    all_models = sorted(os.listdir(BASE_FOLDER))
    for model in all_models:
        if model in model_names or model == 'Froehlich2018':
            shutil.copytree(BASE_FOLDER + '/' + model, '../../Benchmarking_of_numerical_ODE_integration_methods/BioModelsDatabase_models/' + model)
