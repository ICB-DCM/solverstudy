# Main Manuscript Plot --- Figure 5
# scatter plot of AM vs BDF

import os
import numpy as np
from scipy.stats import gaussian_kde
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from C import (
    DIR_RESULTS_ALGORITHMS, LINSOL_DCT, ATOL_RTOLS, NONLINSOL_DCT, SOLALG_DCT,
    DIR_FIGURES)

# general plotting settings
plt.rcParams['figure.figsize'] = [12.0, 5.5]
plt.rcParams['figure.dpi'] = 80
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 16


# get the data
data_am = []
data_bdf = []
data_lsoda = []
data_states = []
for atol, rtol in ATOL_RTOLS:
    # AM algorithm
    f_am = f"atol_{atol}__rtol_{rtol}__linSol_9__nonlinSol_2__solAlg_1.tsv"
    df_am = pd.read_csv(
        os.path.join(DIR_RESULTS_ALGORITHMS, f_am), sep='\t', index_col=0)
    df_am.sort_index(inplace=True)
    data_am.append(df_am['median_intern'].values)
    # get number of state variables
    data_states.append(df_am['n_species'].values)

    # BDF algorithm
    f_bdf = f"atol_{atol}__rtol_{rtol}__linSol_9__nonlinSol_2__solAlg_2.tsv"
    df_bdf = pd.read_csv(
        os.path.join(DIR_RESULTS_ALGORITHMS, f_bdf), sep='\t', index_col=0)
    df_bdf.sort_index(inplace=True)
    data_bdf.append(df_bdf['median_intern'].values)

    # LSODA algorithm
    f_lsoda = f"atol_{atol}__rtol_{rtol}__linSol_1__nonlinSol_2__solAlg_3.tsv"
    df_lsoda = pd.read_csv(
        os.path.join(DIR_RESULTS_ALGORITHMS, f_lsoda), sep='\t', index_col=0)
    df_lsoda.sort_index(inplace=True)
    data_lsoda.append(df_lsoda['median_intern'].values)

data_am = np.array(data_am)
data_am = data_am.reshape((data_am.size,))
data_bdf = np.array(data_bdf)
data_bdf = data_bdf.reshape((data_bdf.size,))
data_lsoda = np.array(data_lsoda)
data_lsoda = data_lsoda.reshape((data_lsoda.size,))
data_states = np.array(data_states)
data_states = data_states.reshape((data_states.size,))

# create list of doubles for scatter plot
adams_bdf_x = [] # red
adams_bdf_y = []
bdf_adams_x = [] # blue
bdf_adams_y = []
ratio_adams_bdf = []
ratio_bdf_adams = []
ratio_equal = []
ratio_adams_zero = []
ratio_bdf_zero = []
ratio_equal_zero = []
num_states_adams_bdf = []
num_states_bdf_adams = []
num_states_equal = []
num_states_adams_zero = []
num_states_bdf_zero = []
num_states_equal_zero = []
equal_x = [] # yellow
equal_y = []
adams_zero_x = []
adams_zero_y = []
bdf_zero_x = []
bdf_zero_y = []
equal_zero_x = []
equal_zero_y = []

