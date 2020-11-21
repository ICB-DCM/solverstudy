"""Decision tree on the solver algorithms."""

import os
import numpy as np
import pandas as pd
from sklearn import tree

from C import (
    DIR_RESULTS_ALGORITHMS, LINSOL_DCT, NONLINSOL_DCT, SOLALG_DCT, ATOL_RTOLS)

# Number of failures and successes for every setting
times = {}
states = {}
for solalg, solalg_s in SOLALG_DCT.items():
    for nonlinsol, nonlinsol_s in NONLINSOL_DCT.items():
        for linsol, linsol_s in LINSOL_DCT.items():
            for atol, rtol in ATOL_RTOLS:
                f = f"atol_{atol}__rtol_{rtol}__linSol_{linsol}" \
                    f"__nonlinSol_{nonlinsol}__solAlg_{solalg}.tsv"
                df = pd.read_csv(
                    os.path.join(DIR_RESULTS_ALGORITHMS, f), sep='\t')
                times[(solalg_s, nonlinsol_s, linsol_s, (atol, rtol))] = \
                    df['median_intern']
                states[(solalg_s, nonlinsol_s, linsol_s, (atol, rtol))] = \
                    df['n_species']

# subselect for nonlinsol Newton, linsol KLU
times_am_flat = []
times_bdf_flat = []
states_flat = []
for atol, rtol in ATOL_RTOLS:
    times_am_flat.extend(list(
        times[('Adams', 'Newton-type', 'KLU', (atol, rtol))]))
    times_bdf_flat.extend(list(
        times[('BDF', 'Newton-type', 'KLU', (atol, rtol))]))
    states_flat.extend(
        states[('Adams', 'Newton-type', 'KLU', (atol, rtol))])
times_am_flat = np.array(times_am_flat)
times_bdf_flat = np.array(times_bdf_flat)
states_flat = np.array(states_flat)

# remove nan values
nan_mask = np.isnan(times_am_flat) | np.isnan(times_bdf_flat) | \
           np.isnan(states_flat)
times_am_flat = times_am_flat[~nan_mask]
times_bdf_flat = times_bdf_flat[~nan_mask]
states_flat = states_flat[~nan_mask]

am_winner = times_am_flat < times_bdf_flat

# train tree
clf = tree.DecisionTreeClassifier(max_depth=1)
clf.fit(states_flat.reshape(-1, 1), am_winner)
print(tree.export_text(clf))

# Accuracy
print(
    sum(clf.predict(states_flat.reshape(-1, 1)) == am_winner) / am_winner.size)
