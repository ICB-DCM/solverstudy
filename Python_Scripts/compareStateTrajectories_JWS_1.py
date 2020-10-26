# script 1 to compare state trajectories from JWS with trajectories of the AMICI simulation
# => creates two important .tsv files

# Attention:    boundary conditions are not being simulated by JWS!

# Note: libsedml must be imported before libsbml for whatever reason

import libsedml
import libsbml
import amici.plotting
import numpy as np
import pandas as pd
import os
import urllib.request
import requests
import json

from execute_loadModels import all_settings
from JWS_changeValues import JWS_changeValues

from C import (
    DIR_MODELS_SEDML, DIR_MODELS_BIOMODELS, DIR_MODELS_AMICI, DIR_MODELS_JSON,
    DIR_MODELS_REF_TRAJECTORIES)


def _maybe_download_jws_simulation(
        iModel, iFile, sedml_path, sbml_path, json_dictionary, sim_end_time):
    """Download the JWS simulation, unless already downloaded."""
    json_save_path = os.path.join(
        DIR_MODELS_REF_TRAJECTORIES, iModel, iFile)
    tsv_file = os.path.join(json_save_path, 'JWS_simulation.csv')
    if os.path.exists(tsv_file):
        print(f"JWS simulations for model {iModel} {iFile} already exist, "
              "skipping.")
        return tsv_file

    if not os.path.exists(json_save_path):
        os.makedirs(json_save_path)

    # open sedml file
    sedml_model: libsedml.SedDocument = libsedml.readSedML(sedml_path)
    # open sbml file
    sbml_model = libsbml.readSBML(sbml_path)

    sbml_slug = None
    for iCount in range(0, len(json_dictionary)):
        if sbml_model.getModel().getName() == json_dictionary[iCount]['name']:
            sbml_slug = json_dictionary[iCount]['slug']
            break
    if sbml_slug is None:
        raise ValueError(
            f"Extraction of SBML url for {iModel}_{iFile} failed.")

    # import all changes from SEDML
    list_of_strings = JWS_changeValues(iFile, sedml_model)

    # Get Url with all changes
    # <species 1>=<amount>
    # <parameter 1>=<value>, compartment == parameter (in this case)
    url = 'https://jjj.bio.vu.nl/rest/models/' + sbml_slug + \
          '/time_evolution?' \
          'time_end=' + str(sim_end_time) + ';species=all;'
    for iStr in list_of_strings:
        url = url + iStr

    #### Save .json file
    print(f"JWS simulation URL: {url}")
    json_file = os.path.join(json_save_path, 'JWS_simulation.json')
    # JWS sometimes just returns an error output, then just retry
    while True:
        print("Downloading")
        urllib.request.urlretrieve(url, json_file)
        with open(json_file, 'r') as f:
            if f.read() != '{"error_msg": "No result was returned."}':
                break

    #### write as .csv file
    json_2_csv = pd.read_json(json_file)
    tsv_file = os.path.join(json_save_path, 'JWS_simulation.csv')
    json_2_csv.to_csv(tsv_file, sep='\t', index=False)

    return tsv_file


