# check for correctness of BioModels state trajectories

import os
import shutil
import pandas as pd
import sys

from C import (
    DIR_MODELS_BIOMODELS, DIR_MODELS_AMICI_FINAL, DIR_MODELS_TRAJ_AMICI,
    DIR_MODELS_AMICI)

# important paths --- for abs_error = rel_error = 1e-4,
#  abs_tolerance = rel_tolerance = 1e-12 and BDF
trajectory_results_path = os.path.join(
    DIR_MODELS_TRAJ_AMICI,
    'comparisons_BDF_01e-12_01e-12/comparisons_1e-04_1e-04')
new_path = DIR_MODELS_AMICI_FINAL

# set counter
counter_true = 0
counter_model = 0

# open all .csv files
list_directory_amici= sorted(os.listdir(DIR_MODELS_AMICI_FINAL))

for iModel in list_directory_amici:
    # skip if not a biomodels model
    if not os.path.exists(
            os.path.join(DIR_MODELS_BIOMODELS, iModel)):
        continue

    # check if file exists in json folder
    csv_file_name = os.path.join(
        trajectory_results_path, iModel, iModel + '_whole_error.csv')
    if os.path.exists(csv_file_name):
        csv_file = pd.read_csv(csv_file_name, sep='\t')

        # check for True
        if csv_file['trajectories_match'][0]:
            print(f"Keeping {iModel} {iModel}")
            counter_true = counter_true + 1
        else:
            print(iModel + '_' + iModel + ' is False!')

            # delete folder
            shutil.rmtree(os.path.join(
                new_path, iModel, iModel))

    counter_model = counter_model + 1

# print information about the result
print("Counter_true:", counter_true)
print("Counter_model:", counter_model)
counter_difference = counter_model - counter_true
print('Difference: ' + str(counter_difference))

# delete all empty folders
delete_counter = 0
list_directory_amici = sorted(os.listdir(new_path))
for iModel in list_directory_amici:
    if len(os.listdir(os.path.join(new_path, iModel))) == 0:
        os.rmdir(os.path.join(new_path, iModel))
        print('Deleted model ' + iModel)
        delete_counter = delete_counter + 1

# print the number of deleted folders
print('Delete Counter = ' + str(delete_counter))