for iModel in range(0, len(data_am)):
    x_adams_data = 1000 * data_am[iModel]
    y_bdf_data = 1000 * data_bdf[iModel]
    states_data = data_states[iModel]

    if np.isfinite(x_adams_data) and np.isfinite(y_bdf_data):
        if x_adams_data > y_bdf_data:
            bdf_adams_x.append(x_adams_data)
            bdf_adams_y.append(y_bdf_data)
            ratio_adams_bdf.append(np.log10(x_adams_data / y_bdf_data))
            num_states_adams_bdf.append(states_data)
        elif y_bdf_data > x_adams_data:
            adams_bdf_x.append(x_adams_data)
            adams_bdf_y.append(y_bdf_data)
            ratio_bdf_adams.append(np.log10(x_adams_data / y_bdf_data))
            num_states_bdf_adams.append(states_data)
        elif x_adams_data == y_bdf_data:
            equal_x.append(x_adams_data)
            equal_y.append(y_bdf_data)
            ratio_equal.append(np.log10(x_adams_data / y_bdf_data))
            num_states_equal.append(states_data)

    elif (not np.isfinite(x_adams_data)) and np.isfinite(y_bdf_data):
        adams_zero_x.append(3000)
        adams_zero_y.append(y_bdf_data)
        ratio_adams_zero.append(np.log10(400.))
        num_states_adams_zero.append(states_data)

    elif np.isfinite(x_adams_data) and (not np.isfinite(y_bdf_data)):
        bdf_zero_x.append(x_adams_data)
        bdf_zero_y.append(3000)
        ratio_bdf_zero.append(-np.log10(400.))
        num_states_bdf_zero.append(states_data)

    elif (not np.isfinite(x_adams_data)) and (not np.isfinite(y_bdf_data)):
        equal_zero_x.append(3000)
        equal_zero_y.append(3000)
        ratio_equal_zero.append(np.log10(float('nan')))
        num_states_equal_zero.append(states_data)

# print some interesting properties --- look for the biggest/smallest values
print('adams_bdf_x_smallest: ' + str(sorted(adams_bdf_x)[0]))
print('adams_bdf_y_smallest: ' + str(sorted(adams_bdf_y)[0]))
print('bdf_adams_x_smallest: ' + str(sorted(bdf_adams_x)[0]))
print('bdf_adams_y_smallest: ' + str(sorted(bdf_adams_y)[0]))
print('adams_zero_x_smallest: ' + str(sorted(adams_zero_x)[0]))
print('adams_zero_y_smallest: ' + str(sorted(adams_zero_y)[0]))
print('equal_zero_x_smallest: ' + str(sorted(equal_zero_x)[0]))
print('equal_zero_y_smallest: ' + str(sorted(equal_zero_y)[0]))
print('adams_bdf_x_largest: ' + str(sorted(adams_bdf_x, reverse=True)[0]))
print('adams_bdf_y_largest: ' + str(sorted(adams_bdf_y, reverse=True)[0]))
print('bdf_adams_x_largest: ' + str(sorted(bdf_adams_x, reverse=True)[0]))
print('bdf_adams_y_largest: ' + str(sorted(bdf_adams_y, reverse=True)[0]))
print('adams_zero_x_largest: ' + str(sorted(adams_zero_x, reverse=True)[0]))
print('adams_zero_y_largest: ' + str(sorted(adams_zero_y, reverse=True)[0]))
print('equal_zero_x_largest: ' + str(sorted(equal_zero_x, reverse=True)[0]))
print('equal_zero_y_largest: ' + str(sorted(equal_zero_y, reverse=True)[0]))
print('len(equal_zero_x): ' + str(len(equal_zero_x)))
print('len(equal_zero_y): ' + str(len(equal_zero_y)))

# plot a scatter plot + diagonal line
linestyle = (0, (2, 5, 2, 5))
linewidth = 1
fontsize = 17
labelsize = 10
titlesize = 30
alpha = 1
marker_size = 2

# create custom colormap
colors_1 = [(1, 0.9, 0.6, 0.3), (0.96, 0.41, 0, 1)]
cm_1 = LinearSegmentedColormap.from_list('test', colors_1, N=30)
colors_2 = [(0.8, 0.95, 1, 0.3), (0, 0.21, 0.46, 1)]
cm_2 = LinearSegmentedColormap.from_list('test', colors_2, N=30)

# Calculate the point density
# orange
grid_orange = np.vstack([np.log(adams_bdf_x), np.log(adams_bdf_y)])
kde_orange = gaussian_kde(grid_orange)(grid_orange)
# blue
grid_blue = np.vstack([np.log(bdf_adams_x), np.log(bdf_adams_y)])
kde_blue = gaussian_kde(grid_blue)(grid_blue)

