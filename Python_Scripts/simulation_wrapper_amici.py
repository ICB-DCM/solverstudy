"""
This script executes simulations for the benchmark study and wraps around
simulations with AMICI. It accounts for whether trajectories should be compared
or CPU times taken (then it repeats simulations and reports a list of CPU
times). It can be called for one submodel (one SBML model, if its path is
provided, e.g., for trajectory comparison) or for a whole benchmark model
(possibly consisting of multiple submodels, i.e., SBML files).
In the latter case, the script automatically collects all submodels and
CPU times are averaged over the submodels.
"""

import amici
import numpy as np
from time import time as toc
import pandas as pd
import os

from loadModels import get_submodel_list, get_submodel
from C import SIMCONFIG, DIR_MODELS, repetitions_for_cpu_time_study

def simulation_wrapper(
        simulation_mode: str,
        settings: dict,
        model_name: str = None,
        submodel_path: str = None,
):
    """
    This script wraps around the simulation with AMICI,
    applies the settings for the ODE solver,
    and returns a list of result, which depend on simulation_mode:

    :param:
        - simulation_mode:
            whether we want to get trajectories out or cpu times

        - settings:
            a dict with settigs for the ODE solver

        - model_name:
            string with the id of the benchmark model (e.g. parthak2013a),
            which may contain different submodels

        - submodel_path:
            string with path to the amici model module (submodel) which belongs
            to *one* SBML file, path being relative to DIR_MODELS
    """

    # import the model_summary table to add information about the models to load
    model_info = pd.read_csv(os.path.join(DIR_MODELS, 'model_summary.tsv'),
                             sep='\t')

    # get the list of sbml models which belong to this benchmark model
    if submodel_path is None:
        amici_model_list, sbml_model_list = get_submodel_list(model_name,
                                                              model_info)
    else:
        amici_model, sbml_model = get_submodel(submodel_path, model_info)
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
        if simulation_mode == SIMCONFIG.CPUTIME:
            # we want to repeatedly simulate the model
            n_repetitions = repetitions_for_cpu_time_study
        else:
            n_repetitions = 1

        # collect cpu times
        cpu_times_intern = []
        cpu_times_extern = []

        for _ in range(n_repetitions):
            # get the adapted solver object
            solver = _apply_solver_settings(model, settings)

            # simulate and get simulation time
            start = toc()
            rdata = amici.runAmiciSimulation(model, solver)
            time_extern = (toc() - start) # time in seconds

            # if simulation was not successful
            if rdata['status'] != 0:
                cpu_times_extern.append([float('nan')] * n_repetitions)
                cpu_times_intern.append([float('nan')] * n_repetitions)
                break

            # report in seconds
            cpu_times_extern.append(time_extern)
            # convert time in milliseconds to time in seconds
            cpu_times_intern.append(rdata['cpu_time'] / 1000.)

        # let's just always collect the stuff which is cheap anyway
        average_cpu_times_intern.append(np.array(cpu_times_intern))
        average_cpu_times_extern.append(np.array(cpu_times_extern))
        failures.append(rdata['status'] != 0)

        # Trajectories are more memory intensive. Only collect if needed
        if simulation_mode == SIMCONFIG.TRAJECTORY:
            trajectories.append(rdata['x'])

    # postprocess depending on purpose and return a dict
    if simulation_mode == SIMCONFIG.TRAJECTORY:
        return _post_process_trajectories(trajectories,
                                          failures,
                                          amici_model_list,
                                          sbml_model_list)
    else:
        return _post_process_cputime(np.array(average_cpu_times_intern),
                                     np.array(average_cpu_times_extern),
                                     np.array(failures),
                                     n_repetitions)


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
                          failures: np.ndarray,
                          n_repetitions):
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
            'cpu_times_intern': np.full((1, n_repetitions), np.nan),
            'cpu_times_extern': np.full((1, n_repetitions), np.nan),
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
            # unmark prohibited symbols:
            if state[:6] == 'amici_':
                state = state[6:]
            species = sbml_model.getSpecies(state)
            if species.constant == False and species.getBoundaryCondition() == False:
                species_ids.append(state)
                species_keep.append(i_state)

        pruned_trajectories.append(
            pd.DataFrame(data=trajectory[:, species_keep],
                         columns=species_ids))

    return pruned_trajectories
