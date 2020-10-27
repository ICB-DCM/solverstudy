# simulate all models with defined settings

from execute_loadModels import *
import amici.plotting
import libsbml
import time
import statistics
import pandas as pd

from C import DIR_DATA_WHOLESTUDY, DIR_DATA_TOLERANCES, DIR_MODELS_AMICI_FINAL


def simulate(atol, rtol, linSol, iter, solAlg, maxStep, study_indicator):

    # Create new folder structure for study
    if study_indicator == 1:
        tolerance_path = DIR_DATA_WHOLESTUDY
    elif study_indicator == 2:
        tolerance_path = DIR_DATA_TOLERANCES
    if not os.path.exists(tolerance_path):
        os.makedirs(tolerance_path)

    # save name
    s_atol = str(atol).split('-')[1]
    s_rtol = str(rtol).split('-')[1]
    s_linSol = str(linSol)
    s_iter = str(iter)
    s_solAlg = str(solAlg)

    # create .tsv file
    tsv_table = pd.DataFrame(
        columns=['id', 't_intern_ms', 't_extern_ms', 'state_variables',
                 'reactions', 'parameters', 'status', 'error_message'])

    # set row counter for .tsv file
    counter = 0

    # set number of repetitions for simulation
    sim_rep = 40

    # insert specific model properties as strings, e.g.:
    base_path_sedml = DIR_MODELS_SEDML
    base_path_amici = DIR_MODELS_AMICI_FINAL

    # list only specific models ---- should only simulate those models where
    #  sbml2amici worked!
    for iModel in sorted(os.listdir(base_path_amici)):

        # TODO Y refactor, this is trivial
        if os.path.exists(os.path.join(base_path_amici, iModel)):
            list_files = sorted(
                os.listdir(os.path.join(base_path_amici, iModel)))

            for iFile in list_files:
                # Append additional row in .tsv file
                tsv_table = tsv_table.append({}, ignore_index=True)

                # save id in .tsv
                tsv_table.loc[counter].id = \
                    '{' + iModel + '}' + '_' + '{' + iFile + '}'
                tsv_table.loc[counter].setting = \
                    s_solAlg + '_' + s_atol + '_' + s_rtol

                try:
                    # read in SBML file for reactions since AMICI has no
                    #  functions to count all reactions
                    file = libsbml.readSBML(os.path.join(
                        base_path_sedml, iModel, 'sbml_models',
                        iFile + '.sbml'))
                    all_properties = file.getModel()
                    num_reactions = all_properties.getNumReactions()
                    tsv_table.loc[counter].reactions = num_reactions

                    # call function from 'execute_loadModels.py'
                    model = all_settings(iModel, iFile)

                    # save state_variables, reactions and parameters
                    num_states = len(model.getStateNames())
                    num_par = len(model.getParameters())
                    tsv_table.loc[counter].state_variables = num_states
                    tsv_table.loc[counter].parameters = num_par

                    # Create solver instance
                    solver = model.getSolver()

                    # set all settings
                    solver.setAbsoluteTolerance(atol)
                    solver.setRelativeTolerance(rtol)
                    solver.setLinearSolver(linSol)
                    solver.setNonlinearSolverIteration(iter)
                    solver.setLinearMultistepMethod(solAlg)
                    solver.setMaxSteps(maxStep)

                    # clock simulation time while running the simulation
                    #  using pre-defined settings
                    built_in_time = []
                    external_time = []
                    ind_time = []
                    end_time = []

                    try:
                        # set stability limit detection
                        solver.setStabilityLimitFlag(False)
                        for iSim in range(0, sim_rep):
                            start_time = time.time()

                            sim_data = amici.runAmiciSimulation(model, solver)

                            end_time.append(time.time())
                            ind_time.append(sim_data['cpu_time'])

                            external_time.append(1000*(end_time[iSim] - start_time))
                            if iSim == 0:
                                built_in_time.append(ind_time[iSim])
                            else:
                                built_in_time.append(ind_time[iSim] - ind_time[iSim - 1])

                        # take status + median of time_vector
                        sim_status = sim_data['status']
                        internal = statistics.median(built_in_time)
                        external = statistics.median(external_time)

                        # save status + time data in .tsv
                        tsv_table.loc[counter].status = sim_status
                        tsv_table.loc[counter].t_intern_ms = internal
                        tsv_table.loc[counter].t_extern_ms = external

                        # raise counter
                        counter = counter + 1

                    except Exception as e:
                        error_info_3 = str(e)
                        tsv_table.loc[counter].t_intern_ms = 'nan'
                        tsv_table.loc[counter].t_extern_ms = 'nan'
                        tsv_table.loc[counter].error_message = \
                            'Error_3: ' + error_info_3

                        # raise counter
                        counter = counter + 1

                except Exception as e:
                    error_info_2 = str(e)
                    tsv_table.loc[counter].t_intern_ms = 'nan'
                    tsv_table.loc[counter].t_extern_ms = 'nan'
                    tsv_table.loc[counter].error_message = \
                        'Error_2: ' + error_info_2

                    # raise counter
                    counter = counter + 1

    # save data frame as .tsv file
    tsv_table.to_csv(path_or_buf=os.path.join(
        tolerance_path,
        s_solAlg + '_' + s_iter + '_' + s_linSol + '_' + s_atol + '_' +
        s_rtol + '.tsv'),
        sep='\t', index=False)
