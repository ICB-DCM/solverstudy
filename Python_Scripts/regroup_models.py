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

from C import (DIR_MODELS_SEDML, DIR_MODELS_FINAL)
from setTime_BioModels import timePointsBioModels


# get all models
def regroup_models():
    # get all models, list information about them
    list_directory_sedml = sorted(os.listdir(DIR_MODELS_SEDML))
    model_info = []

    for sedml_model in list_directory_sedml:
        # get the model name and year
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
    model_info_df.to_csv('benchmark_models_overview.tsv', sep='\t', index=False)

    return model_info_df


def _group_models_by_id(model_info):
    # We've run through all models. Now, let's generate short identifier for
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

    # benchmark_model = os.path.join(DIR_MODELS_FINAL, sedml_model)
    # if not os.path.exists(benchmark_model):
    #    os.mkdir(benchmark_model)
    # try:
    #    shutil.copy(sbml_files[0],
    #                os.path.join(benchmark_model,
    #                             os.listdir(sbml_folder)[0]))
    # except IndexError:
    #    print('Empty model folder for model ' + sedml_model)

    # get the simulation times and write them to csv file
    out_start, out_end, n_timepoints, _ = \
        timePointsBioModels(sedml_model)
    if out_start is None:
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
            print('No sbml model found for file' + sbml_file +
                  ', in model name ' + model_name +
                  ', model year ' + model_year)
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
            'start_time': out_start,
            'end_time': out_end,
            'n_timepoints': n_timepoints,
            'long_id': (model_name, model_year, n_species, n_reactions),
            'short_id': '',
            'sedml_task': task_number,
        })

    return model_info


regroup_models()
