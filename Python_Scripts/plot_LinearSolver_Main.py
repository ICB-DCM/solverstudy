import os
import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt

from C import (
    DIR_RESULTS_ALGORITHMS, LINSOL_DCT, ATOL_RTOLS, DIR_FIGURES)
from util import (
    solalg_from_fname, nonlinsol_from_fname, linsol_from_fname,
    atol_from_fname, rtol_from_fname)


# Solver algorithm
sol_alg = '2'
non_lin_sol = '2'

# Sub-select files for solver algorithm and non-linear solver
# And remove (1e-6, 1e-6) tolerance combination
files = [f for f in os.listdir(DIR_RESULTS_ALGORITHMS)
         if solalg_from_fname(f) == sol_alg and
         nonlinsol_from_fname(f) == non_lin_sol and
         ((atol_from_fname(f), rtol_from_fname(f)) in ATOL_RTOLS)]

# Extract times and numbers of state variables
times = []
states = []
for f in files:
    df = pd.read_csv(os.path.join(DIR_RESULTS_ALGORITHMS, f), sep='\t')
    times.append(df['median_intern'])
    states.append(df['n_species'])

# Figure object
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12, 10))
fontsize = 15
labelsize = 12
lettersize = 20
alpha = 0.7
marker_size = 2

###############################################################################
# Scatter plot of all data points with color coding and linear regression
#  by the linear solver

ax = axes.flatten()[0]

# Plot layout
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Number of state variables', fontsize=fontsize)
ax.set_ylabel('Simulation time [ms]', fontsize=fontsize)
ax.tick_params(labelsize=labelsize)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Group by linear solver
times_for_linsol = {}
states_for_linsol = {}
for f, time, state in zip(files, times, states):
    linsol = int(linsol_from_fname(f))
    times_for_linsol.setdefault(linsol, []).extend(list(time * 1000))
    states_for_linsol.setdefault(linsol, []).extend(list(state))

# To numpy
for linsol in LINSOL_DCT:
    times_for_linsol[linsol] = np.asarray(times_for_linsol[linsol])
    states_for_linsol[linsol] = np.asarray(states_for_linsol[linsol])

# Linear regression in log10 space (for both variables)
#  Tuples of slope, intercept, minimum and maximum considered value
reg_for_linsol = {}
for linsol in LINSOL_DCT:
    _states = states_for_linsol[linsol]
    _times = times_for_linsol[linsol]
    nan_mask = ~np.isnan(_states) & ~np.isnan(_times)
    slope, intercept, _, _, _ = \
        stats.linregress(np.log10(_states[nan_mask]),
                         np.log10(_times[nan_mask]))
    reg_for_linsol[linsol] = \
        slope, intercept, min(_states[nan_mask]), max(_states[nan_mask])

# Colors
colors_lin_sol = {1: '#d73027', 6: '#fc8d59', 7: '#fee090', 8: '#91bfdb',
                  9: '#4575b4'}
colors_lin_sol_arr = [colors_lin_sol[linsol] for linsol in LINSOL_DCT]

# Plot
for linsol in LINSOL_DCT:
    # Value scatter plot
    ax.scatter(states_for_linsol[linsol], times_for_linsol[linsol],
               # label=LINSOL_DCT[linsol],
               alpha=alpha, c=colors_lin_sol[linsol], s=marker_size)
    # Regression line (transformed from log10 to linear space)
    grad, intercept, min_state, max_state = reg_for_linsol[linsol]
    uq_states = np.sort(np.unique(states_for_linsol[linsol]))
    ax.plot([min_state, max_state],
            10 ** (intercept + grad * np.log10([min_state, max_state])),
            c=colors_lin_sol[linsol],
            label=f'{LINSOL_DCT[linsol]}: slope = {np.round(grad, 4)}')

# Legend (same for both plots)
ax.legend(loc=0, fontsize=labelsize - 1, frameon=False)

# Axis bounds
xmin = min(np.nanmin(states_for_linsol[linsol]) for linsol in LINSOL_DCT)
xmax = max(np.nanmax(states_for_linsol[linsol]) for linsol in LINSOL_DCT)
ax.set_xlim([xmin/1.3, xmax*1.3])
ymin = min(np.nanmin(times_for_linsol[linsol]) for linsol in LINSOL_DCT)
ymax = max(np.nanmax(times_for_linsol[linsol]) for linsol in LINSOL_DCT)
ax.set_ylim([ymin * 0.5, ymax*2])

