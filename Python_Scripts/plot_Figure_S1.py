import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt


from C import DIR_MODELS, DIR_MODELS_AMICI, DIR_MODELS_AMICI_FINAL

# load the table with model information
#model_info = pd.read_csv(os.path.join(DIR_MODELS, 'model_summary.tsv'),
#                         sep='\t')

# load the table with integration errors
max_errors_amici = pd.read_csv(
    os.path.join(DIR_MODELS, 'max_trajectory_errors_amici.tsv'),  sep='\t')
max_errors_copasi = pd.read_csv(
    os.path.join(DIR_MODELS, 'max_trajectory_errors_copasi.tsv'),  sep='\t')

# collect all models, for which import worked
min_errors_amici = []
model_list = list(max_errors_amici['amici_path'])
for model in model_list:
    # get all SBML models (for which import worked), and read out the maximal
    # error found during trajectory comparison
    mi = int(max_errors_amici[max_errors_amici['amici_path'] == model].index.values)

    # discard the column with model name
    error_values_amici = np.array(max_errors_amici.loc[mi,:].values[1:],
                                  dtype=float)
    min_errors_amici.append(np.min(error_values_amici))

# First create a table with the numeric values
all_models_amici = pd.DataFrame(data=np.array(max_errors_amici.values[:, 1:], dtype=float),
                          columns=list(max_errors_amici.keys())[1:],
                          index=model_list)
# then add the string labels to not confuse datatypes
all_models_amici = all_models_amici.join(pd.DataFrame(data=min_errors_amici,
                                                      columns=('best simulation',),
                                                      index=model_list))
min_errors_amici = np.array(min_errors_amici)
min_errors_amici.sort()

# collect all models, for which import worked
min_errors_copasi = []
model_list = list(max_errors_copasi['copasi_path'])
for model in model_list:
    # get all SBML models (for which import worked), and read out the maximal
    # error found during trajectory comparison
    mi = int(max_errors_copasi[max_errors_copasi['copasi_path'] == model].index.values)

    # discard the column with model name
    error_values_copasi = np.array(max_errors_copasi.loc[mi,:].values[1:],
                                  dtype=float)
    min_errors_copasi.append(np.min(error_values_copasi))

# First create a table with the numeric values
all_models_copasi = pd.DataFrame(data=np.array(max_errors_copasi.values[:, 1:], dtype=float),
                          columns=list(max_errors_copasi.keys())[1:],
                          index=model_list)
# then add the string labels to not confuse datatypes
all_models_copasi = all_models_copasi.join(pd.DataFrame(data=min_errors_copasi,
                                                        columns=('best simulation',),
                                                        index=model_list))
min_errors_copasi = np.array(min_errors_copasi)
min_errors_copasi.sort()


plt.plot(min_errors_amici, range(len(min_errors_amici)), 'k-', linewidth=2)
plt.plot(min_errors_copasi, range(len(min_errors_copasi)), 'b-', linewidth=2)
plt.xlabel('maximal allowed error of state trajectories (acceptance threshold)')
plt.ylabel('number of accepted models')
plt.xscale('log')
plt.show()
