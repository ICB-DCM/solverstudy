# check for correctness of BioModels state trajectories

import os
import shutil
import pandas as pd
import sys

# important paths --- for abs_error = rel_error = 1e-4, abs_tolerance = rel_tolerance = 1e-12 and BDF
base_path = '../../Benchmarking_of_numerical_ODE_integration_methods'
old_sbml2amici_path = base_path + '/sbml2amici/correct_amici_models_paper'
biomodels_trajectories_path = base_path + '/biomodels_files/COPASI_all_results_BDF_12_12/COPASI_1e-04_1e-04'

# set counter
counter_true = 0
counter_model = 0

# open all .csv files
list_directory_biomodels = sorted(os.listdir(biomodels_trajectories_path))

for iModel in list_directory_biomodels:

    list_directory_amici_files = sorted(os.listdir(old_sbml2amici_path))
    list_directory_csv_files = sorted(os.listdir(biomodels_trajectories_path + '/' + iModel))

    # check if the biomodel is indeed in the amici folder --- if not something went wrong
    if iModel in list_directory_amici_files:

        # check if .csv file exists in COPASI folder and if so, open it
        if not 'whole_error.csv' in list_directory_csv_files:
            print('Somehow the file containing the information about the correctness of the model is missing! '
                  'Maybe something went wrong in step 1.6 or the file got deleted!')
            sys.exit(0)
        else:
            csv_file = pd.read_csv(biomodels_trajectories_path + '/' + iModel + '/whole_error.csv', sep='\t')

        # check for True
        if csv_file['trajectories_match'][0] == True:
            counter_true = counter_true + 1
        else:
            print(iModel + ' is False!')

            # delete folder in benchmak collection
            shutil.rmtree(old_sbml2amici_path + '/' + iModel)

    else:
        print('The BioModel ' + iModel + ' is not contained in the almost finished benchmark collection, although it should be! '
              'Maybe something went wrong in the steps 1.3 to 1.6!')

    counter_model = counter_model + 1

# print information about the result
print(counter_true)
print(counter_model)
counter_difference = counter_model - counter_true
print('Difference: ' + str(counter_difference))

# delete all empty folders
delete_counter = 0
list_directory_amici = sorted(os.listdir(old_sbml2amici_path))
for iModel in list_directory_amici:
    if len(os.listdir(list_directory_amici + '/' + iModel)) == 0:
        os.rmdir(list_directory_amici + '/' + iModel)
        print('Deleted model ' + iModel)
        delete_counter = delete_counter + 1

# print the number of deleted folders
print('Delete Counter = ' + str(delete_counter))
