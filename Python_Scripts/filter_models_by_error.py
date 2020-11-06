import numpy as np
import pandas as pd
import os


from C import DIR_MODELS

# load the table with model information
model_info = pd.read_csv(os.path.join(DIR_MODELS, 'model_summary.tsv'),
                         sep='\t')

max_num_errors = pd.read_csv(os.path.join(DIR_MODELS, 'amici_results.tsv'),
                             sep='\t')

n_submodels = model_info.shape[0]
model_info = model_info.join(pd.Series(data=['False'] * n_submodels,
                                       name='accepted'))
model_info = model_info.join(pd.Series(data=['inf'] * n_submodels,
                                       name='amici_min_error'))

accepted = []
min_error = []
for i_model in max_num_errors.index:
    tmp = max_num_errors.loc[i_model,:].values

    tmpmin = np.min(tmp[2:])
    acc = tmpmin < 1e-4
    min_error.append(tmpmin)
    accepted.append(acc)

    amici_path = max_num_errors.loc[i_model, 'amici_path']
    model_info.loc[
        model_info['amici_path'] == amici_path, 'amici_min_error'] = tmpmin
    model_info.loc[model_info['amici_path'] == amici_path, 'accepted'] = acc

max_num_errors = max_num_errors.join(pd.Series(data=accepted, name='accepted'))
max_num_errors = max_num_errors.join(pd.Series(data=min_error, name='amici_min_error'))

model_info.to_csv(os.path.join(DIR_MODELS, 'model_summary.tsv'), sep='\t', index=False)
