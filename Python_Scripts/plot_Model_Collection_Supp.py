import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

from matplotlib import cm


from C import DIR_MODELS, DIR_FIGURES

# load the table with model information
#model_info = pd.read_csv(os.path.join(DIR_MODELS, 'model_summary.tsv'),
#                         sep='\t')

## ========== AMICI data ======================================================
# load the table with integration errors
max_errors_amici = pd.read_csv(
    os.path.join(DIR_MODELS, 'max_trajectory_errors_amici.tsv'),  sep='\t')

# collect all models, for which import worked Amici
min_errors_amici = []
model_list = list(max_errors_amici['amici_path'])
for model in model_list:
    # get all SBML models (for which import worked), and read out the maximal
    # error found during trajectory comparison
    mi = int(max_errors_amici[
        max_errors_amici['amici_path'] == model].index.values)

    # discard the column with model name
    error_values_amici = np.array(max_errors_amici.loc[mi,:].values[1:],
                                  dtype=float)
    min_errors_amici.append(np.min(error_values_amici))

# First create a table with the numeric values
all_models_amici = pd.DataFrame(
    data=np.array(max_errors_amici.values[:, 1:], dtype=float),
    columns=list(max_errors_amici.keys())[1:],
    index=model_list)
# then add the string labels to not confuse datatypes
all_models_amici = all_models_amici.join(pd.DataFrame(
    data=min_errors_amici,
    columns=('best simulation',),
    index=model_list))
min_errors_amici = np.array(min_errors_amici)
min_errors_amici.sort()

## ========== COPASI data =====================================================

# load the table with integration errors
max_errors_copasi = pd.read_csv(
    os.path.join(DIR_MODELS, 'max_trajectory_errors_copasi.tsv'),  sep='\t')

# collect all models, for which import worked with Copasi
min_errors_copasi = []
model_list = list(max_errors_copasi['copasi_path'])
for model in model_list:
    # get all SBML models (for which import worked), and read out the maximal
    # error found during trajectory comparison
    mi = int(max_errors_copasi[
        max_errors_copasi['copasi_path'] == model].index.values)

    # discard the column with model name
    error_values_copasi = np.array(max_errors_copasi.loc[mi, :].values[1:],
                                   dtype=float)
    min_errors_copasi.append(np.min(error_values_copasi))

# First create a table with the numeric values
all_models_copasi = pd.DataFrame(
    data=np.array(max_errors_copasi.values[:, 1:], dtype=float),
    columns=list(max_errors_copasi.keys())[1:],
    index=model_list)
# then add the string labels to not confuse datatypes
all_models_copasi = all_models_copasi.join(pd.DataFrame(
    data=min_errors_copasi,
    columns=('best simulation',),
    index=model_list))
min_errors_copasi = np.array(min_errors_copasi)
min_errors_copasi.sort()

## ========== Plotting part ===================================================
# colors
cmap_amici = cm.get_cmap('Purples', 10)
cmap_copasi = cm.get_cmap('Greens', 10)
colors_amici = [cmap_amici(c) for c in range(9, 2, -1)]
colors_copasi = [cmap_copasi(c) for c in range(9, 2, -1)]

# create rang eof accepted models
model_range_amici = list(range(len(min_errors_amici)))
model_range_copasi = list(range(len(min_errors_copasi)))


# plot with subsettings
keys_amici = ('atol:1e-3_rtol:1e-3_linSol:9_nonlinSol:2_solAlg:2',
              'atol:1e-6_rtol:1e-3_linSol:9_nonlinSol:2_solAlg:2',
              'atol:1e-6_rtol:1e-6_linSol:9_nonlinSol:2_solAlg:2',
              'atol:1e-12_rtol:1e-10_linSol:9_nonlinSol:2_solAlg:2',
              'atol:1e-16_rtol:1e-8_linSol:9_nonlinSol:2_solAlg:2',
              'atol:1e-14_rtol:1e-14_linSol:9_nonlinSol:2_solAlg:2',
              'atol:1e-3_rtol:1e-3_linSol:9_nonlinSol:2_solAlg:1',
              'atol:1e-6_rtol:1e-3_linSol:9_nonlinSol:2_solAlg:1',
              'atol:1e-6_rtol:1e-6_linSol:9_nonlinSol:2_solAlg:1',
              'atol:1e-12_rtol:1e-10_linSol:9_nonlinSol:2_solAlg:1',
              'atol:1e-16_rtol:1e-8_linSol:9_nonlinSol:2_solAlg:1',
              'atol:1e-14_rtol:1e-14_linSol:9_nonlinSol:2_solAlg:1',)[::-1]
