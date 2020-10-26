# script 2 to compare state trajectories from BioModels with trajectories of the simulation created by COPASI
# all data from COPASI is stored in the 'Data' folder of the repository
# => creates two important .tsv files

# Attention:    boundary conditions are not being simulated by COPASI!
# all trajectories simulated by COPASI were simulated with absolute and relative tolerances 1e-14 & 1e-14,
# except three models where 1e-12 & 1e-12 had to be used.

from execute_loadModels import *
from JWS_changeValues import *
#from colourDataFrame import *
import amici.plotting
import numpy as np
import matplotlib.pyplot as plt
import libsbml
import libsedml
import time
import statistics
import pandas as pd
import os
import urllib.request
import json
import itertools
import time


def compStaTraj_BioModels_2(MultistepMethod, atol, rtol):
    # upper and lower boundaries for the absolute and relative errors
    AbsError_1 = range(-20, 10)
    RelError_2 = range(-20, 10)

    # important paths
    base_path = '../../Benchmarking_of_numerical_ODE_integration_methods'
    trajectory_path = base_path + '/biomodels_files/StateTrajectories_BioModels_COPASI_Data'
    comparison_files_path = base_path + '/biomodels_files/' + MultistepMethod + '_' + atol + '_' + rtol
    all_biomodels_path = base_path + '/BioModelsDatabase_models'

    # create folder for all results
    if not os.path.exists(comparison_files_path):
        os.makedirs(comparison_files_path)

    # iterate over all error combinations
    for iAbsError in range(0, len(AbsError_1)):
        for iRelError in range(0, len(RelError_2)):

            # stop if somehow the error thresholds do not match
            if iAbsError != iRelError:
                print('The error threshold values somehow do not match!')
                sys.exit(0)

            # set threshold errors
            abs_error = float('1e' + str(AbsError_1[iAbsError]))
            rel_error = float('1e' + str(RelError_2[iRelError]))

            # int2str
            abs_str = '{:.0e}'.format(float(abs_error))
            rel_str = '{:.0e}'.format(float(rel_error))

            # to see where the script is at the moment
            print(f"TOLERANCES: abs={abs_str} rel={rel_str}")

            # create folder for all .csv files of the results
            if not os.path.exists(comparison_files_path + '/COPASI_' + abs_str + '_' + rel_str):
                os.makedirs(comparison_files_path + '/COPASI_' + abs_str + '_' + rel_str)

            # set counter
            counter = 0

            # get all biomodels from the latter created folder in 'biomodels_files'
            list_directory_bio = sorted(os.listdir(trajectory_path))

            # iterate over all models again
            for iMod in range(0, len(list_directory_bio)):
                iModel = list_directory_bio[iMod]
                list_files = sorted(os.listdir(all_biomodels_path + '/' + iModel + '/sbml_models'))

                for iFile in list_files:
                    print(f"    {iModel} :: {iFile}")

                    # iFile without .xml extension
                    iFile, extension = iFile.split('.', 1)

                    # more important paths
                    old_bio_save_path = trajectory_path + '/' + iModel
                    new_bio_save_path = comparison_files_path + '/COPASI_' + abs_str + '_' + rel_str + '/' + iModel

                    if not os.path.exists(old_bio_save_path):
                        print('Model ' + iModel + '_' + iFile + ' crashed some other way!')
                    else:

                        # create folder for all .csv files with the final trajectory comparison results
                        if not os.path.exists(new_bio_save_path):
                            os.makedirs(new_bio_save_path)

                        # open COPASI_simulation .tsv file
                        tsv_file = pd.read_csv(
                            f"{old_bio_save_path}/COPASI_{iModel}_{MultistepMethod}_{atol}_{rtol}.tsv", sep='\t')

                        # open AMICI model_simulation .tsv file
                        df_state_trajectory = pd.read_csv(
                            f"{old_bio_save_path}/AMICI_{iModel}_{MultistepMethod}_{atol}_{rtol}.tsv", sep='\t')

                        # columns names of COPASI file
                        column_names = list(tsv_file.columns)

                        # comparison
                        amount_col = len(column_names)
                        first_col = column_names[0]
                        amount_row = len(df_state_trajectory[first_col])
                        df_single_error = pd.DataFrame(columns=column_names, data=np.zeros((amount_row, amount_col)))
                        df_trajectory_error = pd.DataFrame(columns=column_names, data=np.zeros((1, amount_col)))
                        df_whole_error = pd.DataFrame(columns=['trajectories_match'], data=np.zeros((1, 1)))

                        # single error
                        for iCol in column_names:
                            for iRow in range(0, amount_row):
                                rel_tol = abs((df_state_trajectory.at[iRow, iCol] - tsv_file.at[iRow, iCol]) /
                                              df_state_trajectory.at[iRow, iCol])
                                abs_tol = abs(df_state_trajectory.at[iRow, iCol] - tsv_file.at[iRow, iCol])
                                if rel_tol <= rel_error or abs_tol <= abs_error:
                                    df_single_error.at[iRow, iCol] = 1
                                else:
                                    df_single_error.at[iRow, iCol] = 0

                        # trajectory error
                        for iCol in column_names:
                            if sum(df_single_error[iCol]) == amount_row:
                                df_trajectory_error.at[0, iCol] = 1
                            else:
                                df_trajectory_error.at[0, iCol] = 0

                        # whole error
                        error_list = []
                        for iCol in column_names:
                            error_list.append(df_trajectory_error.at[0, iCol])
                        if sum(error_list) == amount_col:
                            df_whole_error.at[0, 'trajectories_match'] = 1
                        else:
                            df_whole_error.at[0, 'trajectories_match'] = 0

                        # adjust counter
                        if df_whole_error.at[0, 'trajectories_match'] == 1:
                            print('matching state trajectory!')
                            counter = counter + 1

                        # save outcome
                        df_single_error.to_csv(path_or_buf=new_bio_save_path + '/single_error.csv',
                                               sep='\t', index=False)
                        df_trajectory_error.to_csv(path_or_buf=new_bio_save_path + '/trajectory_error.csv',
                                                   sep='\t', index=False)
                        df_whole_error.to_csv(path_or_buf=new_bio_save_path + '/whole_error.csv',
                                              sep='\t', index=False)

            # print number of all models with correct state trajectories
            print('Amount of models with correct state trajectories: ' + str(counter))


###### set all necessary settings from the later script
for solAlg in [1, 2]:
    linSol = 9
    if solAlg == 1:
        MultistepMethod = 'Adams'
        Tolerance_combination = [[1e-3,1e-3], [1e-6,1e-6], [1e-16,1e-8], [1e-12,1e-12], [1e-14,1e-14]]
    elif solAlg == 2:
        MultistepMethod = 'BDF'
        Tolerance_combination = [[1e-3,1e-3], [1e-6,1e-6], [1e-16,1e-8], [1e-12,1e-12], [1e-14,1e-14]]

    for iTolerance in Tolerance_combination:
        # split atol and rtol for naming purposes
        atol = str(iTolerance[0])
        rtol = str(iTolerance[1])

        # call function
        compStaTraj_BioModels_2(MultistepMethod, atol, rtol)
