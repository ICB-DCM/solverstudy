# Main Manuscript Plot --- Figure 2
# scrip to plot a Scatter and Histogram plot to investigate the difference
#  between the non-linear solvers

import os
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt

from averageTime import averaging
from C import DIR_DATA_WHOLESTUDY

base_path = DIR_DATA_WHOLESTUDY

# list of all data frames for nonLinSol == 1 for better indexing in the future
all_intern_columns_1 = [pd.DataFrame(columns=[]) for _ in range(72)]

# list of all data frames for nonLinSol == 2 for better indexing in the future
all_intern_columns_2 = [pd.DataFrame(columns=[]) for _ in range(72)]

all_intern_columns = [all_intern_columns_1, all_intern_columns_2]
column_names = []

# choose only the correct files
all_files = sorted(os.listdir(base_path))
correct_files_1 = []
correct_files_2 = []
for iFile in range(0, len(all_files)):
    if all_files[iFile].split('_')[0] == '1':
        correct_files_1.append(all_files[iFile])
    elif all_files[iFile].split('_')[0] == '2':
        correct_files_2.append(all_files[iFile])
correct_files = [correct_files_1, correct_files_2]

# open all .tsv linear solver files + save right column in data frame
for iNonLinSol in range(0, len(correct_files)):
    for iCorrectFile in range(0, len(correct_files_1)):
        next_tsv = pd.read_csv(os.path.join(
            base_path, correct_files[iNonLinSol][iCorrectFile]), sep='\t')

        # change .tsv-id form e.g. 1_06_10.tsv to 06_10
        new_name = correct_files[iNonLinSol][iCorrectFile].split('.')[0].split('_')[3] + '_' + \
                   correct_files[iNonLinSol][iCorrectFile].split('.')[0].split('_')[4]

        # reset after each iteration
        next_time_value = []
        num_x = []

        # open next file
        next_tsv = averaging(next_tsv)

        # get the correct values
        for iFile in range(0, len(next_tsv['id'])):  # each file
            if next_tsv['t_intern_ms'][iFile] != 0:
                next_time_value.append(next_tsv['t_intern_ms'][iFile])
                num_x.append(next_tsv['state_variables'][iFile])

        # append new column to existing data frame with correct values
        column_names.append(str(new_name))
        all_intern_columns[iNonLinSol][iCorrectFile]['state_variables'] = \
            pd.Series(num_x)
        all_intern_columns[iNonLinSol][iCorrectFile][str(new_name)] = \
            pd.Series(next_time_value)

# length of the last file
file_length = len(next_tsv['id'])

# get correct data for the bar plot
# plot a customized bar plot
fontsize = 12
labelsize = 8
rotation = 45
linewidth = 1

# plot one density plot
ax = plt.axes()
index = np.arange(39)

# initialize y-data
adams_data_1 = []
bdf_data_1 = []
adams_data_2 = []
bdf_data_2 = []

# Functional
blank_space_counter = 0
for iDensityPoint in range(0, int(len(correct_files_1)/2) + 4):
    if iDensityPoint in [7, 15, 23, 31]:
        adams_data_1.append(math.inf)
        bdf_data_1.append(math.inf)
        blank_space_counter += 1
    else:
        adams_data_1.append(1 - round(len(all_intern_columns_1[
            iDensityPoint - blank_space_counter][column_names[
                iDensityPoint - blank_space_counter]]) / file_length, 4))
        bdf_data_1.append(1 - round(len(all_intern_columns_2[
            iDensityPoint - blank_space_counter][column_names[
                iDensityPoint - blank_space_counter]]) / file_length, 4))
nonLinSol11 = ax.plot(index, adams_data_1, '-x', c='#fdb863',
                      label='Functional AM')
nonLinSol21 = ax.plot(index, bdf_data_1, '-x', c='#e66101',
                      label='Functional BDF')

# Newton-type
blank_space_counter = 0
for iDensityPoint in range(
        int(len(correct_files_1)/2), len(correct_files_1) + 4):
    if iDensityPoint in [int(len(correct_files_1)/2) + 7,
                         int(len(correct_files_1)/2) + 15,
                         int(len(correct_files_1)/2) + 23,
                         int(len(correct_files_1)/2) + 31]:
        adams_data_2.append(math.inf)
        bdf_data_2.append(math.inf)
        blank_space_counter += 1
    else:
        adams_data_2.append(1 - round(
            len(all_intern_columns_1[iDensityPoint - blank_space_counter][
                column_names[
                    iDensityPoint - blank_space_counter]]) / file_length, 4))
        bdf_data_2.append(1 - round(
            len(all_intern_columns_2[iDensityPoint - blank_space_counter][
                column_names[
                    iDensityPoint - blank_space_counter]]) / file_length, 4))