# Plot text 'A'
ax.text(-0.13, 1, 'A', fontsize=lettersize, transform=ax.transAxes)

###############################################################################
# Box plot of computation times, colored by linear solver, separated by
#  tolerances

# Configure axes
ax = axes.flatten()[1]
ax.set_yscale('log')
ax.tick_params(labelsize=labelsize)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Group by tolerances, and then linear solver
times_for_linsol_atolrtol = {}
for f, time in zip(files, times):
    linsol = int(linsol_from_fname(f))
    atol = atol_from_fname(f)
    rtol = rtol_from_fname(f)
    times_for_linsol_atolrtol.setdefault(linsol, {}).\
        setdefault((atol, rtol), []).extend(list(time*1000))

# To dict of lists, in correct order
for linsol, vals in times_for_linsol_atolrtol.items():
    times_for_linsol_atolrtol[linsol] = \
        np.asarray([vals[atolrtol] for atolrtol in ATOL_RTOLS])

n_tol = len(ATOL_RTOLS)
n_linsol = len(LINSOL_DCT)

for i_linsol, linsol in enumerate(LINSOL_DCT.keys()):
    vals = times_for_linsol_atolrtol[linsol]
    # remove nans
    vals = [val[~np.isnan(val)] for val in vals]
    # Plot boxplot for the given linear solver
    bp = ax.boxplot(
        vals,
        positions=np.arange(n_tol) + (i_linsol+1) / (n_linsol+1) - 0.5,
        sym="+", widths=0.1, patch_artist=True)
    # Prettify plot
    for patch in bp['boxes']:
        patch.set_facecolor(colors_lin_sol[linsol])
    for whisker in bp['whiskers']:
        whisker.set(color='#7570b3', linewidth=1)
    for cap in bp['caps']:
        cap.set(color='#7570b3', linewidth=1)
    for median in bp['medians']:
        median.set(color='black', linewidth=2)
    for flier in bp['fliers']:
        flier.set(marker='+', color='#e7298a', alpha=alpha, markersize=3)

# x axis labels
x_ticks = np.arange(n_tol)

a_labels = [f'$10^{{{tol[0].split("e")[1]}}}$' for tol in ATOL_RTOLS]
r_labels = [f'$10^{{{tol[1].split("e")[1]}}}$' for tol in ATOL_RTOLS]

# An alternative way of generating the x axis labels
#ax.set_xticks(x_ticks)
#ax.set_xticks(x_ticks+0.001, minor=True)
#ax.set_xticklabels(a_labels, fontsize=labelsize)
#ax.set_xticklabels(r_labels, fontsize=labelsize, minor=True)
#for ticklabel in ax.get_xticklabels(minor=False):
#    ticklabel.set_y(-0.01)
#for ticklabel in ax.get_xticklabels(minor=True):
#    ticklabel.set_y(-0.06)
#ax.text(-0.07, -0.058, 'Abs. tol.:', fontsize=labelsize,
#        transform=ax.transAxes)
#ax.text(-0.07, -0.10, 'Rel. tol.:', fontsize=labelsize,
#        transform=ax.transAxes)

# Axis limits
ax.set_ylim([ymin * 0.5, ymax*2])
ax.set_xlim([-0.5, n_tol - 0.5])

ax.set_xticks(x_ticks)
ax.set_xticklabels([])
for i_tol, (a_label, r_label) in enumerate(zip(a_labels, r_labels)):
    ax.text((i_tol+0.5) / (n_tol), -0.08, a_label, fontsize=labelsize,
            transform=ax.transAxes,
            horizontalalignment='center', verticalalignment='bottom')
    ax.text((i_tol+0.5) / (n_tol), -0.13, r_label, fontsize=labelsize,
            transform=ax.transAxes,
            horizontalalignment='center', verticalalignment='bottom')
ax.text(-0.13, -0.08, 'Abs. tol.:', fontsize=labelsize, transform=ax.transAxes,
        verticalalignment='bottom')
ax.text(-0.13, -0.13, 'Rel. tol.:',  fontsize=labelsize, transform=ax.transAxes,
        verticalalignment='bottom')

# Plot text 'B'
ax.text(-0.13, 1, 'B', fontsize=lettersize, transform=ax.transAxes)

###############################################################################
###############################################################################
# Lower part featuring Copasi

# Solver algorithm
non_lin_sol = '2'

