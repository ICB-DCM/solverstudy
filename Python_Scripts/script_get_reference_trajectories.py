"""Get reference trajectories regarded as "ground truth".

Either download or copy from /Cache, depending on environment variable
`USE_CACHED_REF_TRAJ`.
"""

import libsedml
import libsbml
import os
import shutil
import logging
import pandas as pd
import json
import tempfile
import requests
import urllib

from util import is_empty
from C import (
    DIR_BASE, DIR_MODELS, USE_CACHED_REF_TRAJ,
    DIR_TRAJ_REF, DIR_TRAJ_REF_JWS,
    DIR_TRAJ_REF_BIOMODELS,
    DIR_CACHE_TRAJ_REF_JWS, DIR_CACHE_TRAJ_REF_BIOMODELS)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(os.path.join(DIR_BASE, 'jws_trajectory_download.log'))
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
logger.addHandler(logging.StreamHandler())

# load the table with model information (global variable)
model_info: pd.DataFrame = \
    pd.read_csv(os.path.join(DIR_MODELS, 'model_summary.tsv'), sep='\t')


def get_reference_trajectories():
    """Either use cached, or compute reference trajectories."""
    # Create trajectory reference base folder
    os.makedirs(DIR_TRAJ_REF, exist_ok=True)

    # Copy cached trajectories if flag set
    if USE_CACHED_REF_TRAJ == 'YES':
        shutil.copytree(DIR_CACHE_TRAJ_REF_JWS, DIR_TRAJ_REF_JWS)
        shutil.copytree(
            DIR_CACHE_TRAJ_REF_BIOMODELS, DIR_TRAJ_REF_BIOMODELS)
        return

    # TODO We use cached biomodels simulations anyway, unless automatic
    #  simulation is implemented here too. Until then, manually copy if
    #  changes of the Biomodels simulations are intended.
    shutil.copytree(
        DIR_CACHE_TRAJ_REF_BIOMODELS,
        DIR_TRAJ_REF_BIOMODELS)

    # Target folder for JWS trajectories
    dir_traj_jws = os.path.join(
        DIR_TRAJ_REF, 'trajectories_reference_jws')
    # Create if not existent
    os.makedirs(dir_traj_jws)

    # Get jws model slug list
    url = "https://jjj.mib.ac.uk/rest/models/?format=json"
    jws_model_infos = json.loads(requests.get(url).text)

    # Loop over all models
    for i_submodel in model_info.index:
        if is_empty(model_info.loc[i_submodel, 'amici_path']):
            # Only get references for amici importable models
            continue

        # Path of the sedml file
        sedml_file = model_info.loc[i_submodel, 'sedml_path']
        if is_empty(sedml_file):
            # Not from jws
            continue

        download_jws_reference_trajectory(
            i_submodel, sedml_file, jws_model_infos)


