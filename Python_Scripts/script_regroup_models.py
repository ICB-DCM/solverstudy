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
import pandas as pd
import re

from C import (DIR_MODELS_SEDML, DIR_MODELS_REGROUPED, DIR_MODELS, DIR_BASE)
from setTime_BioModels import timePointsBioModels


# get all models
def regroup_models():
    # get all models, list information about them
    list_directory_sedml = sorted(os.listdir(DIR_MODELS_SEDML))
    model_info = []

    for sedml_model in list_directory_sedml:
        # get the model name and year based on the SED-ML and SBML name
        model_name, model_year = _parse_model_name(sedml_model)
        if model_name is None or model_year is None:
            continue

        # get the paths
        sedml_folder = os.path.join(DIR_MODELS_SEDML, sedml_model)
        sedml_file = os.path.join(sedml_folder, f'{sedml_model}.sedml')

        sbml_folder = os.path.join(sedml_folder, 'sbml_models')
        sbml_files = [os.path.join(sbml_folder, sbml_model)
                      for sbml_model in sorted(os.listdir(sbml_folder))]

        if os.path.exists(sedml_file):
            model_info = _check_sedml_submodels(sedml_file, sbml_files,
                                                model_name, model_year,
                                                model_info)
        else:
            # only one SBML file, no SED-ML info. A benchmark model on its own.
            sbml_path = os.path.abspath(sbml_files[0])
            model_info = _check_biomodels_model(sedml_model, sbml_path,
                                                model_name, model_year,
                                                model_info)

    # Group sbml models and give them short Identifiers (e.g., Bachmann2011a)
    model_info_df = _group_models_by_id(model_info)

    return model_info_df


def _group_models_by_id(model_info):
    # We've run through all models. Now, let's generate short identifiers for
    # the groups of models, which should belong together
    known_ids = {}
    for model in model_info:
        if model['long_id'] not in known_ids:
            new_id = _generate_new_id(known_ids, model['long_id'])
            known_ids[model['long_id']] = new_id
        model['short_id'] = known_ids[model['long_id']]
    # finally we want to post-process the model_list
    return pd.DataFrame(model_info)


