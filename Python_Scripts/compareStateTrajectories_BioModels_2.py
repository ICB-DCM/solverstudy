"""Compare the AMICI and COPASI trajectories, check for each model whether
to accept."""

# Attention:    boundary conditions are not being simulated by COPASI!
# all trajectories simulated by COPASI were simulated with absolute and
#  relative tolerances 1e-14 & 1e-14, except three models where
#  1e-12 & 1e-12 had to be used.

import numpy as np
import pandas as pd
import os

from C import (
    DIR_MODELS_TRAJ_AMICI, DIR_MODELS_AMICI, DIR_MODELS_BIOMODELS,
    DIR_MODELS_TRAJ_REF)


def compStaTraj_BioModels_2(MultistepMethod, atol, rtol):
    # upper and lower boundaries for the absolute and relative errors
    AbsError_1 = range(-20, 10)
    RelError_2 = range(-20, 10)

    print(f"Setting: {MultistepMethod} {atol} {rtol}")

    # iterate over all error combinations
    for iAbsError in range(0, len(AbsError_1)):
        for iRelError in range(0, len(RelError_2)):
            if iAbsError != iRelError:
                continue

            # set threshold errors
            abs_error = float('1e' + str(AbsError_1[iAbsError]))
            rel_error = float('1e' + str(RelError_2[iRelError]))

            # int2str
            abs_str = '{:.0e}'.format(float(abs_error))
            rel_str = '{:.0e}'.format(float(rel_error))

            # to see where the script is at the moment
            print(f"  Tolerances: abs={abs_str} rel={rel_str}")

            # set counter
            counter = 0

            list_directory_amici = sorted(os.listdir(DIR_MODELS_AMICI))

            # iterate over all "sedml" models
            for iMod in range(0, len(list_directory_amici)):
                iModel = list_directory_amici[iMod]
                if not os.path.exists(
                        os.path.join(DIR_MODELS_BIOMODELS, iModel)):
                    continue

                list_files = sorted(os.listdir(os.path.join(
                    DIR_MODELS_AMICI, iModel)))

                # iterate over all sbml models
                for iFile in list_files:
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

                    # open COPASI_simulation .tsv file
                    tsv_file = pd.read_csv(
                        reference_path, sep='\t')

                    # open AMICI model_simulation .tsv file
                    df_state_trajectory = pd.read_csv(
                        old_json_save_path,
                        sep='\t')

                    if tsv_file.shape != df_state_trajectory.shape:
                        raise ValueError("Simulation file shapes do not match")

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
            print('  Amount of models with correct state trajectories: ' + str(counter))


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
        atol, rtol = iTolerance

        # call function
        compStaTraj_BioModels_2(MultistepMethod, atol, rtol)