def download_jws_reference_trajectory(
        i_model, sedml_file, jws_model_infos):
    # Read sedml document
    sedml_doc: libsedml.SedDocument = libsedml.readSedML(sedml_file)
    sedml_id = (sedml_file.split('/')[-1]).split('.')[0]

    sbml_file = model_info.loc[i_model, 'sbml_path']
    # The actual sbml id
    sbml_id = (sbml_file.split('/')[-1]).split('.')[0]

    logger.info(f"Downloading {sedml_id} {sbml_id}")

    # Target referencet trajectory file
    ref_folder = os.path.join(DIR_TRAJ_REF_JWS, sedml_id, sbml_id)
    ref_file = os.path.join(ref_folder, 'JWS_simulation.csv')
    if os.path.exists(ref_file):
        # Model has been downloaded already
        return

    # Simulation time points
    start_time = model_info.loc[i_model, 'start_time']
    end_time = model_info.loc[i_model, 'end_time']
    # TODO JWS does not seem to support the definition of n_timepoints
    #n_timepoints = model_info.loc[i_model, 'n_timepoints']

    # Get the used simulation task
    sedml_task: libsedml.SedTask = \
        sedml_doc.getTask(int(model_info.loc[i_model, 'sedml_task']))
    # Short consistency check that sbml model and sedml task fit together
    assert sbml_id == sedml_task.getModelReference()

    # Get sbml model definition in the sedml file, containing a change list
    sedml_sbml_model = sedml_doc.getModel(sedml_task.getModelReference())

    # Iterate over all changes defined in the sedml file simulation task
    #  for the sbml model.
    #  Like in the AMICI simulation, we overwrite species, parameters,
    #  and compartments.
    changes_list = []
    for change in sedml_sbml_model.getListOfChanges():
        # Change target and value
        target = change.getTarget()
        value = change.getNewValue()

        # Target type
        # TODO this could be improved, if expression matching problems occur
        target_type = (target.split('[')[0]).split(':')[4]
        if target_type not in {'species', 'parameter', 'compartment'}:
            logger.warning(
                f"Requesting a {target_type} change in {sbml_file}, "
                "which AMICI does not support. Keeping the change, but "
                "this is likely to cause non-comparable trajectories.")

        # Target id
        target_id = target.split("'")[1]
        changes_list.append(f'{target_id}={value};')

    # Get slug for JWS model simulation (heuristic, but seems to work)
    sbml_model = libsbml.readSBML(sbml_file).getModel()
    sbml_slug = None
    for jws_model_info in jws_model_infos:
        if sbml_model.getName() == jws_model_info['name']:
            sbml_slug = jws_model_info['slug']
            break
    if sbml_slug is None:
        raise ValueError(
            f"Extraction of SBML url for {sedml_id} {sbml_id} failed.")

    # Get Url with all changes
    # <species i>=<amount>
    # <parameter i>=<value>, compartment == parameter (in this case)
    url = f'https://jjj.bio.vu.nl/rest/models/{sbml_slug}' \
          f'/time_evolution?time_start={start_time};time_end={end_time};' \
          'species=all;' + ''.join(changes_list)
    logger.info(f"JWS simulation URL: {url}")

    # Create a temporary file for the json simulation
    _, tmp_json_file = tempfile.mkstemp()
    # JWS sometimes just returns an error output, then just retry
    while True:
        logger.info("Downloading")
        urllib.request.urlretrieve(url, tmp_json_file)
        with open(tmp_json_file, 'r') as f:
            if f.read() != '{"error_msg": "No result was returned."}':
                break

    # Convert to and save as csv file
    os.makedirs(ref_folder, exist_ok=True)
    pd.read_json(tmp_json_file).to_csv(ref_file, sep='\t', index=False)

    # Remove temporary json file
    os.remove(tmp_json_file)


def link_reference_trajectories_to_amici_models():
    """
    We need to find the correct reference trajectory for each model.
    This is not fully trivial, as some models come from biomodels,
    some from JWS.
    """
    # unset column
    model_info['ref_trajectory_path'] = None

    path_ref_biomodels = DIR_TRAJ_REF_BIOMODELS
    path_ref_jws = DIR_TRAJ_REF_JWS

    # iterate over models, write pyth to reference trajectory
    for sub_id in model_info.index:
        i_row = model_info.loc[sub_id]

        # we must discriminate between models from JWS and biomodels
        if is_empty(i_row['sedml_path']):
            # from biomodels, the ref trajectories were simulated with Copasi
            model_suffix = (i_row['sbml_path'].split('/')[-1]).split('.')[0]
            name = f'trajectories_copasi_strictest_{model_suffix.lower()}.tsv'
            ref = os.path.join(path_ref_biomodels, name)
        else:
            # from JWS online, reference trajectories were downloaded
            # refactor the name based on the sedml and the sbml file names
            name1 = (i_row['sedml_path'].split('/')[-1]).split('.')[0]
            name2 = (i_row['sbml_path'].split('/')[-1]).split('.')[0]
            ref = os.path.join(
                path_ref_jws, name1, name2, 'JWS_simulation.csv')

        # save path
        model_info.loc[sub_id, 'ref_trajectory_path'] = ref


# Get all reference trajectories
get_reference_trajectories()

# Update/set all reference trajectory paths
link_reference_trajectories_to_amici_models()

# Save the model info file again
model_info.to_csv(os.path.join(DIR_MODELS, 'model_summary.tsv'),
                  sep='\t', index=False)
