import amici
import numpy as np
from time import time as toc
import pandas as pd
import os

from loadModels import get_submodel_list_copasi, get_submodel_copasi
from C import simconfig, DIR_MODELS, DIR_COPASI_BIN


def simulation_wrapper(
        simulation_mode: str,
        settings: dict,
        model_name: str = None,
        submodel_path: str = None,
):
    """
    This script wraps around the simulation with Copasi,
    applies the settings for the ODE solver,
    and returns a list of result, which depend on simulation_mode:

    """
    # import the model_summary table to add information about the models to load
    model_info = pd.read_csv(os.path.join(DIR_MODELS, 'model_summary.tsv'),
                             sep='\t')

    # get the list of sbml models which belong to this benchmark model
    if submodel_path is None:
        copasi_file_list = get_submodel_list_copasi(model_name, model_info)
    else:
        copasi_file = get_submodel_copasi(submodel_path, model_info)
        copasi_file_list = [copasi_file]

    # get the path with the Copasi binaries
    CopasiSE = os.path.join(DIR_COPASI_BIN, 'CopasiSE')

    # collect cpu times
    average_cpu_times_intern = []
    average_cpu_times_extern = []
    # collect trajectories
    trajectories = []
    # collect failures
    failures = []

    # loop over models (=modules) to be simulated:
    for i_model, model in enumerate(copasi_file_list):
        if simulation_mode == simconfig.CPUTIME:
            # we want to repeatedly simulate the model
            if os.getenv('SOLVERSTUDY_DIR_BASE', None) == 'TEST':
                n_repetitions = 3
            else:
                n_repetitions = 25
        else:
            n_repetitions = 1

        # collect cpu times
        cpu_times_intern = []
        cpu_times_extern = []

        # adapt the cps-file for Copasi simulation according to the solver
        # settings (create a temporary file for this).
        # Also generate a name for the temporary Copasi report file
        tmp_cps_file, tmp_report_base = \
            _apply_solver_settings(model, settings)

        for i_rep in range(n_repetitions):
            # adapt the name of the temporary report file
            tmp_report_file = f'{tmp_report_base}_{i_rep}.tsv'

            # simulate and get simulation time, remove temporary simulation file
            start = toc()
            os.system(f'{CopasiSE} --report-file {tmp_report_file} {tmp_cps_file}')
            time_extern = (toc() - start)

            # Copasi writes its results to a report file.
            # We need to post process it first and then remove it
            rdata = _post_process_report_file(tmp_report_file, simulation_mode)

            # if simulation was not successful
            if rdata['status'] != 0:
                cpu_times_extern = [float('nan')] * n_repetitions
                cpu_times_intern = [float('nan')] * n_repetitions
                break

            # report in seconds
            cpu_times_extern.append(time_extern)
            cpu_times_intern.append(rdata['cpu_time'])

        # We need to remoe the temporary cps-file
        os.system(f'rm {tmp_cps_file}')

        # let's just always collect the stuff which is cheap anyway
        average_cpu_times_intern.append(np.array(cpu_times_intern))
        average_cpu_times_extern.append(np.array(cpu_times_extern))
        failures.append(rdata['status'] != 0)

        # Trajectories are more memory intensive. Only collect if needed
        if simulation_mode == simconfig.TRAJECTORY:
            trajectories.append(rdata['x'])

    # postprocess depending on purpose and return a dict
    if simulation_mode == simconfig.TRAJECTORY:
        return trajectories
    else:
        return _post_process_cputime(np.array(average_cpu_times_intern),
                                     np.array(average_cpu_times_extern),
                                     np.array(failures),
                                     n_repetitions)


def _apply_solver_settings(model, settings):
    # generate a name for the temporary copasi file
    tmp_cps_file = (model.split('/')[-1]).split('.')[0] + '__for_sim__'
    tmp_report_base = (model.split('/')[-1]).split('.')[0] + '__report__'
    suffix = f'atol_{settings["atol"]}__rtol{settings["rtol"]}__deleteme'
    tmp_cps_file += suffix + '.cps'
    tmp_report_base += suffix

    # open file to read in and to write out
    f_in = open(model, 'r')
    f_out = open(tmp_cps_file, 'w')

    for line in f_in:
        if '<Parameter name="Relative Tolerance" type="unsigned' in line:
            # adapt relative integration error tolerance
            f_out.write('<Parameter name="Relative Tolerance" '
                        'type="unsignedFloat" value="1.0e-06"/>\n')

        elif '<Parameter name="Absolute Tolerance" type="unsigned' in line:
            # adapt absolute integration error tolerance
            f_out.write('<Parameter name="Absolute Tolerance" '
                        'type="unsignedFloat" value="1.0e-06"/>\n')

        elif '<Parameter name="Max Internal Steps" type="unsigned' in line:
            # adpapt number of integration steps
            f_out.write(line.replace('value="100000"', 'value="10000"'))
        else:
            f_out.write(line)

    # close files
    f_out.close()
    f_in.close()

    return tmp_cps_file, tmp_report_base


def _post_process_report_file(tmp_report_file,
                              simulation_mode):
    """
    We want to postprocess the tsv file created by Copasi

    :tmp_report_file:
        string with path to report file created by Copasi

    :simulation_mode:
        ndarray of size n_models x n_repetitions.
        to be averaged oer the models
    """

    # Does the report file exist? If so, assume simulation to be successful
    if os.path.exists(tmp_report_file):
        status = 0
    else:
        return {'status': -1, 'x': None}

    # if the file exists, read it
    results_df = pd.read_csv(tmp_report_file, sep='\t')
    cpu_time = results_df['(Timer)CPU Time'].values[-1]
    if simulation_mode == simconfig.TRAJECTORY:
        # We want trajectories. Hence, we keep them
        trajectories = results_df.drop(['Time', '(Timer)CPU Time',
                                        '(Timer)Wall Clock Time'], axis=1)
    else:
        trajectories = None

    # remove the temporary file
    os.remove(tmp_report_file)
    # return a dict
    return {'status': status, 'x': trajectories, 'cpu_time': cpu_time}


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