def _generate_new_id(known_ids, long_id):
    # count, which letter to append in case (yes, I know that's simplistic)
    letter_count = 0
    letter_list = ['', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
    # iterate over the unique known_ids and increment counter
    for known_id in known_ids:
        if (known_id[0], known_id[1]) == (long_id[0], long_id[1]):
            letter_count += 1
    # append a letter, if necessary
    append_letter = letter_list[letter_count]
    # return the new short identifier
    return str(long_id[0]) + str(long_id[1]) + append_letter


def _parse_model_name(sedml_model):
    """We want to extract the model name and year based on the SBML file"""
    # parse the sedml name via regex
    model_name_full = sedml_model.split('_')[0]
    p_name = re.compile('[A-Za-z]*')
    p_year = re.compile('\d\d\d\d')
    m_name = p_name.match(model_name_full)
    m_year = p_year.search(model_name_full)

    if m_name is None:
        print('Model name could not be read. Model ' + sedml_model)
        return None, None
    else:
        model_name = m_name[0].lower()

    if m_year is None:
        print('Model year could not be read. Model ' + sedml_model)
        return None, None
    else:
        model_year = m_year[0]

    return model_name, model_year


def _check_biomodels_model(sedml_model, sbml_path, model_name, model_year, model_info):
    # only one sbml file, a benchmark model on its own.
    sedml_path = ''
    sbml_model = (libsbml.readSBML(sbml_path)).getModel()
    n_species = len(sbml_model.getListOfSpecies())
    n_reactions = len(sbml_model.getListOfReactions())

    # get the simulation times and write them to csv file
    out_start, out_end, n_timepoints, _ = \
        timePointsBioModels(sedml_model)
    if out_start is None:
        # Tf the model is not found, timePointsBioModels issues a warning.
        # We want to treat this case as a failure
        return model_info

    model_info.append({
        'name': model_name,
        'year': model_year,
        'n_species': n_species,
        'n_reactions': n_reactions,
        'long_id': (model_name, model_year, n_species, n_reactions),
        'short_id': '',
        'sbml_path': sbml_path,
        'sedml_path': sedml_path,
        'regrouped_path': '',
        'start_time': out_start,
        'end_time': out_end,
        'n_timepoints': n_timepoints,
        'sedml_task': '',
    })

    return model_info


def _check_sedml_submodels(sedml_file, sbml_files,
                           model_name, model_year, model_info):
    """Checks which sbml models of one sedml group belong together"""
    sedml_path = os.path.abspath(sedml_file)
    sedml_doc = libsedml.readSedML(sedml_file)
    sedml_task_models = [task.getModelReference() for task in sedml_doc.getListOfTasks()]

    for sbml_file in sbml_files:
        # we want to find a simulation task for this SBML model
        # first, get the name of the file (identifier in SED-ML)
        sbml_path = os.path.abspath(sbml_file)
        sbml_file_short = (sbml_file.split('/')[-1]).split('.')[0]

        # Find the first task for this model (and warn if no task was found)
        try:
            task_number = sedml_task_models.index(sbml_file_short)
        except ValueError:
            print('SBML file not found in list of tasks: ' + sbml_file_short)
            return model_info

        # get the corresponding simulation setting
        current_sim = sedml_doc.getSimulation(sedml_doc.getTask(
            task_number).getSimulationReference())
        # remember simulation settings
        out_start = current_sim.getOutputStartTime()
        out_end = current_sim.getOutputEndTime()
        n_timepoints = current_sim.getNumberOfPoints()

        # get info about the SBML file
        sbml_model = libsbml.readSBML(sbml_file).getModel()
        if sbml_model is None:
            # check for SBML model
            print(f'No sbml model found for file {sbml_file}, '
                  f'in model name f{model_name}, '
                  f'model year {model_year}')
            return model_info
        n_species = len(sbml_model.getListOfSpecies())
        n_reactions = len(sbml_model.getListOfReactions())

        # add model information to the list
        model_info.append({
            'name': model_name,
            'year': model_year,
            'n_species': n_species,
            'n_reactions': n_reactions,
            'sbml_path': sbml_path,
            'sedml_path': sedml_path,
            'regrouped_path': '',
            'start_time': out_start,
            'end_time': out_end,
            'n_timepoints': 101, # for whatever reason, our ref trajectories only use 101 points...
            'long_id': (model_name, model_year, n_species, n_reactions),
            'short_id': '',
            'sedml_task': task_number,
        })

    return model_info


def adapt_and_save_models(model_info_df):
    # create the folders
    if not os.path.exists(DIR_MODELS_REGROUPED):
        os.mkdir(DIR_MODELS_REGROUPED)

    model_folders = list(set(model_info_df['short_id']))
    for model_folder in model_folders:
        if not os.path.exists(os.path.join(DIR_MODELS_REGROUPED, model_folder)):
            os.mkdir(os.path.join(DIR_MODELS_REGROUPED, model_folder))
    logfile = open('sedml_change.log', 'w')
    logfile.close()
    n_models = model_info_df.shape[0]
    for i_model in range(n_models):
        final_file_name = _adapt_and_save_model(
            model_details=dict(model_info_df.loc[i_model, :]))
        model_info_df.loc[i_model, 'regrouped_path'] = os.path.relpath(
            final_file_name, DIR_MODELS)

    return model_info_df


def _adapt_and_save_model(model_details):
    """This routine takes model information from the dataframe created during
    model regrouping, adapts the SBML file, and saves it in the model folder"""

    # get and create info about the paths
    sbml_file_name = model_details['sbml_path'].split('/')[-1]
    final_folder = os.path.join(DIR_MODELS_REGROUPED, model_details['short_id'])
    final_file_name = os.path.join(final_folder, sbml_file_name)

    # ifwe have no SED-ML file, the model is a biomodels model consisting of
    # only one SBML sheet. Move this file to the new location
    if model_details['sedml_path'] == '':
        shutil.copy(model_details['sbml_path'], final_file_name)
        return final_file_name

    # if the model is from the JWS model collection, we must apply the changes
    # from the SED-ML file
    sedml_file = libsedml.readSedML(model_details['sedml_path'])
    sedml_task = sedml_file.getTask(model_details['sedml_task'])
    sbml_file = libsbml.readSBML(model_details['sbml_path'])
    sbml_model = sbml_file.getModel()

    # short consistency check that SBML model and SED-ML task fit together
    assert sbml_file_name.split('.')[0] == sedml_task.getModelReference()
    sedml_submodel = sedml_file.getModel(sedml_task.getModelReference())

    logfile = open('sedml_change.log', 'a')
    for change in sedml_submodel.getListOfChanges():
        # We iterate over all changes for this model in the SED-ML
        target = change.getTarget()
        value = change.getNewValue()

        # decide for species or parameter
        div = (target.split('[')[0]).split(':')[4]
        target_id = target.split("'", )[1]

        if div == 'species':
            try:
                sbml_model.getSpecies(target_id).initial_concentration = \
                    float(value)
            except AttributeError:
                if sbml_model.getSpecies(target_id) is None:
                    logfile.write(f'Trying to change initial concentration of species '
                          f'{target_id} via SED-ML file, but this species does '
                          f'not exist in the current SBML model '
                          f'({sbml_file_name}). Omitting!\n')
        elif div == 'parameter':
            try:
                sbml_model.getParameter(target_id).value = float(value)
            except AttributeError:
                if sbml_model.getParameter(target_id) is None:
                    logfile.write(f'Trying to change sbml_model parameter {target_id}, '
                          f'via SED-ML file, but this parameter does not exist '
                          f'in the current SBML model ({sbml_file_name}).'
                          f'Omitting!\n')
        elif div == 'compartment':
            sbml_model.getCompartment(target_id).size = float(value)
        else:
            logfile.write(f'Trying to change a {div} in sbml_model '
                  f'{sbml_file_name}, which is currently not supported.'
                  f'Omitting!\n')

    # save changed sbml files and the accompaniying sedml file
    libsbml.writeSBMLToFile(sbml_model.getSBMLDocument(), final_file_name)
    logfile.close()
    return final_file_name


def link_reference_trajectories_to_amici_models(model_info_df):
    # we need to find the correct reference trajectory for each model
    ref_trajectory_paths = {}
    path_ref_biomodels = os.path.abspath(os.path.join(
        DIR_BASE, '..', 'Cache', 'trajectories_reference_biomodels'))
    path_ref_jws = os.path.abspath(os.path.join(
        DIR_BASE, '..', 'Cache', 'trajectories_reference_jws'))

    # iterate over models, write pyth to reference trajectory
    for sub_id in model_info_df.index:
        i_row = model_info_df.loc[sub_id]

        # we must discriminate between models from JWS and biomodels
        if i_row['sedml_path'] == '':
            # from biomodels, the ref trajectories were simulated with Copasi
            name = 'original_copasi_' + i_row['name'] + str(i_row['year'])
            if os.path.exists(os.path.join(path_ref_biomodels,
                                           name + '_14_14.tsv')):
                # did it work with tolerances 1e-14, 1e-14?
                ref = name + '_14_14.tsv'
            else:
                # If not, tolerances 1e-12, 1e-12 were used
                ref = name + '_12_12.tsv'
            # add the path
            ref = os.path.join(path_ref_biomodels, ref)

        else:
            # from JWS online, reference trajectories were downloaded
            # refactor the name based on the sedml and the sbml file names
            name1 = (i_row['sedml_path'].split('/')[-1]).split('.')[0]
            name2 = (i_row['sbml_path'].split('/')[-1]).split('.')[0]
            ref = os.path.join(path_ref_jws, name1, name2, 'JWS_simulation.csv')

        ref_trajectory_paths[sub_id] = ref

    # We've collected the paths of all reference trajectories.
    # Now we append them to the dataframe
    return model_info_df.join(pd.Series(ref_trajectory_paths,
                                        name='ref_trajectory_path'))


model_info_df = regroup_models()

model_info_df = adapt_and_save_models(model_info_df)

model_info_df = link_reference_trajectories_to_amici_models(model_info_df)

model_info_df.to_csv(os.path.join(DIR_MODELS, 'model_summary.tsv'),
                     sep='\t', index=False)
