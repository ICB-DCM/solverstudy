# script 2 to compare state trajectories from JWS with trajectories of the simulation
# => compares state trajectories

# Attention:    boundary conditions are not being simulated by JWS!

import os
import numpy as np
import pandas as pd
import time

from C import (
    DIR_MODELS_TRAJ_AMICI, DIR_MODELS_SEDML, DIR_MODELS_BIOMODELS, DIR_MODELS_AMICI,
    DIR_MODELS_TRAJ_REF)


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
        atol, rtol = iTolerance

        print(f"Setting: {MultistepMethod} {atol} {rtol}")

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

                print(f"  Tolerances: abs={abs_str} rel={rel_str}")

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
                    if os.path.exists(
                            os.path.join(DIR_MODELS_BIOMODELS, iModel)):
                        continue

                    list_files = sorted(os.listdir(os.path.join(
                        DIR_MODELS_AMICI, iModel)))

                    for iFile in list_files:
                        # important paths
                        # TODO Y I fixed the path (how did this work???)
                        reference_path = os.path.join(
                            DIR_MODELS_TRAJ_REF, iModel,
                            iFile + '_reference_simulation.csv')
                        old_json_save_path = os.path.join(
                            DIR_MODELS_TRAJ_AMICI,
                            f'trajectories_{MultistepMethod}_{atol}_{rtol}',
                            iModel,
                            iFile + '_amici_simulation.csv')
                        new_json_save_path = os.path.join(
                            DIR_MODELS_TRAJ_AMICI,
                            f'comparisons_{MultistepMethod}_{atol}_{rtol}',
                            f'comparisons_{abs_str}_{rel_str}',
                            iModel)

                        if not os.path.exists(old_json_save_path):
                            continue

                        # create folder
                        if not os.path.exists(new_json_save_path):
                            os.makedirs(new_json_save_path)

                        # open jws_simulation .csv file
                        tsv_file = pd.read_csv(
                            reference_path,
                            sep='\t')

                        # open model_simulation .csv file
                        df_state_trajectory = pd.read_csv(
                            old_json_save_path,
                            index_col=0,
                            sep='\t')

                        # TODO Y tidy this up
                        tsv_file.drop('time', axis=1, inplace=True)

                        if tsv_file.shape != df_state_trajectory.shape:
                            raise ValueError(
                                "Simulation file shapes do not match for "
                                f"{iModel} {iFile}")

                        # comparison
                        df_whole_error = pd.DataFrame(
                            columns=['trajectories_match'],
                            data=np.zeros((1, 1)))

                        df_abs = (df_state_trajectory - tsv_file).abs()
                        df_rel = (df_abs / df_state_trajectory).abs()
                        df_single_error = (
                            (df_abs <= abs_error) | (df_rel <= rel_error))

                        if df_single_error.all().all():
                            df_whole_error.at[0, 'trajectories_match'] = 1
                            counter = counter + 1
                        else:
                            df_whole_error.at[0, 'trajectories_match'] = 0

                        # save outcome
                        df_whole_error.to_csv(
                            path_or_buf=os.path.join(
                                new_json_save_path,
                                iFile + '_whole_error.csv'),
                            sep='\t', index=False)

                # print number of all models with correct state trajectories
                print("  Amount of models with correct state trajectories: "
                      f"{str(counter)}")
                # print time needed for the comparison
                print(f"  Time needed: {str(time.time() - start_time)}")
