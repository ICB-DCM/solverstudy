# Supplementary Plot --- Figure S3
# script to plot Scatter Plot and Box Plot for the linear solver study

import matplotlib.pyplot as plt
from averageTime import *
from LinearRegression import *


left = 0.07
bottom = 0.1
width = 0.43
height = 0.85
row_factor = 0.47
column_factor = 0.22
rotation_factor = 90

ax1 = plt.axes([left, bottom, width, height])
ax2 = plt.axes([left + row_factor, bottom, width, height])

def LinearSolver(solAlg, nonLinSol):

    ######## subplot 1: linear regressions of combined scatter plots
    # list of all 35 data frames for better indexing in the future
    all_intern_columns = [pd.DataFrame(columns=[]), pd.DataFrame(columns=[]),
                          pd.DataFrame(columns=[]), pd.DataFrame(columns=[]),
                          pd.DataFrame(columns=[]), pd.DataFrame(columns=[]),
                          pd.DataFrame(columns=[]), pd.DataFrame(columns=[]),
                          pd.DataFrame(columns=[]), pd.DataFrame(columns=[]),
                          pd.DataFrame(columns=[]), pd.DataFrame(columns=[]),
                          pd.DataFrame(columns=[]), pd.DataFrame(columns=[]),
                          pd.DataFrame(columns=[]), pd.DataFrame(columns=[]),
                          pd.DataFrame(columns=[]), pd.DataFrame(columns=[]),
                          pd.DataFrame(columns=[]), pd.DataFrame(columns=[]),
                          pd.DataFrame(columns=[]), pd.DataFrame(columns=[]),
                          pd.DataFrame(columns=[]), pd.DataFrame(columns=[]),
                          pd.DataFrame(columns=[]), pd.DataFrame(columns=[]),
                          pd.DataFrame(columns=[]), pd.DataFrame(columns=[]),
                          pd.DataFrame(columns=[]), pd.DataFrame(columns=[]),
                          pd.DataFrame(columns=[]),
                          pd.DataFrame(columns=[]),
                          pd.DataFrame(columns=[]),
                          pd.DataFrame(columns=[]),
                          pd.DataFrame(columns=[])]
    column_names = []

    # check whether the folder 'Benchmarking_of_numerical_ODE_integration_methods/Data' exists
    if not os.path.exists('../../Benchmarking_of_numerical_ODE_integration_methods/Data/WholeStudy'):
        base_path = '../Data/WholeStudy'
    elif os.path.exists('../../Benchmarking_of_numerical_ODE_integration_methods/Data/WholeStudy'):
        base_path = '../../Benchmarking_of_numerical_ODE_integration_methods/Data/WholeStudy'

    # choose only the correct files
    all_files = sorted(os.listdir(base_path))
    correct_files = []
    for iFile in range(0, len(all_files)):
        if all_files[iFile].split('_')[0] == solAlg and all_files[iFile].split('_')[1] == nonLinSol:
            correct_files.append(all_files[iFile])

    # open all .tsv linear solver files + save right column in data frame
    for iCorrectFile in range(0, len(correct_files)):  # each .tsv file
        next_tsv = pd.read_csv(base_path + '/' + correct_files[iCorrectFile], sep='\t')

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

        # append new column to existing data frame with correct log10 values
        column_names.append('simulation_time')
        all_intern_columns[iCorrectFile]['state_variables'] = pd.Series(num_x)
        all_intern_columns[iCorrectFile]['simulation_time'] = pd.Series(next_time_value)

    # plot scatter plot of all data points for the accompynying linear solver + linear regressions
    fontsize = 12
    labelsize = 8
    alpha = 0.5
    marker_size = 2
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_xlim([0.8, 2000])
    ax1.set_ylim([0.2, 100000])
    ax1.set_xlabel('Number of state variables', fontsize=fontsize)
    ax1.set_ylabel('Simulation time [ms]', fontsize=fontsize)
    ax1.tick_params(labelsize=labelsize)

    linSol_for_Legend = ['DENSE', 'GMRES', 'BICGSTAB', 'TFQMR', 'KLU']
    colors = ['#d73027', '#fc8d59', '#fee090', '#91bfdb', '#4575b4']
    for iLinearSolverDataPoints in range(0, int(len(correct_files)/7)):
        # concatenate Data Frames in categories of linear solver data points
        vertically_stacked_tsv = pd.concat([all_intern_columns[7*iLinearSolverDataPoints], all_intern_columns[7*iLinearSolverDataPoints + 1],
                                    all_intern_columns[7*iLinearSolverDataPoints + 2], all_intern_columns[7*iLinearSolverDataPoints + 3],
                                    all_intern_columns[7*iLinearSolverDataPoints + 4], all_intern_columns[7*iLinearSolverDataPoints + 5],
                                    all_intern_columns[7*iLinearSolverDataPoints + 6]], axis=0)
        vertically_stacked_tsv = vertically_stacked_tsv.reset_index(drop=True)

        # do a linear regression
        y_axis_interception, slope = linearRegression(vertically_stacked_tsv, 'state_variables', 'simulation_time')

        # plot a scatter plot + linear regressions
        num_x = [np.log10(p) for p in vertically_stacked_tsv['state_variables']]
        data_simulation_time = [np.log10(q) for q in vertically_stacked_tsv['simulation_time']]
        data_regression = [l[0] for l in [10 ** k for k in [y_axis_interception + j for j in [slope * i for i in num_x]]]]
        exp_num_x = [10 ** m for m in list(num_x)]
        exp_simulation_time = [10 ** n for n in list(data_simulation_time)]
        ax1.scatter(exp_num_x, exp_simulation_time, s=marker_size, alpha=alpha, c=colors[iLinearSolverDataPoints])
        ax1.plot(exp_num_x, data_regression, c=colors[iLinearSolverDataPoints], label=linSol_for_Legend[iLinearSolverDataPoints] + ': slope = ' + str(np.round(slope[0], 4)))

    # plot legend
    ax1.legend(loc=1, fontsize=labelsize - 2, frameon=False)

    # make top and right boxlines invisible
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # plot text 'A'
    ax1.text(-0.13, 1, 'A', fontsize=labelsize + 5, transform=ax1.transAxes)


    ######## subplot 2: box plot over computation times
    first_set = []
    second_set = []
    third_set = []
    fourth_set = []
    fifth_set = []
    sixth_set = []
    seventh_set = []
    for iDataFrame in range(0, len(all_intern_columns)):
        if iDataFrame in [0, 7, 14, 21, 28]:
            first_set.append(list(all_intern_columns[iDataFrame]['simulation_time']))
        elif iDataFrame in [1, 8, 15, 22, 29]:
            second_set.append(list(all_intern_columns[iDataFrame]['simulation_time']))
        elif iDataFrame in [2, 9, 16, 23, 30]:
            third_set.append(list(all_intern_columns[iDataFrame]['simulation_time']))
        elif iDataFrame in [3, 10, 17, 24, 31]:
            fourth_set.append(list(all_intern_columns[iDataFrame]['simulation_time']))
        elif iDataFrame in [4, 11, 18, 25, 32]:
            fifth_set.append(list(all_intern_columns[iDataFrame]['simulation_time']))
        elif iDataFrame in [5, 12, 19, 26, 33]:
            sixth_set.append(list(all_intern_columns[iDataFrame]['simulation_time']))
        elif iDataFrame in [6, 13, 20, 27, 34]:
            seventh_set.append(list(all_intern_columns[iDataFrame]['simulation_time']))

    # get all elements in one list and add empty spaces to enhance clarity
    total_data = first_set + [[]] + second_set + [[]] + third_set + [[]] +  fourth_set + [[]] + fifth_set + [[]] + sixth_set + [[]] + seventh_set

    # plot boxplot
    bp = ax2.boxplot(total_data, sym='+', widths=0.5, patch_artist=True, positions=range(1, 42))

    # set more options
    ax2.set_yscale('log')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.set_ylim([0.2, 100000])

    # change colour for each set
    color1 = '#d73027'
    color2 = '#fc8d59'
    color3 = '#fee090'
    color4 = '#91bfdb'
    color5 = '#4575b4'

    colors = [color1, color2, color3, color4, color5, 'white', color1, color2, color3, color4, color5, 'white',
              color1, color2, color3, color4, color5, 'white', color1, color2, color3, color4, color5, 'white',
              color1, color2, color3, color4, color5, 'white', color1, color2, color3, color4, color5, 'white',
              color1, color2, color3, color4, color5]

    # for bplot in bp:
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
    for whisker in bp['whiskers']:
        whisker.set(color='#7570b3', linewidth=1)
    for cap in bp['caps']:
        cap.set(color='#7570b3', linewidth=1)
    for median in bp['medians']:
        median.set(color='black', linewidth=2)
    for flier in bp['fliers']:
        flier.set(marker='+', color='#e7298a', alpha=0.5, markersize=3)

    ax2.tick_params(labelsize=labelsize)
    ax2.set_xticklabels([])
    ax2.set_xlim([0, 42])
    specific_xticks = ax2.xaxis.get_major_ticks()

    # create major and minor ticklabels
    Abs_xTickLabels = ['', '', '', r'$10^{-6}$', '', '',
                       '', '', '', r'$10^{-8}$', '', '',
                       '', '', '', r'$10^{-8}$', '', '',
                       '', '', '', r'$10^{-10}$', '', '',
                       '', '', '', r'$10^{-12}$', '', '',
                       '', '', '', r'$10^{-14}$', '', '',
                       '', '', '', r'$10^{-16}$', '', '']
    Rel_xTickLabels = ['', '', '', r'$10^{-8}$', '', '',
                       '', '', '', r'$10^{-6}$', '', '',
                       '', '', '', r'$10^{-16}$', '', '',
                       '', '', '', r'$10^{-12}$', '', '',
                       '', '', '', r'$10^{-10}$', '', '',
                       '', '', '', r'$10^{-14}$', '', '',
                       '', '', '', r'$10^{-8}$', '', '']

    ax2.set_xticks(list(range(42)))
    minor_list_1 = [x + 0.001 for x in list(range(42))]
    ax2.set_xticks(minor_list_1, minor=True)
    ax2.set_xticklabels(Abs_xTickLabels, fontsize=labelsize)
    ax2.set_xticklabels(Rel_xTickLabels, minor=True, fontsize=labelsize)
    ax2.tick_params(axis='x', which='major', pad=5)
    ax2.tick_params(axis='x', which='minor', pad=20)
    ax2.text(-0.1, -0.05, 'Abs. tol.: ', fontsize=labelsize, transform=ax2.transAxes)
    ax2.text(-0.1, -0.10, 'Rel. tol.: ', fontsize=labelsize, transform=ax2.transAxes)
    specific_xticks_major = ax2.xaxis.get_major_ticks()
    for iTick in range(1,42):
        specific_xticks_major[iTick].set_visible(False)
    for iTick in [3, 9, 15, 21, 27, 33, 39]:
        specific_xticks_major[iTick].set_visible(True)
    specific_xticks_minor = ax2.xaxis.get_minor_ticks()
    for iTick in range(1,42):
        specific_xticks_minor[iTick].set_visible(False)
    for iTick in [3, 9, 15, 21, 27, 33, 39]:
        specific_xticks_minor[iTick].set_visible(True)

    # plot text 'B'
    ax2.text(-0.13, 1, 'B', fontsize=labelsize + 5, transform=ax2.transAxes)


########## call both functions + some global properties
LinearSolver('1','2')

# better layout
plt.tight_layout()

# change plotting size
fig = plt.gcf()
fig.set_size_inches(18.5, 10.5)

# show figure
plt.show()
