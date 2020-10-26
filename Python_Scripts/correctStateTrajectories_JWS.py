# check for correctness of JWS state trajectories and do a pre-selection of biomodels based on their ability to be simulated

import os
import shutil
import pandas as pd
from setTime_BioModels import *

# important paths --- for abs_error = rel_error = 1e-4, abs_tolerance = rel_tolerance = 1e-12 and BDF
base_path = '../../Benchmarking_of_numerical_ODE_integration_methods'
json_path = base_path + '/json_files/json_files_all_results_BDF_12_12/json_files_1e-04_1e-04'
sedml_path = base_path + '/sedml_models'
old_path = base_path + '/sbml2amici/amici_models_newest_version_0.10.19'
new_path = base_path + '/sbml2amici/correct_amici_models_paper'

# copy all successfully imported amici models and eliminate those witch don't have matching state trajectories to JWS
if not os.path.exists(new_path):
    shutil.copytree(old_path, new_path)

# set counter
counter_true = 0
counter_model = 0

# open all .csv files
list_directory_sedml = sorted(os.listdir(new_path))

for iModel in list_directory_sedml:

    list_directory_sbml = sorted(os.listdir(new_path + '/' + iModel))

    for iFile in list_directory_sbml:

        iFile_name = iFile

        # check if file exists in correct_amici_models folder
        if os.path.exists(new_path + '/' + iModel + '/' + iFile_name):
            counter_model = counter_model + 1

            # check if file exists in json folder
            if os.path.exists(json_path + '/' + iModel + '/' + iFile_name):
                csv_file = pd.read_csv(json_path + '/' + iModel + '/' + iFile_name + '/whole_error.csv', sep='\t')

                # check for True
                if csv_file['trajectories_match'][0] == True:
                    counter_true = counter_true + 1
                else:
                    print(iModel + '_' + iFile_name + ' is False!')

                    # delete folder
                    shutil.rmtree(new_path + '/' + iModel + '/' + iFile_name)

            else:
                # check for BioModels
                try:
                    sim_start_time, sim_end_time, sim_num_time_points, ybound = timePointsBioModels(iModel)
                    counter_true = counter_true + 1
                except:
                    print('BioModels model could not be imported!')

                    # delete folder
                    shutil.rmtree(new_path + '/' + iModel + '/' + iFile_name)

        else:
            print(iModel + '_' + iFile_name + ' has already been deleted!')
            counter_model = counter_model + 1

print(counter_true)
print(counter_model)
counter_difference = counter_model - counter_true
print('Difference: ' + str(counter_difference))

# delete all empty folders
delete_counter = 0
list_directory_sedml = sorted(os.listdir(new_path))
for iModel in list_directory_sedml:
    if len(os.listdir(new_path + '/' + iModel)) == 0:
        os.rmdir(new_path + '/' + iModel)
        print('Deleted model ' + iModel)
        delete_counter = delete_counter + 1

# print the number of deleted folders
print('Delete Counter = ' + str(delete_counter))
