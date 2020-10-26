# script 1 to compare state trajectories from JWS with trajectories of the AMICI simulation
# => creates two important .tsv files

# Attention:    boundary conditions are not being simulated by JWS!

from execute_loadModels import *
from JWS_changeValues import *
import amici.plotting
import numpy as np
import libsbml
import libsedml
import pandas as pd
import os
import urllib.request
import requests
import json
import itertools



def compStaTraj(delete_counter):
    # create new folder for all json files
    if not os.path.exists('../../Benchmarking_of_numerical_ODE_integration_methods/json_files'):
        os.makedirs('../../Benchmarking_of_numerical_ODE_integration_methods/json_files')

    # set settings for simulation
    for solAlg in [1, 2]:
        nonlinSol = 2
        linSol = 9
        if solAlg == 1:
            MultistepMethod = 'Adams'
            Tolerance_combination = [[1e-3,1e-3], [1e-6,1e-3], [1e-6,1e-6], [1e-12,1e-12], [1e-16,1e-8]]
        elif solAlg == 2:
            MultistepMethod = 'BDF'
            Tolerance_combination = [[1e-3,1e-3], [1e-6,1e-3], [1e-6,1e-6], [1e-12,1e-12], [1e-16,1e-8], [1e-14,1e-14], [1e-16,1e-16]]

        for iTolerance in Tolerance_combination:
            # split atol and rtol for naming purposes
            atol_exp = str(iTolerance[0])
            rtol_exp = str(iTolerance[1])
            if len(atol_exp) != 2:
                atol_exp = '0' + atol_exp
            if len(rtol_exp) != 2:
                rtol_exp = '0' + rtol_exp

            # get name of jws reference
            url = "https://jjj.bio.vu.nl/rest/models/?format=json"
            view_source = requests.get(url)
            json_string = view_source.text
            json_dictionary = json.loads(json_string)

            # get all models
            list_directory_amici = sorted(os.listdir('../../Benchmarking_of_numerical_ODE_integration_methods/'
                                                     'sbml2amici/amici_models_newest_version_0.10.19'))
            if delete_counter != 0:
                del list_directory_amici[0:delete_counter]

            for iMod in range(0, len(list_directory_amici)):

                iModel = list_directory_amici[iMod]
                list_files = sorted(os.listdir('../../Benchmarking_of_numerical_ODE_integration_methods/'
                                               'sedml_models/' + iModel + '/sbml_models'))

                for iFile in list_files:
                    # iFile without .sbml extension
                    iFile, extension = iFile.split('.', 1)

                    # important paths
                    json_save_path = '../../Benchmarking_of_numerical_ODE_integration_methods/json_files/' + \
                                     f'json_files_{MultistepMethod}_{atol_exp}_{rtol_exp}' + '/' + iModel + '/' + iFile
                    sedml_path = '../../Benchmarking_of_numerical_ODE_integration_methods/sedml_models/' + \
                                 iModel + '/' + iModel +'.sedml'
                    sbml_path = '../../Benchmarking_of_numerical_ODE_integration_methods/sedml_models/' + \
                                iModel + '/sbml_models/' + iFile + '.sbml'
                    BioModels_path = '../../Benchmarking_of_numerical_ODE_integration_methods/BioModelsDatabase_models'


                    if os.path.exists(BioModels_path + '/' + iModel):
                        print('Model is not part of JWS-database!')
                    else:
                        # Open SBML file
                        sbml_model = libsbml.readSBML(sbml_path)

                        # get right model reference from sbml model
                        parse_name_model = sbml_model.getModel().getId()
                        for iCount in range(0, len(json_dictionary)):
                            parse_name_jws = json_dictionary[iCount]['slug']
                            if parse_name_model == parse_name_jws:
                                model_reference = json_dictionary[iCount]['slug']
                                break
                        # elements in json_dictionary are only lower case --- the sbml model has upper case models
                        try:
                            model_reference
                        except:
                            wrong_model_name = ["".join(x) for _, x in itertools.groupby(parse_name_model,
                                                                                         key=str.isdigit)]
                            if wrong_model_name[0].islower() == False:
                                correct_model_letters = wrong_model_name[0].lower()
                                correct_model_name = correct_model_letters + wrong_model_name[1]
                                for iCount in range(0, len(json_dictionary)):
                                    parse_name_jws = json_dictionary[iCount]['slug']
                                    if correct_model_name == parse_name_jws:
                                        model_reference = json_dictionary[iCount]['slug']
                                        break
                        # check if 'all_settings' works
                        try:
                            # Get whole model
                            model = all_settings(iModel,iFile,1)

                            # create folder
                            if not os.path.exists(json_save_path):
                                os.makedirs(json_save_path)
                        except:
                            print('Model ' + iModel + ' extension is missing!')
                            continue


                        ######### jws simulation
                        # Get time data with num_time_points == 100
                        t_data = model.getTimepoints()
                        sim_start_time = t_data[0]
                        sim_end_time = t_data[len(t_data) - 1]
                        sim_num_time_points = 101
                        model.setTimepoints(np.linspace(sim_start_time, sim_end_time, sim_num_time_points))

                        # Open sedml file
                        sedml_model = libsedml.readSedML(sedml_path)

                        # import all changes from SEDML
                        list_of_strings = JWS_changeValues(iFile, sedml_model)

                        # Get Url with all changes
                        # <species 1>=<amount>
                        # <parameter 1>=<value>, compartment == parameter (in this case)
                        url = 'https://jjj.bio.vu.nl/rest/models/' + model_reference + '/time_evolution?time_end=' + \
                              str(sim_end_time) + ';species=all;'

                        for iStr in list_of_strings:
                            url = url + iStr

                        #### Save .json file
                        urllib.request.urlretrieve(url, json_save_path + '/' + iFile + '_JWS_simulation.json')

                        #### write as .csv file
                        json_2_csv = pd.read_json(json_save_path + '/' + iFile + '_JWS_simulation.json')
                        json_2_csv.to_csv(json_save_path + '/' + iFile + '_JWS_simulation.csv', sep='\t', index=False)

                        # open new .csv file
                        tsv_file = pd.read_csv(json_save_path + '/' + iFile + '_JWS_simulation.csv', sep='\t')

                        # columns names of .tsv file
                        column_names = list(tsv_file.columns)
                        column_names.remove('time')
                        del tsv_file['time']

                        ########## model simulation
                        # Create solver instance
                        solver = model.getSolver()

                        # set all settings
                        solver.setAbsoluteTolerance(iTolerance[0])
                        solver.setRelativeTolerance(iTolerance[1])
                        solver.setLinearSolver(linSol)
                        solver.setNonLinearSolver(nonlinSol)
                        solver.setLinearMultistepMethod(solAlg)

                        # set stability flag for Adams-Moulton
                        if solAlg == 1:
                            solver.setStabilityLimitFlag(False)

                        # Simulate model
                        sim_data = amici.runAmiciSimulation(model, solver)

                        # print some values
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

                        # Convert ndarray 'state-trajectory' to data frame and save it
                        try:
                            df_state_trajectory = pd.DataFrame(columns=column_names, data=state_trajectory)
                        except:
                            print('Try again for model ' + list_directory_amici[iMod] + '_' + iFile)
                            compStaTraj(iMod)
                        df_state_trajectory.to_csv(json_save_path + '/' + iFile + '_model_simulation.csv', sep='\t')

# call function, starting with no models to delete
compStaTraj(0)