# Sort the points by density, so that the densest points are plotted last
# orange
ids_orange = kde_orange.argsort()
adams_bdf_x, adams_bdf_y, kde_orange = \
    np.array(adams_bdf_x)[ids_orange],\
    np.array(adams_bdf_y)[ids_orange],\
    np.array(kde_orange)[ids_orange]
# blue
ids_blue = kde_blue.argsort()
bdf_adams_x, bdf_adams_y, kde_blue = \
    np.array(bdf_adams_x)[ids_blue],\
    np.array(bdf_adams_y)[ids_blue],\
    np.array(kde_blue)[ids_blue]


# plot scatter plot
ax = plt.axes([0.08, 0.11, 0.37, 0.84])
ax2 = plt.axes([0.57, 0.11, 0.40, 0.84])
z = range(0,3000)
AM_faster = round(100 * len(adams_bdf_x) / data_am.size, 2)
BDF_faster = round(100 * len(bdf_adams_x) / data_am.size, 2)
AM_failed = round(100 * len(adams_zero_x) / data_am.size, 2)
BDF_failed = round(100 * len(bdf_zero_x) / data_am.size, 2)
both_failed = round(100 * len(equal_zero_x) / data_am.size, 2)
plt1 = ax.scatter(
    adams_bdf_x, adams_bdf_y, s=marker_size, c=kde_orange, cmap=cm_1,
    label=f'AM faster: {AM_faster}%',
    zorder=10, clip_on=False, alpha=alpha)
plt2 = ax.scatter(
    bdf_adams_x, bdf_adams_y, s=marker_size, c=kde_blue, cmap=cm_2,
    label=f'BDF faster: {BDF_faster}%',
    zorder=10, clip_on=False, alpha=alpha)
plt3 = ax.scatter(
    equal_x, equal_y, s=marker_size, c='grey', zorder=10, clip_on=False,
    alpha=alpha)
plt4 = ax.scatter(
    adams_zero_x, adams_zero_y, c='orange', cmap=cm_2, marker='D',
    s=marker_size, facecolors='none', edgecolors='blue', zorder=10,
    clip_on=False)
plt5 = ax.scatter(
    bdf_zero_x, bdf_zero_y, c='blue', cmap=cm_1, s=marker_size,
    facecolors='none', edgecolors='orange', marker='D', zorder=10,
    clip_on=False)
plt6 = ax.scatter(
    equal_zero_x, equal_zero_y, s=marker_size, facecolors='none',
    edgecolors='grey', marker='D', zorder=10, clip_on=False)
ax.plot(z, c='black', zorder=20)
ax.set_xlim([0.2, 3000])
ax.set_ylim([0.2, 3000])
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('AM simulation time [ms]', fontsize=fontsize)
ax.set_ylabel('BDF simulation time [ms]', fontsize=fontsize)

# plot legend manually
ax.plot(0.4, 1750, 'o', fillstyle='full', c='orange', markersize=marker_size)
ax.plot(0.4, 950, 'o', fillstyle='full', c='blue', markersize=marker_size)
ax.text(0.6, 1500, f'AM faster: {AM_faster}%', fontsize=fontsize)
ax.text(0.6, 800, f'BDF faster: {BDF_faster}%', fontsize=fontsize)

plt.tick_params(labelsize=labelsize)
ax.spines['top'].set_linestyle(linestyle)
ax.spines['top'].set_linewidth(linewidth)
ax.spines['right'].set_linestyle(linestyle)
ax.spines['right'].set_linewidth(linewidth)
ax.spines['top'].set_color('grey')
ax.spines['right'].set_color('grey')

# write text over axis
ax.text(3500, 25, f'only AM failed: {AM_failed}%',
        fontsize=fontsize, rotation=-90, va='center')
ax.text(25, 3500, f'only BDF failed: {BDF_failed}%',
        fontsize=fontsize, ha='center')
ax.text(5000, 3500, 'Both failed:', fontsize=fontsize,
        ha='center')
ax.text(8000, 2400, f'{both_failed}%',
        fontsize=fontsize, ha='center', va='center')

