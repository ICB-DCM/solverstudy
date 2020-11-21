import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from C import (
    DIR_RESULTS_TOLERANCES, LINSOL_IDS, NONLINSOL_IDS, SOLALG_IDS,
    DIR_FIGURES, ATOLS_ALL, RTOLS_ALL)

n_atol = len(ATOLS_ALL)
n_rtol = len(RTOLS_ALL)

# Figure object
fig, axes = plt.subplots(nrows=n_atol, ncols=n_rtol, figsize=(15, 12))
fontsize = 15
labelsize = 12
alpha = 0.7
marker_size = 2

# Get failure rates and simulation times
failures = {}
times = {}
for atol in ATOLS_ALL:
    for rtol in RTOLS_ALL:
        f = os.path.join(
            DIR_RESULTS_TOLERANCES,
            f"atol_{atol}__rtol_{rtol}__linSol_{LINSOL_IDS['KLU']}" \
            f"__nonlinSol_{NONLINSOL_IDS['Newton-type']}" \
            f"__solAlg_{SOLALG_IDS['BDF']}.tsv")
        # Read in and sort
        df = pd.read_csv(f, sep='\t', index_col=0).sort_index()
        failure_rate = 100 * sum(df['failure']) / df.shape[0]
        failures[(atol, rtol)] = failure_rate
        times[(atol, rtol)] = np.array(df['median_intern'])

# Normalize simulation times by (1e-6, 1e-6)
ref_tol = ('1e-6', '1e-6')
for atol in ATOLS_ALL:
    for rtol in RTOLS_ALL:
        if (atol, rtol) != ('1e-6', '1e-6'):
            times[(atol, rtol)] /= times[ref_tol]
times[ref_tol] /= times[ref_tol]

# x bounds
xmin = min(np.nanmin(times[(atol, rtol)])
           for rtol in RTOLS_ALL for atol in ATOLS_ALL)
xmax = max(np.nanmax(times[(atol, rtol)])
           for rtol in RTOLS_ALL for atol in ATOLS_ALL)
# For same-width bins on log-scale
bins = np.logspace(np.log10(xmin), np.log10(xmax), num=20, base=10)

a_labels = [f'$10^{{{tol.split("e")[1]}}}$' for tol in ATOLS_ALL]
r_labels = [f'$10^{{{tol.split("e")[1]}}}$' for tol in RTOLS_ALL]

for i_atol, atol in enumerate(ATOLS_ALL):
    for i_rtol, rtol in enumerate(RTOLS_ALL):
        # Note: the the first coordinate is y, the second coordinate is x
        ax = axes[i_atol, i_rtol]

        # Histogram
        ax.hist(times[(atol, rtol)], bins=bins, color='#c0c0c0')

        # Failure rate
        ax.text(0.9, 0.9, f"{failures[(atol, rtol)]:.1f}%",
                ha='right', va='top', transform=ax.transAxes,
                fontsize=fontsize)

        # Axes decorations
        ax.set_xlim([xmin, xmax])
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.tick_params(labelsize=labelsize)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        if i_rtol > 0:
            ax.set_yticks([])
        else:
            ax.set_ylabel(a_labels[i_atol], fontsize=fontsize)
        if i_atol < n_atol - 1:
            ax.set_xticks([])
        if i_atol == 0:
            ax.set_xlabel(r_labels[i_rtol], fontsize=fontsize)
            ax.xaxis.set_label_position('top')

# Get extreme y bounds, ignoring 1e-6, 1e-6 for max
ymin = min(ax.get_ylim()[0] for ax in axes.flatten())
ymax = max(ax.get_ylim()[1] for ax in axes.flatten()[1:])

# Apply maximum to all
for ax in axes.flatten():
    ax.set_ylim([ymin, ymax])

# Labels
fig.text(0.5, 0.01, "Relative simulation time", ha='center', va='center',
         fontsize=fontsize+3)
fig.text(0.01, 0.5, "Number of models", ha='center', va='center',
         rotation='vertical', fontsize=fontsize+3)

fig.text(0.5, 0.97, "Rel. tol.", ha='center', va='center',
         fontsize=fontsize)
fig.text(0.03, 0.5, "Abs. tol.", rotation='vertical', ha='center', va='center',
         fontsize=fontsize)

# Condense layout
plt.tight_layout(rect=[0.03, 0.03, 0.97, 0.97])

# Save plot
os.makedirs(DIR_FIGURES, exist_ok=True)
plt.savefig(os.path.join(DIR_FIGURES, "Tolerances_Supp.pdf"))
plt.savefig(os.path.join(DIR_FIGURES, "Tolerances_Supp.png"), dpi=300)

#plt.show()
