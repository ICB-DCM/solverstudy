import os
import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt

from C import (
    DIR_RESULTS_ALGORITHMS, LINSOL_DCT, LINSOL_IDS, NONLINSOL_IDS, SOLALG_IDS,
    ATOL_RTOLS, DIR_FIGURES)

# Figure object
fig, axes = plt.subplots(nrows=4, ncols=2, figsize=(12, 8))
fontsize = 12
labelsize = 8
alpha = 0.7
marker_size = 2

# Mock Copasi LSODA
LINSOL_DCT[42] = 'LSODA'

# Get simulation times and states
times = {}
states = {}
failures = {}
for atol, rtol in ATOL_RTOLS:
    for linsol in LINSOL_DCT:
        if linsol == 42:
            # Copasi
            f = os.path.join(
                DIR_RESULTS_ALGORITHMS,
                f"atol_{atol}__rtol_{rtol}__linSol_1" \
                f"__nonlinSol_{NONLINSOL_IDS['Newton-type']}" \
                f"__solAlg_3.tsv")
        else:
            f = os.path.join(
                DIR_RESULTS_ALGORITHMS,
                f"atol_{atol}__rtol_{rtol}__linSol_{linsol}" \
                f"__nonlinSol_{NONLINSOL_IDS['Newton-type']}" \
                f"__solAlg_{SOLALG_IDS['BDF']}.tsv")
        df = pd.read_csv(f, sep='\t', index_col=0).sort_index()
        times.setdefault((atol, rtol), {})[linsol] = \
            1000 * np.array(df['median_intern'])
        states.setdefault((atol, rtol), {})[linsol] = \
            np.array(df['n_species'])
        failures.setdefault((atol, rtol), {})[linsol] = \
            100 * sum(df['failure']) / df.shape[0]

# Colors
colors = {1: '#d73027', 6: '#fc8d59', 7: '#fee090', 8: '#91bfdb', 9: '#4575b4',
          42: '#9e9e9e'}

# Tolerance labels
tol_labels = [(f'$10^{{{atol.split("e")[1]}}}$',
               f'$10^{{{rtol.split("e")[1]}}}$')
               for atol, rtol in ATOL_RTOLS]

###############################################################################
# States vs times scatter plots

# Minimal and maximal values
xmin = min(np.nanmin(states[(atol, rtol)][linsol])
           for linsol in LINSOL_DCT for atol, rtol in ATOL_RTOLS)
xmax = max(np.nanmax(states[(atol, rtol)][linsol])
           for linsol in LINSOL_DCT for atol, rtol in ATOL_RTOLS)
ymin = min(np.nanmin(times[(atol, rtol)][linsol])
           for linsol in LINSOL_DCT for atol, rtol in ATOL_RTOLS)
ymax = max(np.nanmax(times[(atol, rtol)][linsol])
           for linsol in LINSOL_DCT for atol, rtol in ATOL_RTOLS)

# Plot
for ix, (ax, (atol, rtol)) in enumerate(zip(axes.flatten()[:-1], ATOL_RTOLS)):
    for linsol in LINSOL_DCT:
        xs = states[(atol, rtol)][linsol]
        ys = times[(atol, rtol)][linsol]
        ax.scatter(xs, ys, alpha=alpha, c=colors[linsol], s=marker_size)

        # Compute linear regression curve
        nan_mask = ~np.isnan(xs) & ~np.isnan(ys)
        slope, intercept, _, _, _ = stats.linregress(
            np.log10(xs[nan_mask]), np.log10(ys[nan_mask]))
        range = [min(xs[nan_mask]), max(xs[nan_mask])]
        ax.plot(range,
                10 ** (intercept + slope * np.log10(range)),
                c=colors[linsol],
                label=f'{LINSOL_DCT[linsol]}')

    # Decorations
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim([xmin/1.3, xmax*1.3])
    ax.set_ylim([ymin*0.5, ymax*2])
    atol_lb, rtol_lb = tol_labels[ix]
    ax.set_title(f"Abs. tol = {atol_lb}, Rel. tol = {rtol_lb}",
                 fontsize=labelsize + 1)
    if ix % 2 == 0:
        ax.set_ylabel("Simulation time [ms]")
    else:
        ax.set_yticklabels([])
    if ix < len(ATOL_RTOLS) - 2:
        ax.set_xticks([])

axes.flatten()[0].legend(loc='center', bbox_to_anchor=[1.05, 0.5],
                         fontsize=labelsize - 1, frameon=False)

###############################################################################
# Failure rate plot
ax = axes.flatten()[-1]
# To long
failures_arr = []
colors_arr = []
for atol, rtol in ATOL_RTOLS:
    for linsol in LINSOL_DCT:
        failures_arr.append(failures[(atol, rtol)][linsol])
        colors_arr.append(colors[linsol])
    failures_arr.append(np.nan)
    colors_arr.append('white')

# Decorations
n_tol = len(ATOL_RTOLS)
n_linsol = len(LINSOL_DCT)
xs = np.arange(len(failures_arr))
ax.bar(x=xs, height=failures_arr, color=colors_arr, width=0.5)
ax.set_ylabel("Failure rate [%]")
xticks = (n_linsol + 1) * np.arange(n_tol) + n_linsol / 2
ax.set_xticks(xticks)
ax.set_xticklabels([])

# x labels
for i_tol, (atol_lb, rtol_lb) in enumerate(tol_labels):
    x = (n_linsol + 1) * i_tol + n_linsol / 2
    ax.text(x, -7, atol_lb, fontsize=labelsize, transform=ax.transData,
            horizontalalignment='center', verticalalignment='bottom')
    ax.text(x, -11, rtol_lb, fontsize=labelsize, transform=ax.transData,
            horizontalalignment='center', verticalalignment='bottom')
ax.text(-6, -7, 'Abs. tol.:', fontsize=labelsize+1, transform=ax.transData,
        verticalalignment='bottom')
ax.text(-6, -11, 'Rel. tol.:',  fontsize=labelsize+1, transform=ax.transData,
        verticalalignment='bottom')

###############################################################################
# Finishing

# Decorations for all
for ax in axes.flatten():
    ax.tick_params(labelsize=labelsize)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# Condense layout
plt.tight_layout()

# Save plot
os.makedirs(DIR_FIGURES, exist_ok=True)
plt.savefig(os.path.join(DIR_FIGURES, "LinearSolver_Supp2.pdf"))
plt.savefig(os.path.join(DIR_FIGURES, "LinearSolver_Supp2.png"))

#plt.show()
