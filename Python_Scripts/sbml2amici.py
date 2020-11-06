# AMICI import of a JWS sbml model from the model collection

import libsbml
import amici
import os
import logging
import pandas as pd

from C import (
    DIR_BASE, DIR_MODELS_REGROUPED, DIR_MODELS, DIR_MODELS_AMICI)

# create .tsv file
model_info = pd.read_csv(os.path.join(DIR_MODELS, 'model_summary.tsv'),
                         sep='\t')
model_info = model_info.join(pd.Series([''] * model_info.shape[0],
                                       name='amici_path'))
model_info = model_info.join(pd.Series([''] * model_info.shape[0],
                                       name='amici_import'))
model_info = model_info.join(pd.Series([''] * model_info.shape[0],
                                       name='id'))

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
for i_model in list_directory:
    list_files = os.listdir(os.path.join(base_path, i_model))
    list_files = sorted(list_files)

    for i_file in list_files:
        sbml_file = os.path.join(base_path, i_model, i_file)
        regrouped_path = os.path.relpath(sbml_file, DIR_MODELS)
        model_name, other_stuff = i_file.split(".", 1)
        model_output_dir = os.path.join(
            models_path, i_model, model_name)

        # get new_observables()
        print('Current Model: ' + i_model + '_' + model_name)

        # Append additional row in .tsv file
        model_row = model_info.loc[model_info['regrouped_path'] == regrouped_path]
        counter = int(model_row.index.values)

        model_info.loc[counter, 'id'] = '{' + i_model + '}' + '_' + \
                                        '{' + i_file + '}'

        try:
            # Create SBML importer
            sbml_importer = amici.SbmlImporter(sbml_file)

            # SBML2AMICI
            sbml_importer.sbml2amici(
                model_name, model_output_dir, verbose=False)

            # Write 'OK' in 'error_message' column
            model_info.loc[counter, 'amici_import'] = 'OK'
            model_info.loc[counter, 'amici_path'] = os.path.relpath(
                model_output_dir, DIR_MODELS)

        except Exception as e:
            error_info = str(e)
            print(error_info)
            logging.exception('Model failed: %s, %s', i_model, i_file)
            logging.info('\n')

            # Write the error message in 'error_message' column
            model_info.loc[counter, 'amici_import'] = error_info

# save .tsv file
model_info.to_csv(
    path_or_buf=os.path.join(models_base_path, 'model_summary.tsv'),
    sep='\t', index=False)
