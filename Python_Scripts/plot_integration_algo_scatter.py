# Main Manuscript Plot --- Figure 5
# scatter plot of AM vs BDF

import os
import numpy as np
from scipy.stats import gaussian_kde
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from C import (
    DIR_RESULTS_ALGORITHMS, ATOL_RTOLS, DIR_FIGURES)

# general plotting settings
plt.rcParams['figure.figsize'] = [12.0, 16.5]

axs = [
    plt.axes([0.08, 0.31 * 0.11 + .005, 0.37, 0.32 * .84]),
    plt.axes([0.57, 0.31 * 0.11 + .005, 0.40, 0.32 * 0.84]),
    plt.axes([0.08, 0.31 * 0.11 + .34, 0.37, 0.32 * 0.84]),
    plt.axes([0.57, 0.31 * 0.11 + .34, 0.40, 0.32 * 0.84]),
    plt.axes([0.08, 0.31 * 0.11 + .675, 0.37, 0.32 * 0.84]),
    plt.axes([0.57, 0.31 * 0.11 + .675, 0.40, 0.32 * 0.84])]

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

# create custom colormap
darkest_am = (0.96, 0.41, 0, 1)
colors_am = [(1, 0.9, 0.6, 0.3), darkest_am]
cm_am = LinearSegmentedColormap.from_list('test', colors_am, N=30)
darkest_bdf = (0, 0.21, 0.46, 1)
colors_bdf = [(0.8, 0.95, 1, 0.3), darkest_bdf]
cm_bdf = LinearSegmentedColormap.from_list('test', colors_bdf, N=30)
darkest_lsoda = (0.55, 0.6, 0.5, 1)
colors_lsoda = [(0.9, 1, 0.8, 0.3), darkest_lsoda]
cm_lsoda = LinearSegmentedColormap.from_list('test', colors_lsoda, N=30)


