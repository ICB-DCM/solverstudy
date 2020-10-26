# Main Manuscript Plot --- Figure 5
# scatter plot of AM vs BDF

import os
import numpy as np
from scipy.stats import gaussian_kde
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from averageTime import averaging
from C import DIR_DATA_WHOLESTUDY

base_path = DIR_DATA_WHOLESTUDY
Adams_base_path = base_path
BDF_base_path = base_path

# general plotting settings
plt.rcParams['figure.figsize'] = [15.0, 7.]
plt.rcParams['figure.dpi'] = 80
plt.rcParams['savefig.dpi'] = 200
plt.rcParams['font.size'] = 17

# open .tsv files
list_directory_general = sorted(os.listdir(base_path))
list_directory_adams = []
list_directory_bdf = []
for iFile in range(0, int(len(list_directory_general)/2)):
    adams_split = list_directory_general[iFile].split('_')
    bdf_split = list_directory_general[iFile + int(
        len(list_directory_general)/2)].split('_')
    if adams_split[1] == '2' and adams_split[2] == '9':
        list_directory_adams.append(list_directory_general[iFile])
    if bdf_split[1] == '2'and bdf_split[2] == '9':
        list_directory_bdf.append(list_directory_general[
            iFile + int(len(list_directory_general)/2)])

# create list of doubles for scatter plot
adams_bdf_x = [] # red
adams_bdf_y = []
bdf_adams_x = [] # green
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

for iTsvFile in range(0, len(list_directory_adams)):
    adams_tsv_file = pd.read_csv(os.path.join(
        Adams_base_path, list_directory_adams[iTsvFile]), sep='\t')
    bdf_tsv_file = pd.read_csv(os.path.join(
        BDF_base_path, list_directory_bdf[iTsvFile]), sep='\t')

    # average from 211 to 167 models
    adams_tsv_file = averaging(adams_tsv_file)
    bdf_tsv_file = averaging(bdf_tsv_file)

    for iModel in range(0, len(adams_tsv_file['t_intern_ms'])):
        x_adams_data = adams_tsv_file['t_intern_ms'][iModel]
        y_bdf_data = bdf_tsv_file['t_intern_ms'][iModel]
        states_data = adams_tsv_file['state_variables'][iModel]

        if x_adams_data != 0 and y_bdf_data != 0:
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

        elif x_adams_data == 0 and y_bdf_data != 0:
            adams_zero_x.append(3000)
            adams_zero_y.append(y_bdf_data)
            ratio_adams_zero.append(np.log10(400.))
            num_states_adams_zero.append(states_data)

        elif x_adams_data != 0 and y_bdf_data == 0:
            bdf_zero_x.append(x_adams_data)
            bdf_zero_y.append(3000)
            ratio_bdf_zero.append(-np.log10(400.))
            num_states_bdf_zero.append(states_data)

        elif x_adams_data == 0 and y_bdf_data == 0:
            equal_zero_x.append(3000)
            equal_zero_y.append(3000)
            ratio_equal_zero.append(np.log10(float('nan')))
            num_states_equal_zero.append(states_data)

    # display progress
    print(iTsvFile)

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
plt1 = ax.scatter(
    adams_bdf_x, adams_bdf_y, s=marker_size, c=kde_orange, cmap=cm_1,
    label='AM faster: ' + str(round(len(adams_bdf_x) / len(adams_tsv_file['t_intern_ms'])*100/len(list_directory_adams), 2)) + ' %',
    zorder=10, clip_on=False, alpha=alpha)
plt2 = ax.scatter(
    bdf_adams_x, bdf_adams_y, s=marker_size, c=kde_blue, cmap=cm_2,
    label='BDF faster: ' + str(round(len(bdf_adams_x) / len(adams_tsv_file['t_intern_ms'])*100/len(list_directory_adams), 2)) + ' %', zorder=10, clip_on=False, alpha=alpha)
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
ax.text(0.6, 1500, 'AM faster: ' + str(round(len(adams_bdf_x) / len(adams_tsv_file['t_intern_ms'])*100/len(list_directory_adams), 2)) + ' %', fontsize=fontsize)
ax.text(0.6, 800, 'BDF faster: ' + str(round(len(bdf_adams_x)/len(adams_tsv_file['t_intern_ms'])*100/len(list_directory_adams), 2)) + ' %', fontsize=fontsize)

plt.tick_params(labelsize=labelsize)
ax.spines['top'].set_linestyle(linestyle)
ax.spines['top'].set_linewidth(linewidth)
ax.spines['right'].set_linestyle(linestyle)
ax.spines['right'].set_linewidth(linewidth)
ax.spines['top'].set_color('grey')
ax.spines['right'].set_color('grey')

# write text over axis
ax.text(3500, 25,'only AM failed: ' + str(round(len(adams_zero_x) / len(
    adams_tsv_file['t_intern_ms'])*100/len(list_directory_adams), 2)) + ' %',
        fontsize=fontsize, rotation=-90, va='center')
ax.text(25, 3500, 'only BDF failed: ' + str(round(len(bdf_zero_x) / len(
    adams_tsv_file['t_intern_ms'])*100/len(list_directory_adams), 2)) + ' %',
        fontsize=fontsize, ha='center')
ax.text(5000, 3500, 'Both failed:', fontsize=fontsize,
        ha='center')
ax.text(8000, 2400, str(round(len(equal_zero_x) / len(adams_tsv_file[
    't_intern_ms'])*100/len(list_directory_adams), 2)) + ' %',
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
