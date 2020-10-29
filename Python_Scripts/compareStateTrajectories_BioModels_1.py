"""Simulate trajectories for all biomodels models and load reference
trajectories."""

# Attention:    boundary conditions are not being simulated by COPASI!
# all trajectories simulated by COPASI were simulated with absolute and relative tolerances 1e-14 & 1e-14,
# except three models where 1e-12 & 1e-12 had to be used.

from execute_loadModels import all_settings
import amici.plotting
import numpy as np
import libsbml
import pandas as pd
import os

from C import (
    DIR_MODELS_BIOMODELS, DIR_MODELS_AMICI, DIR_MODELS_TRAJ_REF_BIOMODELS,
    DIR_MODELS_TRAJ_REF, DIR_MODELS_SEDML, DIR_MODELS_TRAJ_AMICI)


def compStaTraj_BioModels():
    # set settings for simulation
    for solAlg in [1, 2]:
        linSol = 9
        Tolerance_combination = [[1e-3, 1e-3], [1e-6, 1e-6], [1e-16, 1e-8],
                                 [1e-12, 1e-12], [1e-14, 1e-14]]
        MultistepMethod = 'BDF'
        if solAlg == 1:
            MultistepMethod = 'Adams'

        for iTolerance in Tolerance_combination:
            # split atol and rtol for naming purposes
            atol, rtol = iTolerance

            # get all AMICI compatible models
            list_directory_amici = sorted(os.listdir(DIR_MODELS_AMICI))

            # iterate over the "sedml" models
            for iMod in range(0, len(list_directory_amici)):
                iModel = list_directory_amici[iMod]
                print(iModel)

                if not os.path.exists(
                        os.path.join(DIR_MODELS_BIOMODELS, iModel)):
                    print("Model is not part of Biomodels")
                    continue

                list_files = sorted(os.listdir(os.path.join(
                    DIR_MODELS_SEDML, iModel, 'sbml_models')))

                # iterate over the sbml models
                for iFile in list_files:
                    # iFile without .sbml extension
                    iFile, extension = iFile.split('.', 1)

                    # more important model-dependent paths
                    #  path to the original copasi simulation
                    sbml_path = os.path.join(
                        DIR_MODELS_SEDML, iModel, 'sbml_models',
                        iFile + '.sbml')

                    # Get whole model
                    try:
                        model = all_settings(iModel, iFile)
                    except Exception as e:
                        print(f'Model {iModel} failed ', e)
                        continue

                    ######### COPASI simulatiom
                    # open new .csv file with COPASI simulation trajectories
                    if os.path.exists(os.path.join(
                            DIR_MODELS_TRAJ_REF_BIOMODELS,
                            f'Original_COPASI_{iModel}_14_14.tsv')):
                        tsv_file = pd.read_csv(os.path.join(
                            DIR_MODELS_TRAJ_REF_BIOMODELS,
                            f'Original_COPASI_{iModel}_14_14.tsv'),
                            sep='\t')
                    else:
                        # TODO Y Why the alternative?
                        tsv_file = pd.read_csv(os.path.join(
                            DIR_MODELS_TRAJ_REF_BIOMODELS,
                            f'Original_COPASI_{iModel}_12_12.tsv'),
                            sep='\t')

                    # columns names of .tsv file and alter .tsv file
                    column_names = list(tsv_file.columns)
                    column_names.remove('# Time')
                    column_names = column_names[:len(column_names) - 1]
                    position = []

                    # TODO Y ????
                    del_counter = 0
                    for iName in range(0, len(column_names)):
                        if 'Values[' in column_names[iName - del_counter]:
                            column_names.remove(
                                column_names[iName - del_counter])
                            position.append(iName)
                            del_counter += 1
                    del tsv_file['# Time']
                    tsv_file.drop(
                        tsv_file.columns[len(tsv_file.columns) - 1],
                        axis=1, inplace=True)
                    if len(position) != 0:
                        tsv_file = tsv_file.drop(
                            tsv_file.columns[position], axis=1)

                    ########## model simulation
                    # Create solver instance
                    solver = model.getSolver()

                    # set all settings
                    solver.setAbsoluteTolerance(atol)
                    solver.setRelativeTolerance(rtol)
                    solver.setLinearSolver(linSol)
                    solver.setLinearMultistepMethod(solAlg)

                    # set stability flag for Adams-Moulton
                    if solAlg == 1:
                        solver.setStabilityLimitFlag(False)

                    # Simulate model
                    print("Simulating with AMICI")
                    sim_data = amici.runAmiciSimulation(model, solver)

                    # If AMICI failed, we cannot write any trajectory
                    if sim_data['status'] < 0:
                        continue

                    # np.set_printoptions(threshold=8, edgeitems=2)
                    # Get state trajectory
                    state_trajectory = sim_data['x']

                    # prune out constant species for trajectory comparison
                    # open sbml file
                    sbml_model = libsbml.readSBML(sbml_path)
                    delete_ind = [
                        iSpec for iSpec in
                        range(sbml_model.getModel().getNumSpecies())
                        if sbml_model.getModel().getSpecies(
                            iSpec).getBoundaryCondition()
                           is True]
                    state_trajectory = np.delete(
                        state_trajectory, delete_ind, 1)

                    # Adjustment for the 'Froehlich2018' model
                    # TODO Y Why?
                    if iModel == 'Froehlich2018':
                        state_trajectory = np.delete(
                            state_trajectory, np.s_[1177:1178], axis=1)

                    # Convert ndarray 'state-trajectory' to data frame + save it and modified COPASI file
                    df_state_trajectory = pd.DataFrame(
                        columns=column_names, data=state_trajectory)

                    # Store simulations
                    amici_result_file = os.path.join(
                        DIR_MODELS_TRAJ_AMICI,
                        f'trajectories_{MultistepMethod}_{atol}_{rtol}',
                        iModel, iFile + '_amici_simulation.csv')
                    os.makedirs(os.path.dirname(amici_result_file),
                                exist_ok=True)
                    df_state_trajectory.to_csv(
                        amici_result_file, sep='\t', index=False)

                    # TODO Y only do this once if at all
                    ref_result_file = os.path.join(
                        DIR_MODELS_TRAJ_REF, iModel,
                        iFile + '_reference_simulation.csv')
                    if not os.path.exists(ref_result_file):
                        os.makedirs(os.path.dirname(ref_result_file),
                                    exist_ok=True)
                        tsv_file.to_csv(ref_result_file, sep='\t', index=False)

                    # to know where one is
                    print(f'Model {iModel} successfully completed')


# call function with no models to delete
compStaTraj_BioModels()