def plot_scatter_times(data_setting_a, data_setting_b,
                       setting_a_name, setting_b_name,
                       colormap_a, colormap_b,
                       color_name_a, color_name_b,
                       lower_bound, upper_bound, ratio_bound,
                       ax_left, ax_right, letter_left, letter_right):
    # create list of doubles for scatter plot
    setting_a_better_x = []  # red
    setting_a_better_y = []
    setting_b_better_x = []  # blue
    setting_b_better_y = []
    ratio_a_over_b = []
    ratio_b_over_a = []
    ratio_equal = []
    ratio_setting_a_failed = []
    ratio_setting_b_failed = []
    ratio_both_failed = []
    n_states_setting_a_better = []
    n_states_setting_b_better = []
    num_states_equal = []
    n_states_setting_a_failed = []
    n_states_setting_b_failed = []
    n_states_both_failed = []
    equal_x = []  # yellow
    equal_y = []
    setting_a_failed_x = []
    setting_a_failed_y = []
    setting_b_failed_x = []
    setting_b_failed_y = []
    both_failed_x = []
    both_failed_y = []

    for iModel in range(0, len(data_am)):
        x_data_a = 1000 * data_setting_a[iModel]
        y_data_b = 1000 * data_setting_b[iModel]
        states_data = data_states[iModel]

        if np.isfinite(x_data_a) and np.isfinite(y_data_b):
            if x_data_a > y_data_b:
                setting_b_better_x.append(x_data_a)
                setting_b_better_y.append(y_data_b)
                ratio_a_over_b.append(np.log10(x_data_a / y_data_b))
                n_states_setting_b_better.append(states_data)
            elif y_data_b > x_data_a:
                setting_a_better_x.append(x_data_a)
                setting_a_better_y.append(y_data_b)
                ratio_b_over_a.append(np.log10(x_data_a / y_data_b))
                n_states_setting_a_better.append(states_data)
            elif x_data_a == y_data_b:
                equal_x.append(x_data_a)
                equal_y.append(y_data_b)
                ratio_equal.append(np.log10(x_data_a / y_data_b))
                num_states_equal.append(states_data)

        elif (not np.isfinite(x_data_a)) and np.isfinite(y_data_b):
            setting_a_failed_x.append(upper_bound)
            setting_a_failed_y.append(y_data_b)
            ratio_setting_a_failed.append(np.log10(ratio_bound))
            n_states_setting_a_failed.append(states_data)

        elif np.isfinite(x_data_a) and (not np.isfinite(y_data_b)):
            setting_b_failed_x.append(x_data_a)
            setting_b_failed_y.append(upper_bound)
            ratio_setting_b_failed.append(-np.log10(ratio_bound))
            n_states_setting_b_failed.append(states_data)

        elif (not np.isfinite(x_data_a)) and (not np.isfinite(y_data_b)):
            both_failed_x.append(upper_bound)
            both_failed_y.append(upper_bound)
            ratio_both_failed.append(np.log10(float('nan')))
            n_states_both_failed.append(states_data)

    # plot a scatter plot + diagonal line
    linestyle = (0, (2, 5, 2, 5))
    linewidth = 1
    fontsize = 16
    labelsize = 12
    lettersize = 20
    alpha = 1
    marker_size = 2

    ###########################################################################
    # Left scatter plot

    # Calculate the point density
    # color setting a
    grid_color_a = np.vstack([np.log(setting_a_better_x),
                              np.log(setting_a_better_y)])
    kde_color_a = gaussian_kde(grid_color_a)(grid_color_a)
    # color setting b
    grid_color_b = np.vstack([np.log(setting_b_better_x),
                              np.log(setting_b_better_y)])
    kde_color_b = gaussian_kde(grid_color_b)(grid_color_b)

    # Sort the points by density, so that the densest points are plotted last
    # color for setting a
    ids_color_a = kde_color_a.argsort()
    setting_a_better_x, setting_a_better_y, kde_color_a = \
        np.array(setting_a_better_x)[ids_color_a],\
        np.array(setting_a_better_y)[ids_color_a],\
        np.array(kde_color_a)[ids_color_a]
    # color for setting b
    ids_color_b = kde_color_b.argsort()
    setting_b_better_x, setting_b_better_y, kde_color_b = \
        np.array(setting_b_better_x)[ids_color_b],\
        np.array(setting_b_better_y)[ids_color_b],\
        np.array(kde_color_b)[ids_color_b]

    # plot scatter plot
    a_faster_percentage = round(100 * len(setting_a_better_x) / data_am.size, 2)
    b_faster_percentage = round(100 * len(setting_b_better_x) / data_am.size, 2)
    a_failed_percentage = round(100 * len(setting_a_failed_x) / data_am.size, 2)
    b_failed_percentage = round(100 * len(setting_b_failed_x) / data_am.size, 2)
    both_failed_percentage = round(100 * len(both_failed_x) / data_am.size, 2)
    # plot a-better points (above diagonal)
    ax_left.scatter(
        setting_a_better_x, setting_a_better_y,
        s=marker_size, c=kde_color_a, cmap=colormap_a,
        label=f'{setting_a_name} faster: {a_faster_percentage}%',
        zorder=10, clip_on=False, alpha=alpha)
    # plot b-better points (below diagonal)
    ax_left.scatter(
        setting_b_better_x, setting_b_better_y,
        s=marker_size, c=kde_color_b, cmap=colormap_b,
        label=f'{setting_b_name} faster: {b_faster_percentage}%',
        zorder=10, clip_on=False, alpha=alpha)
    # plot a=b-points (on diagonal)
    ax_left.scatter(
        equal_x, equal_y, s=marker_size, c='grey', zorder=10, clip_on=False,
        alpha=alpha)
    # plot a-failed points on right axis
    ax_left.scatter(
        setting_a_failed_x, setting_a_failed_y,
        c=color_name_a, cmap=colormap_b, marker='D',
        s=marker_size, facecolors='none', edgecolors=color_name_b, zorder=10,
        clip_on=False)
    # plot b-failed points on upper axis
    ax_left.scatter(
        setting_b_failed_x, setting_b_failed_y,
        c=color_name_b, cmap=colormap_a, s=marker_size,
        facecolors='none', edgecolors=color_name_a, marker='D', zorder=10,
        clip_on=False)
    # plot both-failed points in upper-right corner
    ax_left.scatter(
        both_failed_x, both_failed_y, s=marker_size, facecolors='none',
        edgecolors='grey', marker='D', zorder=10, clip_on=False)
    # plot diagonal
    ax_left.plot([lower_bound, upper_bound], [lower_bound, upper_bound],
                 c='black', zorder=20)

    # decorations
    ax_left.set_xlim([lower_bound, upper_bound])
    ax_left.set_ylim([lower_bound, upper_bound])
    ax_left.set_xscale('log')
    ax_left.set_yscale('log')
    ax_left.set_xlabel(f'{setting_a_name} simulation time [ms]',
                       fontsize=fontsize)
    ax_left.set_ylabel(f'{setting_b_name} simulation time [ms]',
                       fontsize=fontsize)

    geo_mean_bounds = np.sqrt(upper_bound * lower_bound)
    beyond_bound = upper_bound * 1.15

    # plot a/b faster texts
    ax_left.text(.2 * geo_mean_bounds, .25 * upper_bound,
                 f'{setting_a_name} faster: {a_faster_percentage}%',
                 fontsize=fontsize, va='top', ha='center',
                 color=color_name_a)
    ax_left.text(geo_mean_bounds, 4 * lower_bound,
                 f'{setting_b_name} faster: {b_faster_percentage}%',
                 fontsize=fontsize, va='bottom', ha='left',
                 color=color_name_b)

    # decorations
    ax_left.tick_params(labelsize=labelsize)
    ax_left.spines['top'].set_linestyle(linestyle)
    ax_left.spines['top'].set_linewidth(linewidth)
    ax_left.spines['right'].set_linestyle(linestyle)
    ax_left.spines['right'].set_linewidth(linewidth)
    ax_left.spines['top'].set_color('grey')
    ax_left.spines['right'].set_color('grey')

    # write failed-%-text over axes
    ax_left.text(
        beyond_bound, geo_mean_bounds,
        f'only {setting_a_name} failed: {a_failed_percentage}%',
        fontsize=fontsize, rotation=-90, va='center', ha='left')
    ax_left.text(
        geo_mean_bounds, beyond_bound,
        f'only {setting_b_name} failed: {b_failed_percentage}%',
        fontsize=fontsize, ha='center', va='bottom')
    ax_left.text(
        beyond_bound, beyond_bound,
        'Both failed:', fontsize=fontsize, ha='center', va='bottom')
    ax_left.text(
        beyond_bound, upper_bound, f'{both_failed_percentage}%',
        fontsize=fontsize, ha='left', va='top')

    # plot text 'A'
    ax_left.text(-0.18, 1, letter_left, fontsize=lettersize,
                 transform=ax_left.transAxes)

    ###########################################################################
    # Right ratio plot

    # hide spines
    ax_right.spines['left'].set_visible(False)
    ax_right.spines['right'].set_visible(False)
    ax_right.spines['top'].set_visible(False)

    # plot left and right "spines"
    max_model_size = 2000
    ax_right.plot([-np.log10(ratio_bound), -np.log10(ratio_bound)],
                  [0.8, max_model_size], '--', color='grey',
                  linestyle=linestyle, linewidth=linewidth)
    ax_right.plot([np.log10(ratio_bound), np.log10(ratio_bound)],
                  [0.8, max_model_size], '--', color='grey',
                  linestyle=linestyle, linewidth=linewidth)

    # plot data
    # plot b-better points (right)
    ax_right.scatter(
        ratio_a_over_b, n_states_setting_b_better,
        s=marker_size, c=kde_color_b, cmap=colormap_b, alpha=alpha,
        zorder=10, clip_on=False)
    # plot a-better points (left)
    ax_right.scatter(
        ratio_b_over_a, n_states_setting_a_better,
        s=marker_size, c=kde_color_a, cmap=colormap_a, alpha=alpha,
        zorder=10, clip_on=False)
    # plot a=b-points on center axis
    ax_right.scatter(
        ratio_equal, num_states_equal,
        s=marker_size, c='grey', alpha=alpha,
        zorder=100, clip_on=False)
    # plot a-failed points on right axis
    ax_right.scatter(
        ratio_setting_a_failed, n_states_setting_a_failed,
        s=marker_size, c=color_name_b, cmap=colormap_b, alpha=alpha,
        zorder=10, clip_on=False)
    # plot b-failed points on left axis
    ax_right.scatter(
        ratio_setting_b_failed, n_states_setting_b_failed,
        s=marker_size, c=color_name_a, cmap=colormap_a,
        alpha=alpha, marker='D',
        facecolors='none', edgecolors=color_name_a,
        zorder=10, clip_on=False)
    ax_right.scatter(
        ratio_both_failed, n_states_both_failed,
        s=marker_size, c='grey', alpha=alpha, marker='D',
        facecolors='none', edgecolors='grey', zorder=100, clip_on=False)

    # plot central spine with ticks
    ax_right.plot([0, 0], [.8, max_model_size], 'k-', linewidth=linewidth)
    ax_right.plot([-.05, .05], [1e3, 1e3], 'k-', linewidth=linewidth)
    for iMajor in range(3):
        ax_right.plot([-.05, .05], [10 ** iMajor, 10 ** iMajor], 'k-',
                      linewidth=linewidth)
        for iMinor in range(2, 10):
            ax_right.plot([-.02, .02],
                          [iMinor * 10 ** iMajor, iMinor * 10 ** iMajor],
                          'k-', linewidth=linewidth)

    # formatting
    ax_right.set_yscale('log')
    ax_right.set_ylim((0.8, max_model_size))
    ax_right.set_xlim((-np.log10(ratio_bound * 1.15),
                       np.log10(ratio_bound * 1.15)))
    ax_right.set_yticks([])
    ax_right.tick_params(labelsize=labelsize)

    beyond_bound_side = ratio_bound * 1.15
    ax_right.text(0, max_model_size * 1.1, 'Number of state variables',
                  fontsize=fontsize, ha='center', va='bottom')
    ax_right.text(-0.1, 1, '$10^0$', fontsize=labelsize,
                  va='center', ha='right')
    ax_right.text(-0.1, 10, '$10^1$', fontsize=labelsize,
                  va='center', ha='right')
    ax_right.text(-0.1, 100, '$10^2$', fontsize=labelsize,
                  va='center', ha='right')
    ax_right.text(-0.1, 1000, '$10^3$', fontsize=labelsize,
                  va='center', ha='right')
    ax_right.set_xlabel(f'Computation time ratio {setting_a_name} / {setting_b_name}',
                        fontsize=fontsize)
    ax_right.set_xticks(
        [-np.log10(ratio_bound), -2, -1, 0, 1, 2, np.log10(ratio_bound)])
    ax_right.set_xticklabels(
        ['', '$10^{-2}$', '$10^{-1}$', '1', '$10^1$', '$10^2$', ''])
    ax_right.text(-np.log10(beyond_bound_side), np.sqrt(max_model_size),
                  f'{setting_b_name} failed', fontsize=fontsize, rotation=90,
                  ha='right', va='center')
    ax_right.text(np.log10(beyond_bound_side), np.sqrt(max_model_size),
                  f'{setting_a_name} failed', fontsize=fontsize, rotation=-90,
                  ha='left', va='center')

    # plot text 'B'
    ax_right.text(-0.08, 1, letter_right,
                  fontsize=lettersize, transform=ax_right.transAxes)


plot_scatter_times(data_am, data_bdf, 'AM', 'BDF',
                   cm_am, cm_bdf, darkest_am, darkest_bdf,
                   0.05, 2e3, 700,
                   axs[4], axs[5], 'A', 'B')

plot_scatter_times(data_lsoda, data_am, 'LSODA', 'AM',
                   cm_lsoda, cm_am, darkest_lsoda, darkest_am,
                   0.05, 2e5, 700,
                   axs[2], axs[3], 'C', 'D')

plot_scatter_times(data_lsoda, data_bdf, 'LSODA', 'BDF',
                   cm_lsoda, cm_bdf, darkest_lsoda, darkest_bdf,
                   0.05, 2e5, 700,
                   axs[0], axs[1], 'E', 'F')

# Save plot
os.makedirs(DIR_FIGURES, exist_ok=True)
plt.savefig(os.path.join(DIR_FIGURES, "integration_algo_scatter_main.pdf"))
plt.savefig(os.path.join(DIR_FIGURES, "integration_algo_scatter_main.png"),
            dpi=300)

# show figure
plt.show()
