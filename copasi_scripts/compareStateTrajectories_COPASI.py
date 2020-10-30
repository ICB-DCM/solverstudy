# script 2 to compare state trajectories from JWS with trajectories of the simulation
# => compares state trajectories

# Attention:    boundary conditions are not being simulated by JWS!

from execute_loadModels import *
from JWS_changeValues import *
from colourDataFrame import *
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


def compStaTraj_COPASI():
    # upper and lower boundaries for the absolute and relative errors
    AbsError_1 = range(-4,-3)
    RelError_2 = range(-4,-3)

    # folder
    folder_path = '../copasi_sim'
    jws_path = './FigS1_preselection'

    # iterate over all error combinations
    for iAbsError in range(0, len(AbsError_1)):
        for iRelError in range(0, len(RelError_2)):

            if iAbsError != iRelError:
                continue

            # set errors
            abs_error = float('1e' + str(AbsError_1[iAbsError]))
            rel_error = float('1e' + str(RelError_2[iRelError]))

            # int2str
            abs_str = '{:.0e}'.format(float(abs_error))
            rel_str = '{:.0e}'.format(float(rel_error))

            print(f"TOLERANCES: abs={abs_str} rel={rel_str}")

            # set counter
            counter = 0

            # iterate over all models
            list_models_with_simulationData = sorted(os.listdir(folder_path))
            for iMod in range(0, len(list_models_with_simulationData)):
                iModel = list_models_with_simulationData[iMod]
                iModel = 'aguda1999_fig5c'

                list_files = sorted(os.listdir(folder_path + '/' + iModel))
                for iFile in list_files:
                    print(f"    {iModel} :: {iFile}")
                    iFile = 'model0_aguda1'

                    # important paths
                    copasi_path = folder_path + '/' + iModel + '/' + iFile
                    jws_path = jws_path + '/json_files_2_2_9_14_14/' + iModel + '/' + iFile
                    BioModels_path = './BioModelsDatabase_models'

                    # open jws_simulation .csv file
                    tsv_file = pd.read_csv(jws_path + '/' + iFile + '_JWS_simulation.csv', sep='\t')

                    # open COPASI .tsv file
                    df_state_trajectory = pd.read_csv(copasi_path + '/copasi_results_0.tsv', sep='\t')

                    # columns names of JWS file
                    column_names_JWS = list(tsv_file.columns)
                    column_names_JWS.remove('time')
                    del tsv_file['time']

                    # column names of COPASI file
                    column_names_COPASI = []
                    column_names_2 = list(df_state_trajectory.columns)
                    column_names_2.remove('Time')
                    column_names_2.remove('(Timer)CPU Time')
                    column_names_2.remove('(Timer)Wall Clock Time')
                    del df_state_trajectory['Time']
                    del df_state_trajectory['(Timer)CPU Time']
                    del df_state_trajectory['(Timer)Wall Clock Time']
                    for ColName in column_names_2:
                        _,colname = ColName.split('[')
                        colname,_ = colname.split(']')
                        column_names_COPASI.append(colname)
                    df_state_trajectory.columns = column_names_COPASI

                    # comparison
                    if column_names_COPASI != column_names_JWS:
                        print('column names do not match!')
                        sys.exit()
                    amount_col = len(column_names_JWS)
                    first_col = column_names_JWS[0]
                    amount_row = len(df_state_trajectory[first_col])
                    df_single_error = pd.DataFrame(columns=column_names_JWS, data=np.zeros((amount_row, amount_col)))
                    df_trajectory_error = pd.DataFrame(columns=column_names_JWS, data=np.zeros((1, amount_col)))
                    df_whole_error = pd.DataFrame(columns=['trajectories_match'], data=np.zeros((1, 1)))

                    # single error
                    for iCol in column_names_JWS:
                        for iRow in range(0, amount_row):
                            rel_tol = abs((df_state_trajectory.at[iRow, iCol] - tsv_file.at[iRow,iCol]) / df_state_trajectory.at[iRow, iCol])
                            abs_tol = abs(df_state_trajectory.at[iRow, iCol] - tsv_file.at[iRow,iCol])
                            if rel_tol <= rel_error or abs_tol <= abs_error:
                                df_single_error.at[iRow, iCol] = 1
                            else:
                                df_single_error.at[iRow, iCol] = 0

                    # trajectory error
                    for iCol in column_names_JWS:
                        if sum(df_single_error[iCol]) == amount_row:
                            df_trajectory_error.at[0, iCol] = 1
                        else:
                            df_trajectory_error.at[0, iCol] = 0

                    # whole error
                    error_list = []
                    for iCol in column_names_JWS:
                        error_list.append(df_trajectory_error.at[0, iCol])
                    if sum(error_list) == amount_col:
                        df_whole_error.at[0, 'trajectories_match'] = 1
                    else:
                        df_whole_error.at[0, 'trajectories_match'] = 0

                    # adjust counter and print outcome
                    if df_whole_error.at[0, 'trajectories_match'] == 1:
                        print('Model ' + iModel + '_' + iFile + ' has matching state trajectories!')
                        counter = counter + 1
                    elif df_whole_error.at[0, 'trajectories_match'] == 0:
                        print('Model ' + iModel + '_' + iFile + ' has wrong state trajectories!')

                    # print outcome
                    a = 4


        # print number of all models with correct state trajectories and display running time
        print('Amount of models with correct state trajectories: ' + str(counter))


# call function
compStaTraj_COPASI()
