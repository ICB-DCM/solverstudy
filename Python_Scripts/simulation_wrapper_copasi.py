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
        copasi_file_list, sbml_model_list = \
            get_submodel_list_copasi(model_name, model_info)
    else:
        copasi_file, sbml_model = get_submodel_copasi(submodel_path, model_info)
        copasi_file_list = [copasi_file]
        sbml_model_list = [sbml_model]

    # get the path with the Copasi binaries
    CopasiSE = os.path.join(DIR_COPASI_BIN, 'CopasiSE')

    # collect cpu times
    average_cpu_times_intern = []
    average_cpu_times_extern = []
    # collect trajectories
    trajectories = []
    # collect failures
    failures = []

    if simulation_mode == simconfig.CPUTIME:
        # we want to repeatedly simulate the model
        if os.getenv('SOLVERSTUDY_DIR_BASE', None) == 'TEST':
            n_repetitions = 3
        else:
            n_repetitions = 25
    else:
        n_repetitions = 1

    # loop over models (=modules) to be simulated:
    for i_model, model in enumerate(copasi_file_list):
        # get the corresponding SBML model
        sbml_model = sbml_model_list[i_model]

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
            rdata = _post_process_report_file(tmp_report_file, simulation_mode,
                                              sbml_model)

            # if simulation was not successful
            if rdata['status'] != 0:
                cpu_times_extern = [float('nan')] * n_repetitions
                cpu_times_intern = [float('nan')] * n_repetitions
                break

            # report in seconds
            cpu_times_extern.append(time_extern)
            cpu_times_intern.append(rdata['cpu_time'])

        # We need to remoe the temporary cps-file
        os.remove(tmp_cps_file)

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
                              simulation_mode,
                              sbml_model):
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
    cpu_time = float(results_df['(Timer)CPU Time'].values[-1])
    if simulation_mode == simconfig.TRAJECTORY:
        # We want trajectories. Hence, we keep them
        for rm_key in ('time', 'Time', '(Timer)CPU Time',
                       '(Timer)Wall Clock Time'):
            if  rm_key in results_df.keys():
                results_df.drop(rm_key, axis=1, inplace=True)

        # We also want to drop columns with constant species
        # Copasi marks species concentrations with [], e.g., [RAS]
        # We need to remove the "[]" to have species IDs as column names
        new_keys = []
        species_list = [spec.id for spec in sbml_model.getListOfSpecies()]
        for i_key in list(results_df.keys()):
            quantity = i_key[1:-1]
            if quantity not in species_list:
                results_df.drop(i_key, axis=1, inplace=True)
                continue

            species = sbml_model.getSpecies(quantity)
            if species.constant == True or species.getBoundaryCondition() == True:
                results_df.drop(i_key, axis=1, inplace=True)
                continue

            new_keys.append(quantity)

        if new_keys:
            results_df.columns = new_keys
        else:
            return {'status': -1, 'x': None}

    else:
        results_df = None

    # remove the temporary file
    os.remove(tmp_report_file)
    # return a dict
    return {'status': status, 'x': results_df, 'cpu_time': cpu_time}


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
