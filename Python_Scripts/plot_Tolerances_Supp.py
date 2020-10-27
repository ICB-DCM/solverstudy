# Supplementary Plot --- Figure S5
# script to plot a histogram for all tolerance settings with success rates

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from averageTime import averaging
from C import DIR_DATA_TOLERANCES

tolerance_path = os.path.join(DIR_DATA_TOLERANCES, 'BDF')

# main .tsv file to norm all other files
main_tsv = pd.read_csv(os.path.join(
    tolerance_path, '2_06_06.tsv'), sep='\t')

# plot as histogram
fontsize = 17
labelsize = 14
titlesize = 30
left = 0.065
bottom = 0.8
width = 0.135
height = 0.127
row_factor = 0.155
column_factor = 0.142
rotation_factor = 90
ylim = [0.7, 200]
xlim = [-1, 2]
bins = 40

# get new .tsv file
main_tsv = averaging(main_tsv)

# open all .tsv tolerance files
tolerance_files = sorted(os.listdir(tolerance_path))
for iTolerance in range(0, len(tolerance_files)):
    next_tsv = pd.read_csv(os.path.join(
        tolerance_path, tolerance_files[iTolerance]), sep='\t')

    # get new .tsv file
    next_tsv = averaging(next_tsv)

    zero_values_counter = 0
    main_intern_is_0_counter = 0
    normed_list = []
    for iFile in range(0, len(main_tsv['id'])):
        main_intern = main_tsv['t_intern_ms'][iFile]
        next_intern = next_tsv['t_intern_ms'][iFile]

        # norm all internal + external time by 06_06
        if main_intern == 0:
            quotient = 0
        else:
            quotient = next_intern / main_intern

        # leave out value if zero but only count for the success rate if next_intern = 0
        if next_intern == 0:
            zero_values_counter += 1
            'No 0 values allowed!'
        elif main_intern == 0:
            main_intern_is_0_counter += 1
            continue
        else:
            normed_list.append(np.log10(quotient))

    # for xlim control
    if sorted(normed_list, reverse=True)[0] > 10:
        print('Need bigger xlim: ' +
              str(sorted(normed_list, reverse=True)[0]) + ' ; ' +
              main_tsv['id'][iFile] + ' ; ' + tolerance_files[iTolerance])

    # get absolute and relative tolerance number
    _, abs_tol, rest = tolerance_files[iTolerance].split('_')
    rel_tol = rest.split('.')[0]
    if abs_tol[0] == '0':
        abs_tol = abs_tol[1]
    if rel_tol[0] == '0':
        rel_tol = rel_tol[1]

    # create axes
    if iTolerance in range(0,6):
        ax1 = plt.axes([left + iTolerance * row_factor, bottom, width, height])
        ax1.set_xlim(xlim)
        ax1.set_ylim(ylim)
        ax1.tick_params(labelbottom=False)
        if iTolerance == 0:
            ax1.text(-0.25, 0.5, r'$10^{-' + str(abs_tol) + '}$',
                     fontsize=fontsize, transform=ax1.transAxes,
                     rotation=rotation_factor)
            ax1.text(0.5, 1.1, r'$10^{-' + str(rel_tol) + '}$',
                     fontsize=fontsize, transform=ax1.transAxes)
        if iTolerance in range(1,6):
            ax1.tick_params(labelleft=False)
            ax1.text(0.5, 1.1, r'$10^{-' + str(rel_tol) + '}$',
                     fontsize=fontsize, transform=ax1.transAxes)
    elif iTolerance in range(6,12):
        ax1 = plt.axes([left + (iTolerance - 6) * row_factor,
                        bottom - 1 * column_factor ,width, height])
        ax1.set_xlim(xlim)
        ax1.set_ylim(ylim)
        ax1.tick_params(labelbottom=False)
        if iTolerance == 6:
            ax1.text(-0.25, 0.5, r'$10^{-' + str(abs_tol) + '}$',
                     fontsize=fontsize, transform=ax1.transAxes,
                     rotation=rotation_factor)
        if iTolerance in range(7,12):
            ax1.tick_params(labelleft=False)
    elif iTolerance in range(12,18):
        ax1 = plt.axes([left + (iTolerance - 12) * row_factor,
                        bottom - 2 * column_factor , width, height])
        ax1.set_xlim(xlim)
        ax1.set_ylim(ylim)
        ax1.tick_params(labelbottom=False)
        if iTolerance == 12:
            ax1.text(-0.25, 0.5, r'$10^{-' + str(abs_tol) + '}$',
                     fontsize=fontsize, transform=ax1.transAxes,
                     rotation=rotation_factor)
        if iTolerance in range(13,18):
            ax1.tick_params(labelleft=False)
    elif iTolerance in range(18, 24):
        ax1 = plt.axes([left + (iTolerance - 18) * row_factor,
                        bottom - 3 * column_factor , width, height])
        ax1.set_xlim(xlim)
        ax1.set_ylim(ylim)
        ax1.tick_params(labelbottom=False)
        if iTolerance == 18:
            ax1.text(-0.25, 0.5, r'$10^{-' + str(abs_tol) + '}$',
                     fontsize=fontsize, transform=ax1.transAxes,
                     rotation=rotation_factor)
        if iTolerance in range(19,24):
            ax1.tick_params(labelleft=False)
    elif iTolerance in range(24,30):
        ax1 = plt.axes([left + (iTolerance - 24) * row_factor,
                        bottom - 4 * column_factor , width, height])
        ax1.set_xlim(xlim)
        ax1.set_ylim(ylim)
        ax1.tick_params(labelbottom=False)
        if iTolerance == 24:
            ax1.text(-0.25, 0.5, r'$10^{-' + str(abs_tol) + '}$',
                     fontsize=fontsize, transform=ax1.transAxes,
                     rotation=rotation_factor)
        if iTolerance in range(25,30):
            ax1.tick_params(labelleft=False)
    elif iTolerance in range(30,36):
        ax1 = plt.axes([left + (iTolerance - 30) * row_factor,
                        bottom - 5 * column_factor , width, height])
        ax1.set_xlim(xlim)
        ax1.set_ylim(ylim)
        if iTolerance == 30:
            ax1.text(-0.25, 0.5, r'$10^{-' + str(abs_tol) + '}$',
                     fontsize=fontsize, transform=ax1.transAxes,
                     rotation=rotation_factor)
        if iTolerance in range(31,36):
            ax1.tick_params(labelleft=False)

    ax1.set_yscale('log')
    ax1.set_xticklabels([r'$10^{-1}$', r'$10^{0}$', r'$10^{1}$', r'$10^{2}$'])
    ax1.tick_params(labelsize=labelsize)
    if iTolerance == 0:
        plot_histogram = ax1.hist(x=normed_list, range=None, bins=bins,
                                  log=False)
    else:
        plot_histogram = ax1.hist(x=normed_list, range=None, bins=bins,
                                  log=False)
    plt.text(x=1, y=90, s=str(round(100 - (
        len(normed_list) + main_intern_is_0_counter) / (
        len(normed_list) +
        zero_values_counter + main_intern_is_0_counter) * 100, 2)) +
        ' %', fontsize=fontsize)

    # make top and right boxlines invisible
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)


# set global labels
plt.text(-5.7, 6.8, 'Rel.tol.:', fontsize=fontsize, transform=ax1.transAxes)
plt.text(-6.18, 6.7, 'Abs.tol.:', fontsize=fontsize, transform=ax1.transAxes)
plt.text(-3.2, -0.55, 'Relative simulation time', fontsize=fontsize + 5,
         transform=ax1.transAxes)
plt.text(-6.18, 2.1, 'Number of models', fontsize=fontsize + 5,
         transform=ax1.transAxes, rotation=90)

# better layout
plt.tight_layout()

# change plotting size
plt.rcParams['figure.figsize'] = [15.0, 7.]
plt.rcParams['figure.dpi'] = 80
plt.rcParams['savefig.dpi'] = 200
plt.rcParams['font.size'] = 17

# show figure
plt.show()
