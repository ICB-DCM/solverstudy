import os
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import scipy.stats as st
import pandas as pd
import seaborn as sns
import copy

from C import DIR_MODELS, DIR_FIGURES

# load the table with model information
model_info = pd.read_csv(os.path.join(
    DIR_MODELS, 'model_summary.tsv'), sep='\t')

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
    if all([str(val) == 'nan' for val in model_info.loc[mi, 'copasi_path']]):
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
                          columns=('Number of species', 'Number of reactions'),
                          index=model_names)
# then add the string labels to not confuse datatypes
all_models = all_models.join(pd.DataFrame(data=accepted_label,
                             columns=('Composition',), index=model_names))
# then add the dataFrame again to have seaborn plotting things correctly
copied_models = copy.deepcopy(all_models)
copied_models['Composition'] = ['all models'] * all_models.shape[0]
data = pd.concat([copied_models, all_models])

# set plotting properties
sns.set(rc={'axes.labelsize':16,
            'xtick.labelsize':12,
            'ytick.labelsize':12})
sns.set_style('ticks')

#
fig = sns.JointGrid(data=data, hue='Composition',
                    x='Number of species', y='Number of reactions',
                    xlim=(-.2, 3.5), ylim=(-.2, 3.5),
                    palette=[[0, 0, 0, 1], [.25, .15, .85, 1], [.9, .6, .2, 1]])
# fig = fig.plot_joint(sns.scatterplot, hue='Composition', data=data)

fig.ax_joint.set_yticks((0, 1, 2, 3))
fig.ax_joint.set_yticklabels(('$10^0$', '$10^1$', '$10^2$', '$10^3$'))
fig.ax_joint.set_xticks((0, 1, 2, 3))
fig.ax_joint.set_xticklabels(('$10^0$', '$10^1$', '$10^2$', '$10^3$'))

sns.histplot(data.loc[data['Composition'] == 'all models', 'Number of species'],
             ax=fig.ax_marg_x, legend=False, element="step", binwidth=0.25,
             edgecolor=[0,0,0,1], facecolor=[0, 0, 0, 0],
             binrange=[0, 3.5])
sns.histplot(data.loc[data['Composition'] == 'rejected', 'Number of species'],
             ax=fig.ax_marg_x, legend=False, element="step", binwidth=0.25,
             edgecolor=[.8, .5, .1, .9], facecolor=[.8, .5, .1, .4],
             binrange=[0, 3.5])
sns.histplot(data.loc[data['Composition'] == 'accepted', 'Number of species'],
             ax=fig.ax_marg_x, legend=False, element="step", binwidth=0.25,
             edgecolor=[.2, .1, .7, .9], facecolor=[.2, .1, .7, .4],
             binrange=[0, 3.5])

sns.histplot(data=data.loc[data['Composition'] == 'all models'], y='Number of reactions',
             ax=fig.ax_marg_y, legend=False, element="step", binwidth=0.25,
             edgecolor=[0,0,0,1], facecolor=[0, 0, 0, 0],
             binrange=[0, 3.5])
sns.histplot(data=data.loc[data['Composition'] == 'rejected'], y='Number of reactions',
             ax=fig.ax_marg_y, legend=False, element="step", binwidth=0.25,
             edgecolor=[.8, .5, .1, .9], facecolor=[.8, .5, .1, .4],
             binrange=[0, 3.5])
sns.histplot(data=data.loc[data['Composition'] == 'accepted'], y='Number of reactions',
             ax=fig.ax_marg_y, legend=False, element="step", binwidth=0.25,
             edgecolor=[.2, .1, .7, .9], facecolor=[.2, .1, .7, .4],
             binrange=[0, 3.5])

biomodels = ('eungdamrong2007', 'froehlich2018', 'holzhutter2004', 'hui2014',
             'lai2014', 'leber2015', 'levchenko2000', 'ouzounoglou2014',
             'pathak2013', 'pathak2013a', 'pritchard2002', 'proctor2010',
             'proctor2013', 'qi2013', 'sasagawa2005', 'sengupta2015',
             'singh2006', 'sivakumar2011', 'ueda2001', 'ung2008', 'yang2007')
for model in all_models.index:
    if all_models.loc[model, 'Composition'] == 'accepted':
        col = [.2, .1, .7, .9]
    else:
        col = [.8, .5, .1, .9]

    if model in biomodels:
        form = 'P'
    else:
        form = 'o'

    fig.ax_joint.plot(all_models.loc[model, 'Number of species'],
                      all_models.loc[model, 'Number of reactions'],
                      form, color=col)

fig.ax_joint.text(0.3, 3.4, 'accepted',
                  color=[0,0,0,1], fontsize=12, va='center', ha='center')
fig.ax_joint.text(.95, 3.4, 'rejected',
                  color=[0, 0, 0, 1], fontsize=12, va='center', ha='center')
fig.ax_joint.text(1.7, 3.2, 'Biomodels',
                  color=[0,0,0,1], fontsize=12, va='center', ha='center')
fig.ax_joint.text(1.7, 3.0, 'JWS online',
                  color=[0, 0, 0, 1], fontsize=12, va='center', ha='center')
fig.ax_joint.plot(0.3, 3.2, 'P', color=[.2, .1, .7, .9])
fig.ax_joint.plot(.95, 3.2, 'P', color=[.8, .5, .1, .9])
fig.ax_joint.plot(0.3, 3.0, 'o', color=[.2, .1, .7, .9])
fig.ax_joint.plot(.95, 3.0, 'o', color=[.8, .5, .1, .9])

fig.ax_joint.text(-0.135, 1.17, 'B', fontsize=20,
                  transform=fig.ax_joint.transAxes)

plt.gcf().set_size_inches((7.0, 7.0))
os.makedirs(DIR_FIGURES, exist_ok=True)
plt.savefig(os.path.join(DIR_FIGURES, 'bias_assessment.pdf'))
plt.savefig(os.path.join(DIR_FIGURES, 'bias_assessment.png'), dpi=300)
plt.show()

species_all = all_models['Number of species'].values
species_acc = all_models[all_models['Composition'] ==
                              'accepted']['Number of species'].values
species_rej =  all_models[all_models['Composition'] ==
                              'rejected']['Number of species'].values
reactions_all = all_models['Number of reactions'].values
reactions_acc = all_models[all_models['Composition'] ==
                              'accepted']['Number of reactions'].values
reactions_rej =  all_models[all_models['Composition'] ==
                              'rejected']['Number of reactions'].values

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
