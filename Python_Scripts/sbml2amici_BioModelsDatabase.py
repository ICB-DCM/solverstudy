# AMICI import of a BioModels sbml model from the model collection

import libsbml
import amici
import os
import logging
import pandas as pd


# create .tsv file
tsv_table = pd.DataFrame(columns=['id', 'states', 'reactions', 'error_message'])

# important paths
models_base_path = "../../Benchmarking_of_numerical_ODE_integration_methods/sbml2amici"
models_path = models_base_path + "/amici_models_newest_version_0.10.19"
base_path = "../../Benchmarking_of_numerical_ODE_integration_methods/BioModelsDatabase_models"

# create directory for all future amici models
if not os.path.exists(models_path):
    os.makedirs(models_path)

# create logger object
logger = logging.getLogger()

# initialize the log settings
logging.basicConfig(filename=models_base_path + '/all_logs_Biomodels',level=logging.DEBUG)

# list of all directories + SBML files
list_directory = os.listdir(base_path)
list_directory = sorted(list_directory)

# set row-counter for .tsv file
counter = 0

for models in list_directory:
    list_files = os.listdir(base_path + '/' + models + '/sbml_models')
    list_files = sorted(list_files)

    for files in list_files:
        sbml_file = base_path + '/' + models + '/sbml_models/' + files
        model_name, other_stuff = files.split(".",1)
        model_output_dir = models_path + '/' + models + '/' + model_name

        print('Current Model: ' + models + '_' + model_name)

        try:
            # Append additional row in .tsv file
            tsv_table = tsv_table.append({}, ignore_index=True)

            # define the model id
            tsv_table.loc[counter].id = '{' + models + '}' + '_' + '{' + files + '}'

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
            sbml_importer.sbml2amici(model_name,
                        model_output_dir,
                        verbose=False)

            # Write 'OK' in 'error_message' column
            tsv_table.loc[counter].error_message = 'OK'

            # increase counter by 1
            counter = counter + 1

        except Exception as e:
            error_info = str(e)
            print(error_info)
            logging.exception('Model failed: %s, %s', models, files)
            logging.info('\n')

            # Write the error message in 'error_message' column
            tsv_table.loc[counter].error_message = error_info
            counter = counter + 1

# save .tsv file
tsv_table.to_csv(path_or_buf=models_base_path + '/table_BioModelsDatabase.tsv', sep='\t', index=True)
