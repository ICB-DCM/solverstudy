import os
import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt

from C import (
    DIR_RESULTS_ALGORITHMS, NONLINSOL_DCT, ATOL_RTOLS, DIR_FIGURES)
from util import (
    solalg_from_fname, nonlinsol_from_fname, linsol_from_fname,
    atol_from_fname, rtol_from_fname)


solalg = '2'  # AM
linsol = '9'  # KLU

# Sub-select files for solver algorithm and non-linear solver
# And remove (1e-6, 1e-6) tolerance combination
files = [f for f in os.listdir(DIR_RESULTS_ALGORITHMS)
         if solalg_from_fname(f) == solalg and
         linsol_from_fname(f) == linsol and
         nonlinsol_from_fname(f) in ['1', '2'] and
         ((atol_from_fname(f), rtol_from_fname(f)) in ATOL_RTOLS)]

# Extract times and numbers of state variables
times = []
states = []
for f in files:
    df = pd.read_csv(os.path.join(DIR_RESULTS_ALGORITHMS, f), sep='\t')
    times.append(df['median_intern'])
    states.append(df['n_species'])

# Figure object
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 5))
fontsize = 15
labelsize = 12
lettersize = 20
alpha = 0.7
marker_size = 2

###############################################################################
# Scatter plot of all data points with color coding and linear regression
#  by the linear solver

ax = axes[0]

# Plot layout
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Number of state variables', fontsize=fontsize)
ax.set_ylabel('Simulation time [ms]', fontsize=fontsize)
ax.tick_params(labelsize=labelsize)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Group by linear solver
times_for_nonlinsol = {}
states_for_nonlinsol = {}
for f, time, state in zip(files, times, states):
    nonlinsol = int(nonlinsol_from_fname(f))
    times_for_nonlinsol.setdefault(nonlinsol, []).extend(list(time * 1000))
    states_for_nonlinsol.setdefault(nonlinsol, []).extend(list(state))

# To numpy
for nonlinsol in NONLINSOL_DCT:
    times_for_nonlinsol[nonlinsol] = np.asarray(times_for_nonlinsol[nonlinsol])
    states_for_nonlinsol[nonlinsol] = np.asarray(states_for_nonlinsol[nonlinsol])

# Linear regression in log10 space (for both variables)
#  Tuples of slope, intercept, minimum and maximum considered value
reg_for_nonlinsol = {}
for nonlinsol in NONLINSOL_DCT:
    _states = states_for_nonlinsol[nonlinsol]
    _times = times_for_nonlinsol[nonlinsol]
    nan_mask = ~np.isnan(_states) & ~np.isnan(_times)
    slope, intercept, _, _, _ = \
        stats.linregress(np.log10(_states[nan_mask]),
                         np.log10(_times[nan_mask]))
    reg_for_nonlinsol[nonlinsol] = \
        slope, intercept, min(_states[nan_mask]), max(_states[nan_mask])

# Colors
colors_nonlinsol = {1: '#e66101', 2: '#5e3c99'}

# Plot
for nonlinsol in NONLINSOL_DCT:
    # Value scatter plot
    ax.scatter(states_for_nonlinsol[nonlinsol], times_for_nonlinsol[nonlinsol],
               # label=solver_dct[nonlinsol],
               alpha=alpha, c=colors_nonlinsol[nonlinsol], s=marker_size)
    # Regression line (transformed from log10 to linear space)
    grad, intercept, min_state, max_state = reg_for_nonlinsol[nonlinsol]
    uq_states = np.sort(np.unique(states_for_nonlinsol[nonlinsol]))
    ax.plot([min_state, max_state],
            10 ** (intercept + grad * np.log10([min_state, max_state])),
            c=colors_nonlinsol[nonlinsol],
            label=f'{NONLINSOL_DCT[nonlinsol]}: slope = {np.round(grad, 4)}')

# Legend (same for both plots)
ax.legend(loc=0, fontsize=labelsize - 1, frameon=False)

# Axis bounds
xmin = min(np.nanmin(states_for_nonlinsol[nonlinsol]) for nonlinsol in NONLINSOL_DCT)
xmax = max(np.nanmax(states_for_nonlinsol[nonlinsol]) for nonlinsol in NONLINSOL_DCT)
ax.set_xlim([xmin/1.3, xmax*1.3])
ymin = min(np.nanmin(times_for_nonlinsol[nonlinsol]) for nonlinsol in NONLINSOL_DCT)
ymax = max(np.nanmax(times_for_nonlinsol[nonlinsol]) for nonlinsol in NONLINSOL_DCT)
ax.set_ylim([ymin * 0.5, ymax*2])

# Plot text 'A'
ax.text(-0.13, 1, 'A', fontsize=labelsize + 5, transform=ax.transAxes)

###############################################################################
# Box plot of computation times, colored by linear solver, separated by
#  tolerances

# Configure axes
ax = axes[1]
ax.set_yscale('log')
ax.tick_params(labelsize=labelsize)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Group by tolerances, and then nonlinear solver
times_for_nonlinsol_atolrtol = {}
for f, time in zip(files, times):
    nonlinsol = int(nonlinsol_from_fname(f))
    atol = atol_from_fname(f)
    rtol = rtol_from_fname(f)
    times_for_nonlinsol_atolrtol.setdefault(nonlinsol, {}).\
        setdefault((atol, rtol), []).extend(list(time*1000))

# To dict of lists
for nonlinsol, vals in times_for_nonlinsol_atolrtol.items():
    times_for_nonlinsol_atolrtol[nonlinsol] = \
        np.asarray([vals[atolrtol] for atolrtol in ATOL_RTOLS])

n_tol = len(ATOL_RTOLS)
n_nonlinsol = len(NONLINSOL_DCT)

for i_nonlinsol, nonlinsol in enumerate(NONLINSOL_DCT.keys()):
    vals = times_for_nonlinsol_atolrtol[nonlinsol]
    # remove nans
    vals = [val[~np.isnan(val)] for val in vals]
    # Plot boxplot for the given linear solver
    bp = ax.boxplot(
        vals,
        positions=np.arange(n_tol) + (i_nonlinsol+1) / (n_nonlinsol+1) - 0.5,
        sym="+", widths=0.1, patch_artist=True)
    # Prettify plot
    for patch in bp['boxes']:
        patch.set_facecolor(colors_nonlinsol[nonlinsol])
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

# Plot text 'B'
ax.text(-0.13, 1, 'B', fontsize=labelsize + 5, transform=ax.transAxes)

# Condense layout
plt.tight_layout()

# Save plot
os.makedirs(DIR_FIGURES, exist_ok=True)
plt.savefig(os.path.join(DIR_FIGURES, "NonLinearSolver_Supp.pdf"))
plt.savefig(os.path.join(DIR_FIGURES, "NonLinearSolver_Supp.png"), dpi=300)

#plt.show()