# plot text 'A'
ax.text(-0.18, 1, 'A', fontsize=fontsize + 5, transform=ax.transAxes)


# choose second axes object
plt.sca(ax2)

# create and adapt spines
ax2.spines['left'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['top'].set_visible(False)

# plot left and right "spines"
plt.plot([-np.log10(400), -np.log10(400)], [0.8, 2000], '--', color='grey',
         linestyle=linestyle, linewidth=linewidth)
plt.plot([np.log10(400), np.log10(400)], [0.8, 2000], '--', color='grey',
         linestyle=linestyle, linewidth=linewidth)

# plot data
plt.scatter(ratio_adams_bdf, num_states_adams_bdf,
            s=marker_size, c=kde_blue, cmap=cm_2, alpha=alpha,
            zorder=10, clip_on=False)
plt.scatter(ratio_bdf_adams, num_states_bdf_adams,
            s=marker_size, c=kde_orange, cmap=cm_1, alpha=alpha,
            zorder=10, clip_on=False)
plt.scatter(ratio_equal, num_states_equal,
            s=marker_size, c='grey', alpha=alpha,
            zorder=100, clip_on=False)
plt.scatter(ratio_adams_zero, num_states_adams_zero,
            s=marker_size, c='blue', cmap=cm_2, alpha=alpha,
            zorder=10, clip_on=False)
plt.scatter(ratio_bdf_zero, num_states_bdf_zero,
            s=marker_size, c='orange', cmap=cm_1, alpha=alpha, marker='D',
            facecolors='none', edgecolors='blue', zorder=10, clip_on=False)
plt.scatter(ratio_equal_zero, num_states_equal_zero,
            s=marker_size, c='grey', cmap=cm_1, alpha=alpha, marker='D',
            facecolors='none', edgecolors='grey', zorder=100, clip_on=False)


# plot central spine
plt.plot([0, 0], [.8, 2000], 'k-', linewidth=linewidth)
plt.plot([-.05, .05], [1000, 1000], 'k-', linewidth=linewidth)
for iMajor in range(3):
    plt.plot([-.05, .05], [10**iMajor, 10**iMajor], 'k-', linewidth=linewidth)
    for iMinor in range(2,10):
        plt.plot([-.02, .02], [iMinor * 10**iMajor, iMinor * 10**iMajor],
                 'k-',linewidth=linewidth)

# formatting
ax2.set_yscale('log')
ax2.set_ylim((0.8, 1900))
ax2.set_xlim((-np.log10(450), np.log10(450)))
ax2.set_yticks([])
plt.minorticks_off()
ax2.text(0, 2000, 'Number of state variables', fontsize=fontsize, ha='center')
ax2.text(-0.1, 1, '$10^0$', fontsize=fontsize, va='center', ha='right')
ax2.text(-0.1, 10, '$10^1$', fontsize=fontsize, va='center', ha='right')
ax2.text(-0.1, 100, '$10^2$', fontsize=fontsize, va='center', ha='right')
ax2.text(-0.1, 1000, '$10^3$', fontsize=fontsize, va='center', ha='right')
ax2.set_xlabel('Computation time ratio AM / BDF', fontsize=fontsize)
plt.xticks([-np.log10(400), -2, -1, 0, 1, 2, np.log10(400)],
           ['', '$10^{-2}$', '$10^{-1}$', '1', '$10^1$', '$10^2$',
            ''], fontsize=fontsize)
ax2.text(-np.log10(600), 20, 'BDF failed', fontsize=fontsize, rotation=90,
         ha='center')
ax2.text(np.log10(600), 20, 'AM failed', fontsize=fontsize, rotation=-90,
         ha='center')

# plot text 'B'
ax.text(-0.08, 1, 'B', fontsize=fontsize + 5, transform=ax2.transAxes)


# change plotting size
plt.gcf().subplots_adjust(bottom=0.2)

# better layout
plt.tight_layout()

# show figure
plt.show()
