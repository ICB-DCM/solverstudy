# script 2 to compare state trajectories from JWS with trajectories of the simulation
# => compares state trajectories

# Attention:    boundary conditions are not being simulated by JWS!

import os
import numpy as np
import pandas as pd
import time

from C import (
    DIR_MODELS_JSON, DIR_MODELS_SEDML, DIR_MODELS_BIOMODELS, DIR_MODELS_AMICI,
    DIR_MODELS_REF_TRAJECTORIES)


# upper and lower boundaries for the absolute and relative errors
AbsError_1 = range(-20, 10)
RelError_2 = range(-20, 10)

# loop over all folders
for solAlg in [1, 2]:
    linSol = 9
    if solAlg == 1:
        MultistepMethod = 'Adams'
        Tolerance_combination = [
            [1e-3,1e-3], [1e-6,1e-3], [1e-6,1e-6],
            [1e-12,1e-12], [1e-16,1e-8]]
    elif solAlg == 2:
        MultistepMethod = 'BDF'
        Tolerance_combination = [
            [1e-3,1e-3], [1e-6,1e-3], [1e-6,1e-6], [1e-12,1e-12],
            [1e-16,1e-8], [1e-14,1e-14], [1e-16,1e-16]]
    for iTolerance in Tolerance_combination:

        # split atol and rtol for naming purposes
        atol_exp = str(iTolerance[0])
        rtol_exp = str(iTolerance[1])
        if len(atol_exp) != 2:
            atol_exp = '0' + atol_exp
        if len(rtol_exp) != 2:
            rtol_exp = '0' + rtol_exp

        # create folder for all results for the given method and tolerances
        results_dir_base = os.path.join(
            DIR_MODELS_JSON,
            f'json_files_all_results_{MultistepMethod}_{atol_exp}_{rtol_exp}')
        if not os.path.exists(results_dir_base):
            os.makedirs(results_dir_base)

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

                # create folder for all .csv files of the results
                #  for the given errors
                results_dir = os.path.join(
                    results_dir_base, f'json_files_{abs_str}_{rel_str}')
                if not os.path.exists(results_dir):
                    os.makedirs(results_dir)

                # set counter
                counter = 0

                # get all models
                # TODO Y Here we need to only iterate over AMICI, right?
                list_directory_amici = sorted(os.listdir(DIR_MODELS_AMICI))

                # measure time needed for all mdoels
                start_time = time.time()

                # iterate over all models again
                for iMod in range(0, len(list_directory_amici)):
                    iModel = list_directory_amici[iMod]
                    list_files = sorted(os.listdir(os.path.join(
                        DIR_MODELS_SEDML, iModel, 'sbml_models')))

                    for iFile in list_files:
                        print(f"    {iModel} :: {iFile}")

                        # iFile without .sbml extension
                        iFile, extension = iFile.split('.', 1)

                        # important paths
                        # TODO Y I fixed the path (how did this work???)
                        reference_path = os.path.join(
                            DIR_MODELS_REF_TRAJECTORIES, iModel, iFile)
                        old_json_save_path = os.path.join(
                            DIR_MODELS_JSON,
                            f'json_files_{MultistepMethod}_'
                            f'{atol_exp}_{rtol_exp}',
                            iModel, iFile)
                        new_json_save_path = os.path.join(
                            DIR_MODELS_JSON,
                            f'json_files_all_results_{MultistepMethod}_'
                            f'{atol_exp}_{rtol_exp}',
                            f'json_files_{abs_str}_{rel_str}',
                            iModel, iFile)
                        sedml_path = os.path.join(
                            DIR_MODELS_SEDML, iModel, iModel + '.sedml')
                        sbml_path = os.path.join(
                            DIR_MODELS_SEDML, iModel, 'sbml_models',
                            iFile + '.sbml')
                        BioModels_path = DIR_MODELS_BIOMODELS

                        if os.path.exists(
                                os.path.join(BioModels_path, iModel)):
                            print('Model is still not part of JWS-database!')
                        else:
                            if not os.path.exists(old_json_save_path):
                                print('Model ' + iModel + '_' + iFile + ' crashed some other way!')
                            else:
                                # create folder
                                if not os.path.exists(os.path.join(
                                        results_dir, iModel, iFile)):
                                    os.makedirs(os.path.join(
                                        results_dir, iModel, iFile))

                                # open jws_simulation .csv file
                                tsv_file = pd.read_csv(os.path.join(
                                    reference_path, 'JWS_simulation.csv'),
                                    sep='\t')

                                # open model_simulation .csv file
                                df_state_trajectory = pd.read_csv(os.path.join(
                                    old_json_save_path,
                                    iFile + '_model_simulation.csv'),
                                    sep='\t')

                                # columns names of .tsv file
                                column_names = list(tsv_file.columns)
                                column_names.remove('time')
                                del tsv_file['time']

                                # comparison
                                amount_col = len(column_names)
                                first_col = column_names[0]
                                amount_row = len(df_state_trajectory[first_col])
                                df_single_error = pd.DataFrame(
                                    columns=column_names,
                                    data=np.zeros((amount_row, amount_col)))
                                df_trajectory_error = pd.DataFrame(
                                    columns=column_names,
                                    data=np.zeros((1, amount_col)))
                                df_whole_error = pd.DataFrame(
                                    columns=['trajectories_match'],
                                    data=np.zeros((1, 1)))

                                # single error
                                for iCol in column_names:
                                    for iRow in range(0, amount_row):
                                        rel_tol = abs(
                                            (df_state_trajectory.at[iRow, iCol] - tsv_file.at[iRow,iCol]) /
                                             df_state_trajectory.at[iRow, iCol])
                                        abs_tol = abs(df_state_trajectory.at[iRow, iCol] - tsv_file.at[iRow,iCol])
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
                                df_single_error.to_csv(
                                    path_or_buf=os.path.join(
                                        new_json_save_path,
                                        'single_error.csv'),
                                    sep='\t', index=False)
                                df_trajectory_error.to_csv(
                                    path_or_buf=os.path.join(
                                        new_json_save_path,
                                        'trajectory_error.csv'),
                                    sep='\t', index=False)
                                df_whole_error.to_csv(
                                    path_or_buf=os.path.join(
                                        new_json_save_path,
                                        'whole_error.csv'),
                                    sep='\t', index=False)

                # print number of all models with correct state trajectories
                print("Amount of models with correct state trajectories: "
                      f"{str(counter)}")
                # print time needed for the comparison
                print(f"Time needed: {str(time.time() - start_time)}")
