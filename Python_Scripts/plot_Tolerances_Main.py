import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from C import (
    DIR_RESULTS_TOLERANCES, LINSOL_IDS, NONLINSOL_IDS, SOLALG_IDS,
    DIR_FIGURES, ATOLS_ALL, RTOLS_ALL)

# Figure object
fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(12, 6))
fontsize = 12
labelsize = 8
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
        df = pd.read_csv(f, sep='\t')
        failure_rate = 100 * sum(df['failure']) / df.shape[0]
        failures[(atol, rtol)] = failure_rate
        times[(atol, rtol)] = np.array(df['median_intern'])

# Counters, same but whatever
n_atol = len(ATOLS_ALL)
n_rtol = len(RTOLS_ALL)

# x axis points
xs = np.arange(n_atol * n_rtol + (n_atol - 1))

# Absolute tolerance colors
colors = ['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854', '#ffd92f']

# Normalize simulation times by (1e-6, 1e-6)
ref_tol = ('1e-6', '1e-6')
for atol in ATOLS_ALL:
    for rtol in RTOLS_ALL:
        if (atol, rtol) != ('1e-6', '1e-6'):
            times[(atol, rtol)] /= times[ref_tol]
times[ref_tol] /= times[ref_tol]

# Flat arrays (last dimension expanded for times)
failures_flat = []
times_flat = []
colors_flat = []
for i_atol, atol in enumerate(ATOLS_ALL):
    for rtol in RTOLS_ALL:
        failures_flat.append(failures[(atol, rtol)])
        times_flat.append(times[(atol, rtol)][~np.isnan(times[(atol, rtol)])])
        colors_flat.append(colors[i_atol])
    # Empty
    if i_atol < n_atol - 1:
        failures_flat.append(np.nan)
        times_flat.append(np.array([]))
        colors_flat.append('white')

###############################################################################
# Figure 1: Simulation times box plot

ax = axes[0]

bp = ax.boxplot(
    times_flat,
    positions=xs,
    widths=0.5, patch_artist=True)
# Prettify plot
for patch, color in zip(bp['boxes'], colors_flat):
    patch.set_facecolor(color)
for whisker in bp['whiskers']:
    whisker.set(color='#7570b3', linewidth=1)
for cap in bp['caps']:
    cap.set(color='#7570b3', linewidth=1)
for median in bp['medians']:
    median.set(color='black', linewidth=2)
for flier in bp['fliers']:
    flier.set(marker='+', color='#e7298a', alpha=alpha, markersize=3)

# Decorations
ax.set_ylabel("Relative simulation time")
ax.set_yscale('log')
ax.tick_params(labelsize=labelsize)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ticks = xs[~np.isnan(failures_flat)]
ax.set_xticks(ticks)
ax.set_xticklabels([])
ax.set_xlim([-1, len(failures_flat)])
ax.yaxis.grid(True, linestyle='-', which='both', color='lightgrey', alpha=0.25)

# Plot text 'A'
ax.text(-0.05, 1, 'A', fontsize=fontsize + 3, transform=ax.transAxes)

###############################################################################
# Figure 2: Failure rates bar plot

ax = axes[1]

ax.bar(x=xs, height=failures_flat, color=colors_flat, width=0.5,
       edgecolor='black')

ax.set_ylabel("Failure rate [%]")
#ax.set_yscale('log')
ax.tick_params(labelsize=labelsize)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_xticks(ticks)
ax.set_xticklabels([])
ax.set_xlim([-1, len(failures_flat)])
ax.yaxis.grid(True, linestyle='-', which='both', color='lightgrey', alpha=0.25)

# x labels
a_labels = [f'$10^{{{tol.split("e")[1]}}}$' for tol in ATOLS_ALL]
r_labels = [f'$10^{{{tol.split("e")[1]}}}$' for tol in RTOLS_ALL]
for i_atol, atol in enumerate(ATOLS_ALL):
    for i_rtol, rtol in enumerate(RTOLS_ALL):
        if i_rtol == 0:
            ax.text(i_atol*(n_atol+1), -15, a_labels[i_atol],
                    fontsize=labelsize,
                    transform=ax.transData, rotation=45,
                    horizontalalignment='center', verticalalignment='bottom')
        ax.text(i_atol*(n_atol+1) + i_rtol, -25, r_labels[i_rtol],
                fontsize=labelsize,
                transform=ax.transData, rotation=45,
                horizontalalignment='center', verticalalignment='bottom')
ax.text(-3, -15, 'Abs. tol.:', fontsize=labelsize+1, transform=ax.transData,
        verticalalignment='bottom')
ax.text(-3, -25, 'Rel. tol.:',  fontsize=labelsize+1, transform=ax.transData,
        verticalalignment='bottom')

# Plot text 'B'
ax.text(-0.05, 1, 'B', fontsize=fontsize + 3, transform=ax.transAxes)

# Condense layout
plt.tight_layout()

# Save plot
os.makedirs(DIR_FIGURES, exist_ok=True)
plt.savefig(os.path.join(DIR_FIGURES, "Tolerances_Main.pdf"))
plt.savefig(os.path.join(DIR_FIGURES, "Tolerances_Main.png"))

#plt.show()
