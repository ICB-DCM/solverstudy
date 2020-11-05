# AMICI import of a JWS sbml model from the model collection

import libsbml
import amici
import os
import logging
import pandas as pd

from C import (
    DIR_BASE, DIR_MODELS_REGROUPED, DIR_MODELS, DIR_MODELS_AMICI)

# create .tsv file
tsv_table = pd.DataFrame(
    columns=['id', 'states', 'reactions', 'error_message'])

# important paths
models_path = DIR_MODELS_AMICI
models_base_path = DIR_MODELS
base_path = DIR_MODELS_REGROUPED

# create directory for all future amici models
if not os.path.exists(models_path):
    os.makedirs(models_path)

# create logger object
logger = logging.getLogger()

# initialize the log settings
logging.basicConfig(filename=os.path.join(DIR_BASE, 'sbml2amici.log'),
                    level=logging.DEBUG)

# list of all directories + SBML files
list_directory = sorted(os.listdir(base_path))

# set row-counter for .tsv file and list all model
counter = 0
for i_model in list_directory:
    list_files = os.listdir(os.path.join(base_path, i_model))
    list_files = sorted(list_files)

    for i_file in list_files:
        sbml_file = os.path.join(base_path, i_model, i_file)
        model_name, other_stuff = i_file.split(".", 1)
        model_output_dir = os.path.join(
            models_path, i_model, model_name)

        # get new_observables()
        print('Current Model: ' + i_model + '_' + model_name)

        try:
            # Append additional row in .tsv file
            tsv_table = tsv_table.append({}, ignore_index=True)

            # define the model id
            tsv_table.loc[counter].id = \
                '{' + i_model + '}' + '_' + '{' + i_file + '}'

            # read accompanying sbml file
            file = libsbml.readSBML(sbml_file)
            all_properties = file.getModel()
            num_states = len(all_properties.getListOfSpecies())
            num_reactions = len(all_properties.getListOfReactions())

            # fill in .tsv file
            tsv_table.loc[counter].states = num_states
            tsv_table.loc[counter].reactions = num_reactions

            # Create SBML importer
            sbml_importer = amici.SbmlImporter(sbml_file)

            # SBML2AMICI
            sbml_importer.sbml2amici(
                model_name, model_output_dir, verbose=False)

            # Write 'OK' in 'error_message' column
            tsv_table.loc[counter].error_message = 'OK'

            # increase counter by 1
            counter = counter + 1

        except Exception as e:
            error_info = str(e)
            print(error_info)
            logging.exception('Model failed: %s, %s', i_model, i_file)
            logging.info('\n')

            # Write the error message in 'error_message' column
            tsv_table.loc[counter].error_message = error_info
            counter = counter + 1

# save .tsv file
tsv_table.to_csv(
    path_or_buf=os.path.join(models_base_path, 'amici_import_summary.tsv'),
    sep='\t', index=False)