keys_copasi = ('atol:1e-3_rtol:1e-3_linSol:1_nonlinSol:2_solAlg:3',
               'atol:1e-6_rtol:1e-3_linSol:1_nonlinSol:2_solAlg:3',
               'atol:1e-6_rtol:1e-6_linSol:1_nonlinSol:2_solAlg:3',
               'atol:1e-12_rtol:1e-10_linSol:1_nonlinSol:2_solAlg:3',
               'atol:1e-16_rtol:1e-8_linSol:1_nonlinSol:2_solAlg:3',
               'atol:1e-14_rtol:1e-14_linSol:1_nonlinSol:2_solAlg:3',)[::-1]
leg_amici = ('atol: 1e-14, rtol: 1e-14, Newton, KLU, BDF',
             'atol: 1e-16, rtol: 1e-8, Newton, KLU, BDF',
             'atol: 1e-12, rtol: 1e-10, Newton, KLU, BDF',
             'atol: 1e-6, rtol: 1e-6, Newton, KLU, BDF',
             'atol: 1e-6, rtol: 1e-3, Newton, KLU, BDF',
             'atol: 1e-3, rtol: 1e-3, Newton, KLU, BDF',
             'atol: 1e-14, rtol: 1e-14, Newton, KLU, AM',
             'atol: 1e-16, rtol: 1e-8, Newton, KLU, AM',
             'atol: 1e-12, rtol: 1e-10, Newton, KLU, AM',
             'atol: 1e-6, rtol: 1e-6, Newton, KLU, AM',
             'atol: 1e-6, rtol: 1e-3, Newton, KLU, AM',
             'atol: 1e-3, rtol: 1e-3, Newton, KLU, AM',)
leg_copasi = ('atol: 1e-14, rtol: 1e-14, Newton, DENSE, LSODA',
              'atol: 1e-16, rtol: 1e-8, Newton, DENSE, LSODA',
              'atol: 1e-12, rtol: 1e-10, Newton, DENSE, LSODA',
              'atol: 1e-6, rtol: 1e-6, Newton, DENSE, LSODA',
              'atol: 1e-6, rtol: 1e-3, Newton, DENSE, LSODA',
              'atol: 1e-3, rtol: 1e-3, Newton, DENSE, LSODA',)

# plot accepting with all settings
plt.plot(min_errors_amici, model_range_amici, '-', linewidth=3,
         color=colors_amici[0], label='AMICI, any setting')

for i_key, key in enumerate(keys_amici[:6]):
    data_amici = np.array(list(all_models_amici[key]))
    data_amici.sort()
    plt.plot(data_amici, model_range_amici, '--', linewidth=1.5,
             color=colors_amici[i_key + 1], label=leg_amici[i_key])

for i_key, key in enumerate(keys_amici[6:]):
    data_amici = np.array(list(all_models_amici[key]))
    data_amici.sort()
    plt.plot(data_amici, model_range_amici, ':', linewidth=1.5,
             color=colors_amici[i_key + 1], label=leg_amici[i_key + 6])

# plot accepting with all settings
plt.plot(min_errors_copasi, model_range_copasi, '-', linewidth=3,
         color=colors_copasi[0], label='COPASI, any setting')

for i_key, key in enumerate(keys_copasi):
    data_copasi = np.array(list(all_models_copasi[key]))
    data_copasi.sort()
    plt.plot(data_copasi, model_range_copasi, linewidth=1.5,
             label=leg_copasi[i_key],
             linestyle='dashdot', color=colors_copasi[i_key + 1])

# plot vertical line
plt.plot([1e-4, 1e-4], [-5, 410], 'k:', linewidth=2)

plt.legend(fontsize=12)
plt.xlabel('Maximal allowed error of state trajectories '
           '(acceptance threshold)', fontsize=15)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.ylabel('Number of accepted models', fontsize=15)
plt.xscale('log')
plt.ylim((-10, 420))

ax = plt.gca()
ax.text(.5e-4, 390, 'final acceptance threshold', ha='right', fontsize=12)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# plot
plt.gcf().set_size_inches((15.0, 10.0))
os.makedirs(DIR_FIGURES, exist_ok=True)
plt.savefig(os.path.join(DIR_FIGURES, 'Model_Collection_Supp.eps'),
            format='eps', dpi=300)
plt.savefig(os.path.join(DIR_FIGURES, 'Model_Collection_Supp.pdf'))
plt.savefig(os.path.join(DIR_FIGURES, 'Model_Collection_Supp.png'), dpi=300)
