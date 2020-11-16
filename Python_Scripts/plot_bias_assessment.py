import os
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import scipy.stats as st
import pandas as pd
import seaborn as sns
import copy

from C import DIR_MODELS

# load the table with model information
model_info = pd.read_csv('/home/paulstapor/Dokumente/Projekte/'
                         'ODE-solver-study/solverstudy/SolverStudyWork/'
                         'Models/model_summary (Kopie).tsv', sep='\t')

# collect all models, for which import worked
n_species = []
n_reactions = []
accepted_label = []
model_names = []
model_list = list(set(list(model_info['short_id'])))
for model in model_list:
    # get the first SBML model which belongs to this benchmark model
    # all SBML models of one benchmark have the same number of species and
    # reactions anyway, so we can just take the first to read out the values
    mi = model_info[model_info['short_id'] == model].index.values
    mi0 = model_info[model_info['short_id'] == model].index.values[0]
    # check if import worked
    if all(model_info.loc[mi, 'amici_import'] != 'OK'):
        continue

    # we want to plot on log10-scale
    n_species.append(np.log10(model_info.loc[mi0, 'n_species']))
    n_reactions.append(np.log10(model_info.loc[mi0, 'n_reactions']))
    # collect the model name
    model_names.append(model)
    # collect whether the model was accepted or not
    if any(model_info.loc[mi, 'accepted']):
        accepted_label.append('accepted')
    else:
        accepted_label.append('rejected')

# First create a table with the numeric values
all_models = pd.DataFrame(data=np.array([n_species, n_reactions]).transpose(),
                          columns=('number of species', 'number of reactions'),
                          index=model_names)
# then add the string labels to not confuse datatypes
all_models = all_models.join(pd.DataFrame(data=accepted_label,
                             columns=('Composition',), index=model_names))
# then add the dataFrame again to have seaborn plotting things correctly
copied_models = copy.deepcopy(all_models)
copied_models['Composition'] = ['all models'] * all_models.shape[0]
data = pd.concat([copied_models, all_models])

# set plotting properties
sns.set(rc={'axes.labelsize':18,
            'xtick.labelsize':18,
            'ytick.labelsize':18})
sns.set_style('ticks')

#
fig = sns.JointGrid(data=data, hue='Composition',
                    x='number of species', y='number of reactions',
                    xlim=(-.2, 3.5), ylim=(-.2, 3.5),
                    palette=[[0, 0, 0, 1], [.25, .15, .85, 1], [.9, .6, .2, 1]])
fig = fig.plot_joint(sns.scatterplot, hue='Composition', data=data)

fig.ax_joint.set_yticks((0, 1, 2, 3))
fig.ax_joint.set_yticklabels(('$10^0$', '$10^1$', '$10^2$', '$10^3$'))
fig.ax_joint.set_xticks((0, 1, 2, 3))
fig.ax_joint.set_xticklabels(('$10^0$', '$10^1$', '$10^2$', '$10^3$'))

sns.histplot(data.loc[data['Composition'] == 'all models', 'number of species'],
             ax=fig.ax_marg_x, legend=False, element="step", binwidth=0.25,
             edgecolor=[0,0,0,1], facecolor=[0, 0, 0, 0],
             binrange=[0, 3.5])
sns.histplot(data.loc[data['Composition'] == 'rejected', 'number of species'],
             ax=fig.ax_marg_x, legend=False, element="step", binwidth=0.25,
             edgecolor=[.8, .5, .1, .9], facecolor=[.8, .5, .1, .4],
             binrange=[0, 3.5])
sns.histplot(data.loc[data['Composition'] == 'accepted', 'number of species'],
             ax=fig.ax_marg_x, legend=False, element="step", binwidth=0.25,
             edgecolor=[.2, .1, .7, .9], facecolor=[.2, .1, .7, .4],
             binrange=[0, 3.5])

sns.histplot(data=data.loc[data['Composition'] == 'all models'], y='number of reactions',
             ax=fig.ax_marg_y, legend=False, element="step", binwidth=0.25,
             edgecolor=[0,0,0,1], facecolor=[0, 0, 0, 0],
             binrange=[0, 3.5])
sns.histplot(data=data.loc[data['Composition'] == 'rejected'], y='number of reactions',
             ax=fig.ax_marg_y, legend=False, element="step", binwidth=0.25,
             edgecolor=[.8, .5, .1, .9], facecolor=[.8, .5, .1, .4],
             binrange=[0, 3.5])
sns.histplot(data=data.loc[data['Composition'] == 'accepted'], y='number of reactions',
             ax=fig.ax_marg_y, legend=False, element="step", binwidth=0.25,
             edgecolor=[.2, .1, .7, .9], facecolor=[.2, .1, .7, .4],
             binrange=[0, 3.5])

plt.gcf().set_size_inches((9.0, 9.0))
plt.savefig('../figures/bias_assessment.pdf')
plt.savefig('../figures/bias_assessment.png', dpi=300)

species_all = all_models['number of species'].values
species_acc = all_models[all_models['Composition'] ==
                              'accepted']['number of species'].values
species_rej =  all_models[all_models['Composition'] ==
                              'rejected']['number of species'].values
reactions_all = all_models['number of reactions'].values
reactions_acc = all_models[all_models['Composition'] ==
                              'accepted']['number of reactions'].values
reactions_rej =  all_models[all_models['Composition'] ==
                              'rejected']['number of reactions'].values

ks_species_all_acc = st.ks_2samp(species_all, species_acc)
ks_species_all_rej = st.ks_2samp(species_all, species_rej)
ks_species_acc_rej = st.ks_2samp(species_acc, species_rej)

ks_reactions_all_acc = st.ks_2samp(reactions_all, reactions_acc)
ks_reactions_all_rej = st.ks_2samp(reactions_all, reactions_rej)
ks_reactions_acc_rej = st.ks_2samp(reactions_acc, reactions_rej)

print('KS-test, all models vs. accepted models, number of species:', ks_species_all_acc)
print('KS-test, all models vs. rejected models, number of species:', ks_species_all_rej)
print('KS-test, accepted models vs. rejected models, number of species:', ks_species_acc_rej)
print('KS-test, all models vs. accepted models, number of reactions', ks_reactions_all_acc)
print('KS-test, all models vs. rejected models, number of reactions', ks_reactions_all_rej)
print('KS-test, accepted models vs. rejected models, number of reactions', ks_reactions_acc_rej)
