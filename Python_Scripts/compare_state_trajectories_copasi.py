import numpy as np
import pandas as pd
import os
import logging


from C import (DIR_BASE, DIR_MODELS, DIR_MODELS_REGROUPED, SIMCONFIG)

from simulation_wrapper_copasi import simulation_wrapper

# important paths
models_base_path = DIR_MODELS
base_path = DIR_MODELS_REGROUPED

# create logger object
logger = logging.getLogger()

# initialize the log settings
logging.basicConfig(
    filename=os.path.join(DIR_BASE, 'trajectoryComparisonCopasi.log'),
    level=logging.DEBUG)

# load the table with model information
model_info = pd.read_csv(os.path.join(DIR_MODELS, 'model_summary.tsv'),
                         sep='\t')


def compare_trajectories_copasi():
    # set up a list with the numerical integration errors
    error_list = []
    max_trajectory_errors_copasi = []

    settings = [
        {
            'id': f'atol:{atol}_rtol:{rtol}_linSol:{ls}_nonlinSol:{nls}_solAlg:{algo}',
            'atol': float(atol), 'rtol': float(rtol),
            'linSol': ls, 'nonlinSol': nls, 'solAlg': algo}
        for (atol, rtol) in
        (('1e-3', '1e-3'), ('1e-6', '1e-3'), ('1e-6', '1e-6'),
         ('1e-8', '1e-6'), ('1e-6', '1e-8'), ('1e-12', '1e-10'),
         ('1e-10', '1e-12'), ('1e-16', '1e-8'), ('1e-8', '1e-16'),
         ('1e-14', '1e-14'))
        for ls in (1, 6, 7, 8, 9)
        for nls in (1, 2)
        for algo in (1, 2)
    ]

    # if we're only testing, we don't want to check all settings
    if os.getenv('SOLVERSTUDY_DIR_BASE', None) == 'TEST':
        settings = [
            {'id': f'atol:1e-12_rtol:1e-10_linSol:9_nonlinSol:2_solAlg:2',
            'atol': 1.e-12, 'rtol': 1.e-10,
            'linSol': 9, 'nonlinSol': 2, 'solAlg': 2}
        ]

    for i_submodel in model_info.index:
        # could the model be successfully imported?
        copasi_model_path = model_info.loc[i_submodel, 'copasi_path']
        if str(copasi_model_path) in ('', 'nan'):
            continue

        # load reference trajectories
        ref_path = model_info.loc[i_submodel, 'ref_trajectory_path']
        ref_traj = pd.read_csv(ref_path, sep='\t')

        # save error
        max_trajectory_error = {'copasi_path': copasi_model_path}
        for setting in settings:
            trajectories, = simulation_wrapper(
                simulation_mode=SIMCONFIG.TRAJECTORY,
                settings=setting,
                submodel_path=copasi_model_path)

            if trajectories is None:
                # integration did not work
                max_trajectory_error[setting['id']] = float('inf')
            else:
                # integration worked. Compute a combination of abs and rel
                #  error
                max_trajectory_error[setting['id']] = \
                    _compare_trajetory(trajectories, ref_traj, i_submodel)

        # save the error for each setting and model
        max_trajectory_errors_copasi.append(max_trajectory_error)

    # create a dataframe from the errors and save
    max_trajectory_errors_copasi = pd.DataFrame(max_trajectory_errors_copasi)

    return max_trajectory_errors_copasi


def _compare_trajetory(trajectories, ref_traj, submodel_index):
    errors = []
    for key in trajectories.keys():
        try:
            sim = trajectories[key].values
            ref = ref_traj[key].values
            errors.append(np.max( np.abs(sim - ref) / (1 + ref) ))
        except KeyError:
            errors.append(float('inf'))
            print('could not map the species ' + key  + ' in submodel '
                  + str(submodel_index) + '. Failed comparison.')
    return max(errors)


max_trajectory_errors_copasi = compare_trajectories_copasi()
max_trajectory_errors_copasi.to_csv(
    os.path.join(DIR_MODELS, 'max_trajectory_errors_copasi.tsv'),
    sep='\t', index=False)
