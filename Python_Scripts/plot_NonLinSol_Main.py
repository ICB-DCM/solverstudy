import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from C import (
    DIR_RESULTS_ALGORITHMS, LINSOL_DCT, ATOL_RTOLS, NONLINSOL_DCT, SOLALG_DCT,
    DIR_FIGURES)

# Figure object
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 5))
fontsize = 12
labelsize = 8

# Group by nonlinear solver and solver algorithm
failures = {}

for linsol in LINSOL_DCT:
    for atol, rtol in ATOL_RTOLS:
        for nonlinsol in NONLINSOL_DCT:
            for solalg in SOLALG_DCT:
                f = f"atol_{atol}__rtol_{rtol}__linSol_{linsol}" \
                    f"__nonlinSol_{nonlinsol}__solAlg_{solalg}.tsv"
                df = pd.read_csv(
                    os.path.join(DIR_RESULTS_ALGORITHMS, f), sep='\t')
                failures.setdefault(
                    (nonlinsol, solalg), []).append(
                        100 * sum(df['failure']) / df.shape[0])
    for key in failures:
        failures[key].append(np.nan)

# Translate to single arrays

colors = {
    (1, 1): '#fdb863', (1, 2): '#e66101',
    (2, 1): '#b2abd2', (2, 2): '#5e3c99'}

labels = {
    (1, 1): 'Functional AM', (1, 2): 'Functional BDF',
    (2, 1): 'Newton AM', (2, 2): 'Newton BDF'}

xs = np.arange(len(failures[(1, 1)]))

# Plot failure rates
for key in colors:
    ax.plot(xs, failures[key], 'x-',
            color=colors[key], label=labels[key])

# Variables
ymax = max(np.nanmax(failures[key]) for key in failures) + 1
n_linsol = len(LINSOL_DCT)
n_tol = len(ATOL_RTOLS)

# Plot separation line
for x in n_tol + np.arange(n_linsol-1) * (n_tol+1):
    ax.plot([x, x], [0, ymax], '--k', linewidth=1)

# x axis labels
x_ticks = xs[~np.isnan(failures[(1, 1)])]
ax.set_xticks(x_ticks)
ax.set_xticklabels([])

a_labels = [f'$10^{{{tol[0].split("e")[1]}}}$' for tol in ATOL_RTOLS]
r_labels = [f'$10^{{{tol[1].split("e")[1]}}}$' for tol in ATOL_RTOLS]

for i_linsol, linsol in enumerate(LINSOL_DCT):
    ax.text(i_linsol*(n_tol+1) + 3, -3, LINSOL_DCT[linsol], fontsize=labelsize,
            transform=ax.transData,
            horizontalalignment='center', verticalalignment='center')
    for i_tol, (a_label, r_label) in enumerate(zip(a_labels, r_labels)):
        ax.text(i_linsol*(n_tol+1) + i_tol, -6.5, a_label, fontsize=labelsize,
                transform=ax.transData, rotation=45,
                horizontalalignment='center', verticalalignment='center')
        ax.text(i_linsol*(n_tol+1) + i_tol, -10, r_label, fontsize=labelsize,
                transform=ax.transData, rotation=45,
                horizontalalignment='center', verticalalignment='center')
ax.text(-3, -3, 'Lin. sol.:',
        horizontalalignment='center', verticalalignment='center')
ax.text(-3, -6.5, 'Abs. tol.:',
        horizontalalignment='center', verticalalignment='center')
ax.text(-3, -10, 'Rel. tol.:',
        horizontalalignment='center', verticalalignment='center')

# Legend
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.3),
          ncol=4, frameon=False, fontsize=fontsize)

# Decoration
ax.set_ylabel('Failure rate [%]', fontsize=fontsize)
ax.set_ylim([0, ymax])
ax.tick_params(labelsize=labelsize)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()

# Save plot
os.makedirs(DIR_FIGURES, exist_ok=True)
plt.savefig(os.path.join(DIR_FIGURES, "NonLinearSolver_Main.pdf"))
plt.savefig(os.path.join(DIR_FIGURES, "NonLinearSolver_Main.png"))

plt.show()
