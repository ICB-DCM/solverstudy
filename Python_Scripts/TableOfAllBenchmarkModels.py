# python script to plot a table containing all benchmark models and their basic properties:
# number of state variables, number of reactions, number of parameters, from which datab it was taken

import matplotlib.pyplot as plt
import pandas as pd
from averageTime import *


# important paths
tsv_path = '../Data/Stat_Reac_Par/NEW_stat_reac_par_paper.tsv'

# load NEW_stat_reac_par_paper.tsv file containing all data needed after averaging
tsv_file = pd.read_csv(tsv_path, sep='\t')
tsv_file = averaging(tsv_file)

# adapt column names
old_names = tsv_file.columns
adapted_column_names = ['model_id', 'number_of_state_variables', 'number_of_reactions', 'number_of_parameters']
for iName in range(0, len(adapted_column_names)):
    tsv_file = tsv_file.rename(columns={old_names[iName]:adapted_column_names[iName]})

# Id names in better shape
data_in_better_shape = []
for iRow in range(0, len(tsv_file['model_id'])):
    _,adapted_id = tsv_file['model_id'][iRow].split('{')
    adapted_id,_ = adapted_id.split('}')
    tsv_file['model_id'][iRow] = adapted_id

# add column for classification
JWS = ['BioModels'] * 26
BioModels = ['JWS'] * (len(tsv_file['model_id']) - len(JWS))
list_of_databases = JWS + BioModels
tsv_file['taken_from_database'] = list_of_databases

# change entry for 'Froehlich2018' to GitHub-Link
for iModel in range(0, len(tsv_file['model_id'])):
    if tsv_file['model_id'][iModel] == 'Froehlich2018':
        tsv_file['taken_from_database'][iModel] = 'https://github.com/ICB-DCM/CS_Signalling_ERBB_RAS_AKT/tree/master/FroehlichKes2018/PEtab'


# save new .tsv file if the new folder exists
if os.path.exists('../../Benchmarking_of_numerical_ODE_integration_methods/Data'):
    tsv_file.to_csv('../../Benchmarking_of_numerical_ODE_integration_methods/Data/Supplementary_ListOfAllModels.tsv', index=False, sep='\t')
else:
    print('Since the directory ../../Benchmarking_of_numerical_ODE_integration_methods/Data does not exist, '
          'to display the table, please save the table manually on some directory of our choice.')