import numpy as np
import pandas as pd
import os


from C import DIR_MODELS

# load the table with model information
model_info = pd.read_csv(os.path.join(DIR_MODELS, 'model_summary.tsv'),
                         sep='\t')

max_num_errors = pd.read_csv(os.path.join(DIR_MODELS, 'amici_results.tsv'),
                             sep='\t')

def get_matching_models(max_num_errors):
    accepted = []
    min_error = []
    for i_model in max_num_errors.index:
        tmp = max_num_errors.loc[i_model,:].values
        tmpmin = np.min(tmp[2:])
        min_error.append(tmpmin)
        accepted.append(tmpmin < 1e-4)

    max_num_errors = max_num_errors.join(pd.Series(data=accepted, name='accepted'))
    max_num_errors = max_num_errors.join(pd.Series(data=min_error, name='amici_min_error'))

    return max_num_errors

max_num_errors = get_matching_models(max_num_errors)
max_num_errors.to_csv(os.path.join(DIR_MODELS, 'amici_best_sim.tsv'),
                      sep='\t', index=False)