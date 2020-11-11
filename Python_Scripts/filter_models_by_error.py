import numpy as np
import pandas as pd
import os
import shutil


from C import DIR_MODELS, DIR_MODELS_AMICI, DIR_MODELS_AMICI_FINAL

# load the table with model information
model_info = pd.read_csv(os.path.join(DIR_MODELS, 'model_summary.tsv'),
                         sep='\t')

# load the table with integration errors
max_trajectory_errors_amici = pd.read_csv(
    os.path.join(DIR_MODELS, 'max_trajectory_errors_amici.tsv'),  sep='\t')

# add columns to the model overview table, if necessary
n_submodels = model_info.shape[0]
if 'accepted' not in model_info.keys():
    model_info = model_info.join(pd.Series(data=['False'] * n_submodels,
                                           name='accepted'))
if 'amici_min_error' not in model_info.keys():
    model_info = model_info.join(pd.Series(data=['inf'] * n_submodels,
                                           name='amici_min_error'))
if 'amici_path_final' not in model_info.keys():
    model_info = model_info.join(pd.Series(data=[''] * n_submodels,
                                           name='amici_path_final'))

# We want to call a model "accepted" if our trajectories deviate at most
# by the following amount (combined absolute and relative error) from given
# reference trajectories
acceptance_threshold = 1e-4

# keep track of integration errors and acceptec models
accepted = []
min_error = []
for i_model in max_trajectory_errors_amici.index:
    # get the current row
    current_row = max_trajectory_errors_amici.loc[i_model,:].values
    # get the best simulation: "current_row" comes from a pd..DataFrame, where
    # each column lists an ODE solver setting, each row a model. Column 1 is
    # the model name (discard for having only the numerical errors).
    best_sim_error = np.min(current_row[1:])
    # was the model accepted?
    model_accepted = best_sim_error < acceptance_threshold
    min_error.append(best_sim_error)
    accepted.append(model_accepted)

    # update the model overview table
    amici_path = max_trajectory_errors_amici.loc[i_model, 'amici_path']
    model_info.loc[model_info['amici_path'] ==
                   amici_path, 'amici_min_error'] = best_sim_error
    model_info.loc[model_info['amici_path'] == amici_path, 'accepted'] = model_accepted

    # if the model was accepted: move the files
    if model_accepted:
        old_path = os.path.join(DIR_MODELS, amici_path)
        new_path = os.path.join(DIR_MODELS_AMICI_FINAL, amici_path[13:])
        shutil.copytree(old_path, new_path)

        # add final model path to model info table
        model_info.loc[model_info['amici_path'] == amici_path,
                       'amici_path_final'] = os.path.relpath(new_path, DIR_MODELS)

# save overview table
model_info.to_csv(os.path.join(DIR_MODELS, 'model_summary.tsv'), sep='\t', index=False)
