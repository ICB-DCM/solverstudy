# Supplement Plot --- Figure S7
# scatter plot of AM vs BDF

import os
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from averageTime import averaging
from C import DIR_DATA_WHOLESTUDY

base_path = DIR_DATA_WHOLESTUDY
Adams_base_path = base_path
BDF_base_path = base_path

# open .tsv files
list_directory_general = sorted(os.listdir(base_path))
list_directory_adams = []
list_directory_bdf = []
for iFile in range(0, int(len(list_directory_general)/2)):
    list_directory_adams.append(list_directory_general[iFile])
    list_directory_bdf.append(
        list_directory_general[iFile + int(len(list_directory_general)/2)])

# create list of doubles for scatter plot
adams_bdf_x = []          # red
adams_bdf_y = []
bdf_adams_x = []          # green
bdf_adams_y = []
equal_x = []              # yellow
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

    # average from 210 to 166 models
    adams_tsv_file = averaging(adams_tsv_file)
    bdf_tsv_file = averaging(bdf_tsv_file)

    for iModel in range(0, len(adams_tsv_file['t_intern_ms'])):
        x_adams_data = adams_tsv_file['t_intern_ms'][iModel]
        y_bdf_data = bdf_tsv_file['t_intern_ms'][iModel]

        if x_adams_data != 0 and y_bdf_data != 0:
            if x_adams_data > y_bdf_data:
                bdf_adams_x.append(x_adams_data)
                bdf_adams_y.append(y_bdf_data)
            elif y_bdf_data > x_adams_data:
                adams_bdf_x.append(x_adams_data)
                adams_bdf_y.append(y_bdf_data)
            elif x_adams_data == y_bdf_data:
                equal_x.append(x_adams_data)
                equal_y.append(y_bdf_data)
        elif x_adams_data == 0 and y_bdf_data != 0:
            adams_zero_x.append(45000)
            adams_zero_y.append(y_bdf_data)
        elif x_adams_data != 0 and y_bdf_data == 0:
            bdf_zero_x.append(x_adams_data)
            bdf_zero_y.append(45000)
        elif x_adams_data == 0 and y_bdf_data == 0:
            equal_zero_x.append(45000)
            equal_zero_y.append(45000)

    # display progress
    print(iTsvFile)

# look for the biggest/smallest values
print('adams_bdf_x: ' + str(sorted(adams_bdf_x)[0]))
print('adams_bdf_y: ' + str(sorted(adams_bdf_y)[0]))
print('bdf_adams_x: ' + str(sorted(bdf_adams_x)[0]))
print('bdf_adams_y: ' + str(sorted(bdf_adams_y)[0]))
print('adams_zero_x: ' + str(sorted(adams_zero_x)[0]))
print('adams_zero_y: ' + str(sorted(adams_zero_y)[0]))
print('bdf_zero_x: ' + str(sorted(bdf_zero_x)[0]))
print('bdf_zero_y: ' + str(sorted(bdf_zero_y)[0]))
print('equal_zero_x: ' + str(sorted(equal_zero_x)[0]))
print('equal_zero_y: ' + str(sorted(equal_zero_y)[0]))
print('len(equal_zero_x): ' + str(len(equal_zero_x)))
print('len(equal_zero_y): ' + str(len(equal_zero_y)))

# plot a scatter plot + diagonal line
linestyle = (0, (2, 5, 2, 5))
linewidth = 1
fontsize = 12
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
# orange edge
grid_orange_edge = np.vstack([np.log(adams_zero_x), np.log(adams_zero_y)])
kde_orange_edge = gaussian_kde(grid_orange_edge)(grid_orange_edge)
# blue edge
grid_blue_edge = np.vstack([np.log(bdf_zero_x), np.log(bdf_zero_y)])


# Sort the points by density, so that the densest points are plotted last
# orange
ids_orange = kde_orange.argsort()
adams_bdf_x, adams_bdf_y, kde_orange = \
    np.array(adams_bdf_x)[ids_orange], \
    np.array(adams_bdf_y)[ids_orange], \
    np.array(kde_orange)[ids_orange]
