import numpy as np
import pandas as pd
import os
import shutil


from C import DIR_MODELS, DIR_MODELS_AMICI, DIR_MODELS_AMICI_FINAL

# load the table with model information
model_info = pd.read_csv(os.path.join(DIR_MODELS, 'model_summary.tsv'),
                         sep='\t')

# load the table with integration errors
max_num_errors = pd.read_csv(os.path.join(DIR_MODELS,
                                          'amici_trajectory_errors.tsv'),
                             sep='\t')

# add columns to the model overview table, if necessary
n_submodels = model_info.shape[0]
if 'accepted' not in model_info.keys():
    model_info = model_info.join(pd.Series(data=['False'] * n_submodels,
                                           name='accepted'))
if 'amici_min_error' not in model_info.keys():
    model_info = model_info.join(pd.Series(data=['inf'] * n_submodels,
                                           name='amici_min_error'))
if 'amici_path_final' not in model_info.keys():
    model_info = model_info.join(pd.Series(data=['inf'] * n_submodels,
                                           name='amici_path_final'))

# keep track of integration errors and acceptec models
accepted = []
min_error = []
for i_model in max_num_errors.index:
    # get the current row
    current_row = max_num_errors.loc[i_model,:].values
    # get the best simulation
    best_sim_error = np.min(current_row[2:])
    # was the model accepted?
    acc = best_sim_error < 1e-4
    min_error.append(best_sim_error)
    accepted.append(acc)

    # update the model overview table
    amici_path = max_num_errors.loc[i_model, 'amici_path']
    model_info.loc[model_info['amici_path'] ==
                   amici_path, 'amici_min_error'] = best_sim_error
    model_info.loc[model_info['amici_path'] == amici_path, 'accepted'] = acc

    # if the model was accepted: move the files
    if acc:
        old_path = os.path.join(DIR_MODELS, amici_path)
        new_path = os.path.join(DIR_MODELS_AMICI_FINAL, amici_path[13:])
        shutil.copytree(old_path, new_path)

        # update model info table
        model_info.loc[model_info['amici_path'] == amici_path,
                       'amici_path_final'] = os.path.relpath(new_path, DIR_MODELS)

# save overview table
model_info.to_csv(os.path.join(DIR_MODELS, 'model_summary.tsv'), sep='\t', index=False)