# Sub-select files for solver algorithm and non-linear solver
# And remove (1e-6, 1e-6) tolerance combination
files = [f for f in os.listdir(DIR_RESULTS_ALGORITHMS)
         if (solalg_from_fname(f) in ['1', '2'] and
         linsol_from_fname(f) in ['1', '9'] and
         nonlinsol_from_fname(f) == non_lin_sol and
         ((atol_from_fname(f), rtol_from_fname(f)) in ATOL_RTOLS)) or (
         solalg_from_fname(f) == '3' and
         ((atol_from_fname(f), rtol_from_fname(f)) in ATOL_RTOLS))]

# Extract times and numbers of state variables
times = []
states = []
for f in files:
    df = pd.read_csv(os.path.join(DIR_RESULTS_ALGORITHMS, f), sep='\t')
    times.append(df['median_intern'])
    states.append(df['n_species'])

solver_dct = {
    11: 'AM, Dense',
    12: 'BDF, Dense',
    13: 'AM, KLU',
    14: 'BDF, KLU',
    15: 'LSODA'
}

for i_f, f in enumerate(files):
    if solalg_from_fname(f) == '1' and linsol_from_fname(f) == '1':
        files[i_f] = f.replace("linSol_1", "linSol_11")
    elif solalg_from_fname(f) == '2' and linsol_from_fname(f) == '1':
        files[i_f] = f.replace("linSol_1", "linSol_12")
    elif solalg_from_fname(f) == '1' and linsol_from_fname(f) == '9':
        files[i_f] = f.replace("linSol_9", "linSol_13")
    elif solalg_from_fname(f) == '2' and linsol_from_fname(f) == '9':
        files[i_f] = f.replace("linSol_9", "linSol_14")
    elif solalg_from_fname(f) == '3' and linsol_from_fname(f) == '1':
        files[i_f] = f.replace("linSol_1", "linSol_15")
    else:
        raise ValueError("Unexpected result file")


###############################################################################
# Scatter plot of all data points with color coding and linear regression
#  by the linear solver

ax = axes.flatten()[2]

# Plot layout
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Number of state variables', fontsize=fontsize)
ax.set_ylabel('Simulation time [ms]', fontsize=fontsize)
ax.tick_params(labelsize=labelsize)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Group by linear solver
times_for_linsol = {}
states_for_linsol = {}
for f, time, state in zip(files, times, states):
    linsol = int(linsol_from_fname(f))
    times_for_linsol.setdefault(linsol, []).extend(list(time * 1000))
    states_for_linsol.setdefault(linsol, []).extend(list(state))

# To numpy
for linsol in solver_dct:
    times_for_linsol[linsol] = np.asarray(times_for_linsol[linsol])
    states_for_linsol[linsol] = np.asarray(states_for_linsol[linsol])

# Linear regression in log10 space (for both variables)
#  Tuples of slope, intercept, minimum and maximum considered value
reg_for_linsol = {}
for linsol in solver_dct:
    _states = states_for_linsol[linsol]
    _times = times_for_linsol[linsol]
    nan_mask = ~np.isnan(_states) & ~np.isnan(_times)
    slope, intercept, _, _, _ = \
        stats.linregress(np.log10(_states[nan_mask]),
                         np.log10(_times[nan_mask]))
    reg_for_linsol[linsol] = \
        slope, intercept, min(_states[nan_mask]), max(_states[nan_mask])

# Colors
colors_lin_sol = {11: '#fc8d59', 12: '#d73027', 13: '#91bfdb',
                  14: '#4575b4', 15: '#838282'}
colors_lin_sol_arr = [colors_lin_sol[linsol] for linsol in solver_dct]

# Plot
for linsol in solver_dct:
    # Value scatter plot
    ax.scatter(states_for_linsol[linsol], times_for_linsol[linsol],
               # label=solver_dct[linsol],
               alpha=alpha, c=colors_lin_sol[linsol], s=marker_size)
    # Regression line (transformed from log10 to linear space)
    grad, intercept, min_state, max_state = reg_for_linsol[linsol]
    uq_states = np.sort(np.unique(states_for_linsol[linsol]))
    ax.plot([min_state, max_state],
            10 ** (intercept + grad * np.log10([min_state, max_state])),
            c=colors_lin_sol[linsol],
            label=f'{solver_dct[linsol]}: slope = {np.round(grad, 4)}')

# Legend (same for both plots)
ax.legend(loc=0, fontsize=labelsize - 1, frameon=False)