# blue
ids_blue = kde_blue.argsort()
bdf_adams_x, bdf_adams_y, kde_blue = \
    np.array(bdf_adams_x)[ids_blue], \
    np.array(bdf_adams_y)[ids_blue], \
    np.array(kde_blue)[ids_blue]
# orange
ids_orange_edge = kde_orange_edge.argsort()
adams_zero_x, adams_zero_y, kde_orange_edge = \
    np.array(adams_zero_x)[ids_orange_edge], \
    np.array(adams_zero_y)[ids_orange_edge], \
    np.array(kde_orange_edge)[ids_orange_edge]


# plot scatter plot
ax = plt.axes([0.1, 0.12, 0.8, 0.8])
plt.gcf().subplots_adjust(bottom=0.2)
z = range(0,45000)
plt1 = ax.scatter(
    adams_bdf_x, adams_bdf_y, s=marker_size, c=kde_orange, cmap=cm_1,
    label='AM faster: ' + str(round(len(adams_bdf_x) / len(adams_tsv_file['t_intern_ms'])*10/7, 2)) + ' %',
    zorder=10, clip_on=False, alpha=alpha)
plt2 = ax.scatter(
    bdf_adams_x, bdf_adams_y, s=marker_size, c=kde_blue, cmap=cm_2,
    label='BDF faster: ' + str(round(len(bdf_adams_x)/len(adams_tsv_file['t_intern_ms'])*10/7, 2)) + ' %',
    zorder=10, clip_on=False, alpha=alpha)
plt3 = ax.scatter(
    equal_x, equal_y, s=marker_size, c='grey', zorder=10, clip_on=False,
    alpha=alpha)
plt4 = ax.scatter(
    adams_zero_x, adams_zero_y, c=kde_orange_edge, cmap=cm_2, marker='D',
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
ax.set_xlim([0.2, 45000])
ax.set_ylim([0.2, 45000])
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('AM simulation time [ms]', fontsize=fontsize)
ax.set_ylabel('BDF simulation time [ms]', fontsize=fontsize)

# plot legend manually
ax.plot(0.4, 25000, 'o', fillstyle='full', c='orange', markersize=marker_size)
ax.plot(0.4, 12500, 'o', fillstyle='full', c='blue', markersize=marker_size)
plt.text(
    0.6, 20000,
    'AM faster: ' + str(round(len(adams_bdf_x) / len(adams_tsv_file['t_intern_ms'])*10/7, 2)) + ' %',
    fontsize=labelsize)
plt.text(
    0.6, 10000,
    'BDF faster: ' + str(round(len(bdf_adams_x)/len(adams_tsv_file['t_intern_ms'])*10/7, 2)) + ' %',
    fontsize=labelsize)

plt.tick_params(labelsize=labelsize)
plt.gca().set_aspect('equal', adjustable='box')
ax.spines['top'].set_linestyle(linestyle)
ax.spines['top'].set_linewidth(linewidth)
ax.spines['right'].set_linestyle(linestyle)
ax.spines['right'].set_linewidth(linewidth)
ax.spines['top'].set_color('red')
ax.spines['right'].set_color('red')

# write text over axis
ax.text(
    55000, 2.5,
    'only AM failed: ' + str(round(len(adams_zero_x)/len(adams_tsv_file['t_intern_ms'])*100/len(list_directory_adams), 2)) + ' %',
    fontsize=fontsize, rotation=-90)
ax.text(
    3, 55000,
    'only BDF failed: ' + str(round(len(bdf_zero_x)/len(adams_tsv_file['t_intern_ms'])*100/len(list_directory_adams), 2)) + ' %',
    fontsize=fontsize)
ax.text(70000, 8000, 'Both failed:', fontsize=fontsize, rotation=-45)
ax.text(
    50000, 10000,
    str(round(len(equal_zero_x)/len(adams_tsv_file['t_intern_ms'])*100/len(list_directory_adams), 2)) + ' %',
    fontsize=fontsize, rotation=-45)

# change plotting size
plt.gcf().subplots_adjust(bottom=0.2)

# better layout
plt.tight_layout()

# show figure
plt.show()
