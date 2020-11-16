# execute simulation script with ALL solver setting combinations

######################################################################################
# very important: linSol, nonLinSolIter, solAlg must be their corresponding integers #
#                                                                                    #
# linSol:           Dense == 1  GMRES == 6  BiCGStab == 7   SPTFQMR == 8    KLU == 9 #
# nonLinSolIter:    Functional == 1     Newton-type == 2                             #
# solAlg:           Adams == 1      BDF == 2                                         #
#                                                                                    #
######################################################################################

import logging
import os
import pandas as pd
import numpy as np


from C import DIR_MODELS_AMICI_FINAL, DIR_MODELS_COPASI_FINAL, \
              DIR_RESULTS_ALGORITHMS, \
              DIR_BASE, DIR_MODELS, SIMCONFIG, DIR_COPASI_BIN

from simulation_wrapper_amici import simulation_wrapper as simulate_with_amici
from simulation_wrapper_copasi import simulation_wrapper as simulate_with_copasi

# create logger object
logger = logging.getLogger()

# initialize the log settings
logging.basicConfig(
    filename=os.path.join(DIR_BASE, 'trajectoryComparison.log'),
    level=logging.DEBUG)


def run_study_amici(model_info):
    # the settings we want to simulate with AMICI
    settings_amici = [
        {
            'id': f'atol_{atol}__rtol_{rtol}__linSol_{ls}__nonlinSol_{nls}__solAlg_{algo}',
            'atol': float(atol), 'rtol': float(rtol),
            'linSol': ls, 'nonlinSol': nls, 'solAlg': algo}
        for (atol, rtol) in (('1e-8', '1e-6'), ('1e-6', '1e-8'),
                             ('1e-12', '1e-10'), ('1e-10', '1e-12'),
                             ('1e-16', '1e-8'), ('1e-8', '1e-16'),
                             ('1e-14', '1e-14'))
        for ls in (1, 6, 7, 8, 9)
        for nls in (1, 2)
        for algo in (1, 2)
    ]

    for setting in settings_amici:
        # collect results as a list
        results = []

        for model_name in sorted(os.listdir(DIR_MODELS_AMICI_FINAL)):
            # Get information about the current model
            model_rows = model_info[model_info['short_id'] == model_name]
            idx = model_rows.index.values[0]
            models_to_average = sum([acc for acc in list(model_rows['accepted'])])

            # run the simulation
            result = simulate_with_amici(simulation_mode=SIMCONFIG.CPUTIME,
                                         settings=setting, model_name=model_name)

            # save results in a dict
            model_result = {'model_name': model_name,
                            'median_intern': np.median(result['cpu_times_intern']),
                            'median_extern': np.median(result['cpu_times_extern']),
                            'failure': result['failure'],
                            'n_species': model_rows.loc[idx, 'n_species'],
                            'n_reactions': model_rows.loc[idx, 'n_reactions'],
                            'n_submodels': models_to_average}
            for i_run, runtime in enumerate(result['cpu_times_intern']):
                model_result[f'run_{i_run}'] = runtime
            # save in the DataFrame to be
            results.append(model_result)

        results_df = pd.DataFrame(results)
        results_file = os.path.join(save_path, setting['id'] + '.tsv')
        results_df.to_csv(results_file, sep='\t', index=False)


def run_study_copasi(model_info):
    # the settings we want to simulate with Copasi
    settings_copasi = [
        {
            'id': f'atol_{atol}__rtol_{rtol}__linSol_1__nonlinSol_2__solAlg_3',
            'atol': float(atol), 'rtol': float(rtol),
            'linSol': 1, 'nonlinSol': 2, 'solAlg': 3}
        for (atol, rtol) in (('1e-8', '1e-6'), ('1e-6', '1e-8'),
                             ('1e-12', '1e-10'), ('1e-10', '1e-12'),
                             ('1e-16', '1e-8'), ('1e-8', '1e-16'),
                             ('1e-14', '1e-14'))
    ]

    for setting in settings_copasi:
        # collect results as a list
        results = []

        for model_name in sorted(os.listdir(DIR_MODELS_COPASI_FINAL)):
            # Get information about the current model
            model_rows = model_info[model_info['short_id'] == model_name]
            idx = model_rows.index.values[0]
            models_to_average = sum([acc for acc in list(model_rows['accepted'])])

            # run the simulation
            result = simulate_with_copasi(simulation_mode=SIMCONFIG.CPUTIME,
                                          settings=setting, model_name=model_name)

            # save results in a dict
            model_result = {'model_name': model_name,
                            'median_intern': np.median(result['cpu_times_intern']),
                            'median_extern': np.median(result['cpu_times_extern']),
                            'failure': result['failure'],
                            'n_species': model_rows.loc[idx, 'n_species'],
                            'n_reactions': model_rows.loc[idx, 'n_reactions'],
                            'n_submodels': models_to_average}
            for i_run, runtime in enumerate(result['cpu_times_intern']):
                model_result[f'run_{i_run}'] = runtime
            # save in the DataFrame to be
            results.append(model_result)

        results_df = pd.DataFrame(results)
        results_file = os.path.join(save_path, setting['id'] + '.tsv')
        results_df.to_csv(results_file, sep='\t', index=False)


# Create new folder structure for study
save_path = DIR_RESULTS_ALGORITHMS
if not os.path.exists(save_path):
    os.makedirs(save_path)

# load the table with model information
model_info = pd.read_csv(os.path.join(DIR_MODELS, 'model_summary.tsv'),
                         sep='\t')

run_study_amici(model_info)

if os.system(os.path.join(DIR_COPASI_BIN, 'CopasiSE') + ' --help') != 0:
    print("Copasi seems to be not installed or the path to the Copasi binaries "
          "is not properly set in Python_Scripts/C.py. Stopping.")

else:
    run_study_copasi(model_info)
