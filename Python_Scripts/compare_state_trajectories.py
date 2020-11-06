import sys
import numpy as np
import pandas as pd
import os
import logging
import tempfile
import importlib


from C import (DIR_BASE, DIR_MODELS, DIR_MODELS_AMICI, DIR_MODELS_REGROUPED,
               DIR_MODELS_TRAJ_AMICI, DIR_MODELS_TRAJ_REF, simconfig)

from simulation_wrapper_amici import simulation_wrapper

# important paths
models_path = DIR_MODELS_AMICI
models_base_path = DIR_MODELS
base_path = DIR_MODELS_REGROUPED

model_info = pd.read_csv(os.path.join(DIR_MODELS, 'model_summary.tsv'), sep='\t')

# create logger object
logger = logging.getLogger()

# initialize the log settings
logging.basicConfig(filename=os.path.join(DIR_BASE, 'trajectoryComparison.log'),
                    level=logging.DEBUG)

# set up a list with the numerical integration errors
error_list = []
max_num_errors = []

settings = [
    {'id': f'atol:{atol}_rtol:{rtol}_linSol:{ls}_nonlinSol:{nls}_solAlg:{algo}',
     'atol': float(atol), 'rtol': float(rtol),
     'linSol': ls, 'nonlinSol': nls, 'solAlg': algo}
    for (atol, rtol) in (('1e-3', '1e-3'), ('1e-6', '1e-3'), ('1e-6', '1e-6'),
                         ('1e-8', '1e-6'), ('1e-6', '1e-8'), ('1e-12', '1e-10'),
                         ('1e-10', '1e-12'), ('1e-16', '1e-8'), ('1e-8', '1e-16'),
                         ('1e-14', '1e-14'))
    for ls in (1, 6, 7, 8, 9)
    for nls in (1, 2)
    for algo in (1, 2)
]


def compare_trajetories(trajectories, ref_traj):
    errors = []
    for key in trajectories.keys():
        sim = trajectories[key].values
        ref = ref_traj[key].values
        errors.append(np.max( np.abs(sim - ref) / (1 + ref) ))
    return max(errors)


for i_submodel in model_info.index:
    # could the model be successfully imported?
    amici_model_path = model_info.loc[i_submodel, 'amici_path']
    if str(amici_model_path) in ('', 'nan'):
        continue

    # load reference trajectories
    ref_path = model_info.loc[i_submodel, 'ref_trajectory_path']
    ref_traj = pd.read_csv(ref_path, sep='\t')

    # save error
    max_num_error = {'amici_path': amici_model_path}
    for setting in settings:
        trajectories, = simulation_wrapper(simulation_mode=simconfig.TRAJECTORY,
                                           settings=setting,
                                           submodel_path=amici_model_path)

        if trajectories is None:
            max_num_error[setting['id']] = float('inf')
        else:
            max_num_error[setting['id']] = compare_trajetories(trajectories,
                                                               ref_traj)

    max_num_errors.append(max_num_error)

max_num_errors = pd.DataFrame(max_num_errors)
max_num_errors.to_csv(os.path.join(DIR_MODELS, 'amici_results.tsv'), sep='\t')
