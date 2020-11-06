import amici
import numpy as np
from time import time as toc
import pandas as pd
import os

from loadModels import get_submodel_list, get_submodel
from C import simconfig, DIR_MODELS

def simulation_wrapper(
        simulation_mode: str,
        settings: dict,
        model_name: str = None,
        submodel_path: str = None,
):
    """This script wraps around the simulation with AMICI,
    applies the settings for the ODE solver,
    and returns a list of result, which depend on simulation_mode:

    """
    # get the list of sbml models which belong to this benchmark model
    if submodel_path is None:
        amici_model_list, sbml_model_list = get_submodel_list(model_name)
    else:
        amici_model, sbml_model = get_submodel(submodel_path)
        amici_model_list = [amici_model]
        sbml_model_list = [sbml_model]

    # collect cpu times
    average_cpu_times_intern = []
    average_cpu_times_extern = []
    # collect trajectories
    trajectories = []
    # collect failures
    failures = []

    # loop over models (=modules) to be simulated:
    for i_model, model in enumerate(amici_model_list):
        # get the adapted solver object
        solver = _apply_solver_settings(model, settings)

        if simulation_mode == simconfig.CPUTIME:
            # we want to repeatedly simulate the model
            n_repetitions = 40
        else:
            n_repetitions = 1

        # collect cpu times
        cpu_times_intern = []
        cpu_times_extern = []

        for _ in range(n_repetitions):
            # simulate and get simulation time
            start = toc()
            rdata = amici.runAmiciSimulation(model, solver)
            time_extern = (toc() - start) / 1000.

            # if simulation was not successful
            if rdata['status'] != 0:
                cpu_times_extern.append(float('nan'))
                cpu_times_intern.append(float('nan'))
                break

            # report in seconds
            cpu_times_extern.append(time_extern)
            cpu_times_intern.append(rdata['cpu_time'])

        # let's just always collect the stuff which is cheap anyway
        average_cpu_times_intern.append(np.array(cpu_times_intern))
        average_cpu_times_extern.append(np.array(cpu_times_extern))
        failures.append(rdata['status'] != 0)

        # Trajectories are more memory intensive. Only collect if needed
        if simulation_mode == simconfig.TRAJECTORY:
            trajectories.append(rdata['x'])

    # postprocess depending on purpose and return a dict
    if simulation_mode == simconfig.TRAJECTORY:
        return _post_process_trajectories(trajectories,
                                          failures,
                                          amici_model_list,
                                          sbml_model_list)
    else:
        return _post_process_cputime(np.array(average_cpu_times_intern),
                                     np.array(average_cpu_times_extern),
                                     np.array(failures),)


def _apply_solver_settings(model, settings):
    # get the solver object
    solver = model.getSolver()

    # apply settings
    solver.setAbsoluteTolerance(settings['atol'])
    solver.setRelativeTolerance(settings['rtol'])
    solver.setLinearSolver(settings['linSol'])
    solver.setNonlinearSolverIteration(settings['nonlinSol'])
    solver.setLinearMultistepMethod(settings['solAlg'])

    # set stability flag for Adams-Moulton
    if settings['solAlg'] == 1:
        solver.setStabilityLimitFlag(False)

    return solver


def _post_process_cputime(average_cpu_times_intern: np.ndarray,
                          average_cpu_times_extern: np.ndarray,
                          failures: np.ndarray,):
    """We want to average over the different sbml models
    which belong to the same benchmark model

    :average_cpu_times_intern:
        ndarray of size n_models x n_repetitions.
        to be averaged oer the models

    :average_cpu_times_intern:
        ndarray of size n_models x n_repetitions.
        to be averaged oer the models

    :failures:
        ndarray of size n_models. Must be False for all entries
    """
    # If we have a model simulation failure, we record no cpu time
    if np.any(failures):
        return {
            'cpu_times_intern': None,
            'cpu_times_extern': None,
            'failure': True,
        }

    average_cpu_times_intern = np.mean(average_cpu_times_intern, axis=0)
    average_cpu_times_extern = np.mean(average_cpu_times_extern, axis=0)
    return {
        'cpu_times_intern': average_cpu_times_intern.flatten(),
        'cpu_times_extern': average_cpu_times_extern.flatten(),
        'failure': False,
    }

def _post_process_trajectories(trajectories,
                               failures,
                               amici_model_list,
                               sbml_model_list):
    """This script prunes out the constant species from the trajectory array
    and returns a dataframe with the species ids as column names"""
    pruned_trajectories = []

    for i_model, sbml_model in enumerate(sbml_model_list):
        # did the simulation fail? If so, return None
        failure = failures[i_model]
        if failure:
            pruned_trajectories.append(None)
            continue

        trajectory = trajectories[i_model]
        amici_model = amici_model_list[i_model]
        species_ids = []
        species_keep = []
        for i_state, state in enumerate(amici_model.getStateIds()):
            species = sbml_model.getSpecies(state)
            if species.constant == False and species.getBoundaryCondition() == False:
                species_ids.append(state)
                species_keep.append(i_state)

        pruned_trajectories.append(
            pd.DataFrame(data=trajectory[:, species_keep],
                         columns=species_ids))

    return pruned_trajectories