def _com_sta_traj_for_model(
        iModel, iFile, MultistepMethod, linSol, iTolerance,
        atol_exp, rtol_exp, json_dictionary, solAlg):
    """Generate and save JWS and AMICI trajectories for the given model."""

    # Report the model currently worked on
    print(iModel, iFile, MultistepMethod, linSol, iTolerance)
    # iFile without .sbml extension
    iFile, extension = iFile.split('.', 1)

    # important paths
    json_save_path = os.path.join(
        DIR_MODELS_JSON,
        f'json_files_{MultistepMethod}_{atol_exp}_{rtol_exp}',
        iModel, iFile)
    sedml_path = os.path.join(
        DIR_MODELS_SEDML, iModel, iModel + '.sedml')
    sbml_path = os.path.join(
        DIR_MODELS_SEDML, iModel, 'sbml_models',
        iFile + '.sbml')
    BioModels_path = DIR_MODELS_BIOMODELS

    if os.path.exists(os.path.join(BioModels_path, iModel)):
        print("Model is not part of JWS-database")
    else:
        # check if 'all_settings' works
        # TODO Y this is not good. JWS download should not depend on AMICI!!!
        try:
            # Get whole model
            model = all_settings(iModel, iFile)

            # create folder
            if not os.path.exists(json_save_path):
                os.makedirs(json_save_path)
        except:
            print('Model ' + iModel + ' extension is missing!')
            return

        ######### jws simulation
        # Get time data with num_time_points == 100
        t_data = model.getTimepoints()
        sim_start_time = t_data[0]
        sim_end_time = t_data[len(t_data) - 1]
        sim_num_time_points = 101
        model.setTimepoints(
            np.linspace(sim_start_time, sim_end_time, sim_num_time_points))

        tsv_file = _maybe_download_jws_simulation(
            iModel, iFile, sedml_path, sbml_path, json_dictionary,
            sim_end_time)

        # open new .csv file
        df = pd.read_csv(tsv_file, sep='\t')

        # columns names of .tsv file
        column_names = list(df.columns)
        # TODO Y clean up
        column_names.remove('time')
        del df['time']

        ########## model simulation
        print("Simulating with AMICI")

        # Create solver instance
        solver = model.getSolver()

        # set all settings
        solver.setAbsoluteTolerance(iTolerance[0])
        solver.setRelativeTolerance(iTolerance[1])
        solver.setLinearSolver(linSol)
        solver.setLinearMultistepMethod(solAlg)

        # set stability flag for Adams-Moulton
        if solAlg == 1:
            solver.setStabilityLimitFlag(False)

        # Simulate model
        sim_data = amici.runAmiciSimulation(model, solver)

        # print some values
        # for key, value in sim_data.items():
        #       print('%12s: ' % key, value)

        # Get state trajectory
        state_trajectory = sim_data['x']

        # prune out constant species for trajectory comparison
        # open sbml file
        sbml_model = libsbml.readSBML(sbml_path)
        delete_ind = [
            iSpec for iSpec in range(sbml_model.getModel().getNumSpecies())
            if sbml_model.getModel().getSpecies(iSpec).getBoundaryCondition()
               is True]
        state_trajectory = np.delete(state_trajectory, delete_ind, 1)

        print(column_names, model.getObservableIds())

        # Convert ndarray 'state-trajectory' to data frame and save it
        df_state_trajectory = pd.DataFrame(columns=column_names,
                                           data=state_trajectory)
        df_state_trajectory.to_csv(os.path.join(
            json_save_path, iFile + '_model_simulation.csv'),
            sep='\t')


def compStaTraj():
    """Compute state trajectories with JWS and AMICI."""

    # get name of jws reference
    url = "https://jjj.bio.vu.nl/rest/models/?format=json"
    view_source = requests.get(url)
    json_string = view_source.text
    json_dictionary = json.loads(json_string)

    # set settings for simulation
    for solAlg in [1, 2]:
        linSol = 9
        if solAlg == 1:
            MultistepMethod = 'Adams'
            Tolerance_combination = [
                [1e-3,1e-3], [1e-6,1e-3], [1e-6,1e-6], [1e-12,1e-12],
                [1e-16,1e-8]]
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

            # get all models
            list_directory_amici = sorted(os.listdir(DIR_MODELS_AMICI))

            # iterate over the sedml models
            for iMod in range(0, len(list_directory_amici)):
                iModel = list_directory_amici[iMod]
                list_files = sorted(os.listdir(os.path.join(
                    DIR_MODELS_SEDML, iModel, 'sbml_models')))

                # iterate over the sbml models
                for iFile in list_files:
                    # compute trajectories for model
                    _com_sta_traj_for_model(
                        iModel, iFile, MultistepMethod, linSol, iTolerance,
                        atol_exp, rtol_exp, json_dictionary, solAlg)


# call function, starting with no models to delete
compStaTraj()