# Axis bounds
xmin = min(np.nanmin(states_for_linsol[linsol]) for linsol in solver_dct)
xmax = max(np.nanmax(states_for_linsol[linsol]) for linsol in solver_dct)
ax.set_xlim([xmin/1.3, xmax*1.3])
ymin = min(np.nanmin(times_for_linsol[linsol]) for linsol in solver_dct)
ymax = max(np.nanmax(times_for_linsol[linsol]) for linsol in solver_dct)
ax.set_ylim([ymin * 0.5, ymax*2])

# Plot text 'C'
ax.text(-0.13, 1, 'C', fontsize=lettersize, transform=ax.transAxes)

###############################################################################
# Box plot of computation times, colored by linear solver, separated by
#  tolerances

# Configure axes
ax = axes.flatten()[3]
ax.set_yscale('log')
ax.tick_params(labelsize=labelsize)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Group by tolerances, and then linear solver
times_for_linsol_atolrtol = {}
for f, time in zip(files, times):
    linsol = int(linsol_from_fname(f))
    atol = atol_from_fname(f)
    rtol = rtol_from_fname(f)
    times_for_linsol_atolrtol.setdefault(linsol, {}).\
        setdefault((atol, rtol), []).extend(list(time*1000))

# To dict of lists
for linsol, vals in times_for_linsol_atolrtol.items():
    times_for_linsol_atolrtol[linsol] = \
        np.asarray([vals[atolrtol] for atolrtol in ATOL_RTOLS])

n_tol = len(ATOL_RTOLS)
n_linsol = len(solver_dct)

for i_linsol, linsol in enumerate(solver_dct.keys()):
    vals = times_for_linsol_atolrtol[linsol]
    # remove nans
    vals = [val[~np.isnan(val)] for val in vals]
    # Plot boxplot for the given linear solver
    bp = ax.boxplot(
        vals,
        positions=np.arange(n_tol) + (i_linsol+1) / (n_linsol+1) - 0.5,
        sym="+", widths=0.1, patch_artist=True)
    # Prettify plot
    for patch in bp['boxes']:
        patch.set_facecolor(colors_lin_sol[linsol])
    for whisker in bp['whiskers']:
        whisker.set(color='#7570b3', linewidth=1)
    for cap in bp['caps']:
        cap.set(color='#7570b3', linewidth=1)
    for median in bp['medians']:
        median.set(color='black', linewidth=2)
    for flier in bp['fliers']:
        flier.set(marker='+', color='#e7298a', alpha=alpha, markersize=3)

# x axis labels
x_ticks = np.arange(n_tol)

a_labels = [f'$10^{{{tol[0].split("e")[1]}}}$' for tol in ATOL_RTOLS]
r_labels = [f'$10^{{{tol[1].split("e")[1]}}}$' for tol in ATOL_RTOLS]

# Axis limits
ax.set_ylim([ymin * 0.5, ymax*2])
ax.set_xlim([-0.5, n_tol - 0.5])

ax.set_xticks(x_ticks)
ax.set_xticklabels([])
for i_tol, (a_label, r_label) in enumerate(zip(a_labels, r_labels)):
    ax.text((i_tol+0.5) / (n_tol), -0.08, a_label, fontsize=labelsize,
            transform=ax.transAxes,
            horizontalalignment='center', verticalalignment='bottom')
    ax.text((i_tol+0.5) / (n_tol), -0.13, r_label, fontsize=labelsize,
            transform=ax.transAxes,
            horizontalalignment='center', verticalalignment='bottom')
ax.text(-0.13, -0.08, 'Abs. tol.:', fontsize=labelsize, transform=ax.transAxes,
        verticalalignment='bottom')
ax.text(-0.13, -0.13, 'Rel. tol.:',  fontsize=labelsize, transform=ax.transAxes,
        verticalalignment='bottom')

# Plot text 'D'
ax.text(-0.13, 1, 'D', fontsize=lettersize, transform=ax.transAxes)

###############################################################################
# Finishing

# Same y lims
ymax = max(ax.get_ylim()[1] for ax in axes.flatten())
ymin = min(ax.get_ylim()[0] for ax in axes.flatten())
for ax in axes.flatten():
    ax.set_ylim([ymin, ymax])

# Condense layout
plt.tight_layout()

# Save plot
os.makedirs(DIR_FIGURES, exist_ok=True)
plt.savefig(os.path.join(DIR_FIGURES, "LinearSolver_Main.pdf"))
plt.savefig(os.path.join(DIR_FIGURES, "LinearSolver_Main.png"), dpi=300)

#plt.show()
