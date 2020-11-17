import numpy as np
import pandas as pd
import os
import shutil


from C import DIR_MODELS, DIR_MODELS_AMICI_FINAL, DIR_MODELS_COPASI_FINAL

# load the table with model information
model_info = pd.read_csv(os.path.join(DIR_MODELS, 'model_summary.tsv'),
                         sep='\t')

# load the tables with integration errors
max_trajectory_errors_amici = pd.read_csv(
    os.path.join(DIR_MODELS, 'max_trajectory_errors_amici.tsv'),  sep='\t')
max_trajectory_errors_copasi = pd.read_csv(
    os.path.join(DIR_MODELS, 'max_trajectory_errors_copasi.tsv'),  sep='\t')

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
if 'copasi_min_error' not in model_info.keys():
    model_info = model_info.join(pd.Series(data=['inf'] * n_submodels,
                                           name='copasi_min_error'))
if 'copasi_path_final' not in model_info.keys():
    model_info = model_info.join(pd.Series(data=[''] * n_submodels,
                                           name='copasi_path_final'))

# We want to call a model "accepted" if our trajectories deviate at most
# by the following amount (combined absolute and relative error) from given
# reference trajectories
acceptance_threshold = 1e-4

# run through results of  trajectory comparison with AMICI
for i_model in max_trajectory_errors_amici.index:
    # get the current row
    current_row = max_trajectory_errors_amici.loc[i_model,:].values
    # get the best simulation: "current_row" comes from a pd..DataFrame, where
    # each column lists an ODE solver setting, each row a model. Column 1 is
    # the model name (discard for having only the numerical errors).
    best_sim_error = np.min(current_row[1:])

    # update the model overview table
    amici_path = max_trajectory_errors_amici.loc[i_model, 'amici_path']
    model_info.loc[model_info['amici_path'] ==
                   amici_path, 'amici_min_error'] = best_sim_error

# run through results of  trajectory comparison with COPASI
for i_model in max_trajectory_errors_copasi.index:
    # get the current row
    current_row = max_trajectory_errors_copasi.loc[i_model, :].values
    # get the best simulation: "current_row" comes from a pd..DataFrame, where
    # each column lists an ODE solver setting, each row a model. Column 1 is
    # the model name (discard for having only the numerical errors).
    best_sim_error = np.min(current_row[1:])

    # update the model overview table
    copasi_path = max_trajectory_errors_copasi.loc[i_model, 'copasi_path']
    model_info.loc[model_info['copasi_path'] ==
                   copasi_path, 'copasi_min_error'] = best_sim_error

# Now finally accept models which could be simulated with both tools
for i_model in model_info.index:
    # get necessary information for this model
    best_sim_amici = model_info.loc[i_model, 'amici_min_error']
    best_sim_copasi = model_info.loc[i_model, 'copasi_min_error']
    amici_path = model_info.loc[i_model, 'amici_path']
    copasi_path = model_info.loc[i_model, 'copasi_path']

    # was the model accepted?
    model_accepted = (float(best_sim_amici) < acceptance_threshold) and \
                     (float(best_sim_copasi) < acceptance_threshold)
    model_info.loc[i_model, 'accepted'] = model_accepted

    # if the model was accepted: move the files
    if model_accepted:
        old_path_amici = os.path.join(DIR_MODELS, amici_path)
        new_path_amici = os.path.join(DIR_MODELS_AMICI_FINAL, amici_path[13:])
        shutil.copytree(old_path_amici, new_path_amici)

        old_file_copasi = os.path.join(DIR_MODELS, copasi_path)
        new_file_copasi = os.path.join(DIR_MODELS_COPASI_FINAL, copasi_path[14:])
        new_copasi_folder = os.path.join(DIR_MODELS_COPASI_FINAL,
                                         '/'.join(copasi_path[14:].split('/')[:-1]))
        if not os.path.exists(new_copasi_folder):
            os.makedirs(new_copasi_folder)
        shutil.copyfile(old_file_copasi, new_file_copasi)

        # add final model path to model info table
        model_info.loc[i_model, 'amici_path_final'] = os.path.relpath(
            new_path_amici, DIR_MODELS)
        model_info.loc[i_model, 'copasi_path_final'] = os.path.relpath(
            new_file_copasi, DIR_MODELS)

# save overview table
model_info.to_csv(os.path.join(DIR_MODELS, 'model_summary.tsv'), sep='\t', index=False)
