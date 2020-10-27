# script 1 to compare state trajectories from BioModels with trajectories of the simulation created by COPASI
# all data from COPASI is stored in the 'Data' folder of the repository
# => creates two important .tsv files

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
    DIR_MODELS_TRAJ_REF, DIR_MODELS_SEDML)


def compStaTraj_BioModels():

    # important paths
    COPASI_data = '../Data/BioModels_AMICI_state_trajectory_comparison/StateTrajectories_BioModels_COPASI_Data'
    base_path = '../../Benchmarking_of_numerical_ODE_integration_methods'
    all_biomodels_path = base_path + '/BioModelsDatabase_models'
    simulable_biomodels_path = base_path + '/sbml2amici/correct_amici_models_paper'

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
            atol = iTolerance[0]
            rtol = iTolerance[1]
            _, save_atol = str('{:.1e}'.format(atol)).split('-')
            _, save_rtol = str('{:.1e}'.format(rtol)).split('-')

            # get all AMICI compatible models
            list_directory_amici = sorted(os.listdir(DIR_MODELS_AMICI))

            # iterate over the "sedml" models
            for iMod in range(0, len(list_directory_amici)):
                iModel = list_directory_amici[iMod]
                list_files = sorted(os.listdir(os.path.join(
                    DIR_MODELS_SEDML, iModel, 'sbml_models')))

                # iterate over the sbml models
                for iFile in list_files:
                    # iFile without .xml extension
                    iFile, extension = iFile.split('.', 1)

                    # more important model-dependent paths
                    #  path to the original copasi simulation
                    tsv_path = os.path.join(
                        DIR_MODELS_TRAJ_REF_BIOMODELS, iModel, iModel)
                    save_path = base_path + '/biomodels_files/StateTrajectories_BioModels_COPASI_Data/' + iModel
                    #  path of the sbml file
                    sbml_path = os.path.join(
                        DIR_MODELS_SEDML, iModel, 'sbml_models',
                        iFile + '.sbml')

                    # Open XML file
                    sbml_model = libsbml.readSBML(sbml_path)

                    # Get whole model
                    model = all_settings(iModel, iFile)

                    ######### COPASI simulatiom
                    # open new .csv file with COPASI simulation trajectories
                    if os.path.exists(os.path.join(
                            tsv_path, f'Original_COPASI_{iModel}_14_14.tsv')):
                        tsv_file = pd.read_csv(os.path.join(
                            tsv_path, f'Original_COPASI_{iModel}_14_14.tsv'),
                            sep='\t')
                    else:
                        # TODO Y Why the alternative?
                        tsv_file = pd.read_csv(os.path.join(
                            tsv_path, f'Original_COPASI_{iModel}_12_12.tsv'),
                            sep='\t')

                    # columns names of .tsv file and alter .tsv file
                    column_names = list(tsv_file.columns)
                    column_names.remove('# Time')
                    column_names = column_names[:len(column_names) - 1]
                    position = []
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
                    sim_data = amici.runAmiciSimulation(model, solver)

                    # np.set_printoptions(threshold=8, edgeitems=2)
                    for key, value in sim_data.items():
                        print('%12s: ' % key, value)

                    # Get state trajectory
                    state_trajectory = sim_data['x']

                    # Delete all trajectories for boundary conditions
                    delete_counter = 0
                    all_properties = sbml_model.getModel()
                    for iSpec in range(0, all_properties.getNumSpecies()):
                        all_species = all_properties.getSpecies(iSpec)
                        if all_species.getBoundaryCondition() == True:
                            state_trajectory = state_trajectory.transpose()
                            if delete_counter == 0:
                                state_trajectory = np.delete(state_trajectory, iSpec, 0)
                            else:
                                state_trajectory = np.delete(state_trajectory, iSpec - delete_counter, 0)
                            state_trajectory = state_trajectory.transpose()
                            delete_counter = delete_counter + 1

                    # Adjustment for the 'Froehlich2018' model
                    if iModel == 'Froehlich2018':
                        state_trajectory = np.delete(state_trajectory, np.s_[1177:1178], axis=1)

                    # Convert ndarray 'state-trajectory' to data frame + save it and modified COPASI file
                    df_state_trajectory = pd.DataFrame(columns=column_names, data=state_trajectory)
                    df_state_trajectory.to_csv(
                        f"{save_path}/AMICI_{iModel}_{MultistepMethod}_{save_atol}_{save_rtol}.tsv",
                        sep='\t', index=False)
                    tsv_file.to_csv(
                        f"{save_path}/COPASI_{iModel}_{MultistepMethod}_{save_atol}_{save_rtol}.tsv",
                        sep='\t', index=False)

                    # to know where one is
                    print('Model ' + iModel + ' successfully completed!')


# call function with no models to delete
compStaTraj_BioModels()