nonLinSol12 = ax.plot(index, adams_data_2, '-x', c='#b2abd2',
                      label='Newton-type AM')
nonLinSol22 = ax.plot(index, bdf_data_2, '-x', c='#5e3c99',
                      label='Newton-type BDF')

ax.set_ylabel('Failure rate [%]', fontsize=fontsize)
ax.set_xlim([-0.5, 38.5])
ax.set_ylim([0, 0.3])
ax.set_yticklabels(['0', '5', '10', '15', '20', '25', '30'], fontsize=labelsize)

# plot black separation line
for iLine in [7,15,23,31]:
    ax.plot([iLine,iLine], [0, 0.3], '--k', linewidth=linewidth)

# create major and minor ticklabels
ax.text(0, -0.1,
        '--------------DENSE--------------- ---------------GMRES--------------- -------------BICGSTAB'
        '------------- ---------------TFQMR--------------- ----------------KLU-----------------',
        fontsize=labelsize, transform=ax.transAxes)
upper_labels = [
    r'$10^{-6}$', r'$10^{-8}$', r'$10^{-8}$', r'$10^{-10}$', r'$10^{-12}$', r'$10^{-14}$', r'$10^{-16}$', '',
    r'$10^{-6}$', r'$10^{-8}$', r'$10^{-8}$', r'$10^{-10}$', r'$10^{-12}$', r'$10^{-14}$', r'$10^{-16}$', '',
    r'$10^{-6}$', r'$10^{-8}$', r'$10^{-8}$', r'$10^{-10}$', r'$10^{-12}$', r'$10^{-14}$', r'$10^{-16}$', '',
    r'$10^{-6}$', r'$10^{-8}$', r'$10^{-8}$', r'$10^{-10}$', r'$10^{-12}$', r'$10^{-14}$', r'$10^{-16}$', '',
    r'$10^{-6}$', r'$10^{-8}$', r'$10^{-8}$', r'$10^{-10}$', r'$10^{-12}$', r'$10^{-14}$', r'$10^{-16}$']
lower_labels = [
    r'$10^{-8}$', r'$10^{-6}$', r'$10^{-16}$', r'$10^{-12}$', r'$10^{-10}$', r'$10^{-14}$', r'$10^{-8}$', '',
    r'$10^{-8}$', r'$10^{-6}$', r'$10^{-16}$', r'$10^{-12}$', r'$10^{-10}$', r'$10^{-14}$', r'$10^{-8}$', '',
    r'$10^{-8}$', r'$10^{-6}$', r'$10^{-16}$', r'$10^{-12}$', r'$10^{-10}$', r'$10^{-14}$', r'$10^{-8}$', '',
    r'$10^{-8}$', r'$10^{-6}$', r'$10^{-16}$', r'$10^{-12}$', r'$10^{-10}$', r'$10^{-14}$', r'$10^{-8}$', '',
    r'$10^{-8}$', r'$10^{-6}$', r'$10^{-16}$', r'$10^{-12}$', r'$10^{-10}$', r'$10^{-14}$', r'$10^{-8}$']

ax.set_xticks(list(range(39)))
minor_list_1 = [x + 0.001 for x in list(range(39))]
ax.set_xticks(minor_list_1, minor=True)
ax.set_xticklabels(upper_labels, fontsize=labelsize, rotation=rotation)
ax.set_xticklabels(lower_labels, minor=True, fontsize=labelsize,
                   rotation=rotation)
ax.tick_params(axis='x', which='major', pad=25)
ax.tick_params(axis='x', which='minor', pad=50)
ax.text(-0.12, -0.1, 'Lin. sol.: ', fontsize=fontsize, transform=ax.transAxes)
ax.text(-0.12, -0.22, 'Abs. tol.: ', fontsize=fontsize, transform=ax.transAxes)
ax.text(-0.12, -0.34, 'Rel. tol.: ', fontsize=fontsize, transform=ax.transAxes)

# delete xticks at specific positions
specific_xticks_major = ax.xaxis.get_major_ticks()
for iTick in [7, 15, 23, 31]:
    specific_xticks_major[iTick].set_visible(False)
specific_xticks_minor = ax.xaxis.get_minor_ticks()
for iTick in [7, 15, 23, 31]:
    specific_xticks_minor[iTick].set_visible(False)

# plot legend
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.4), fancybox=True,
          shadow=True, ncol=5, frameon=False, fontsize=fontsize)

# make top and right boxlines invisible
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# better layout
plt.tight_layout()

# change plotting size
fig = plt.gcf()
fig.set_size_inches(18.5, 10.5)

# show figure
plt.show()

###############################################################################
# adjustment values for a plot editor to replicate the exact plot seen in the
#  main manuscript

#top = 0.96,
#bottom = 0.328,
#left = 0.11,
#right = 0.975,
#hspace = 0.2,
#wspace = 0.2
