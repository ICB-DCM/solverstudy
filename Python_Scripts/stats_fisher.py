"""Statistical tests: Fisher's exact test on various targets."""

import os
import pandas as pd
import scipy.stats as stats
from typing import List, Tuple

from C import (
    DIR_RESULTS_ALGORITHMS, LINSOL_DCT, NONLINSOL_DCT, SOLALG_DCT, ATOL_RTOLS)

# Number of failures and successes for every setting
failures = {}
successes = {}
for solalg, solalg_s in SOLALG_DCT.items():
    for nonlinsol, nonlinsol_s in NONLINSOL_DCT.items():
        for linsol, linsol_s in LINSOL_DCT.items():
            for atol, rtol in ATOL_RTOLS:
                f = f"atol_{atol}__rtol_{rtol}__linSol_{linsol}" \
                    f"__nonlinSol_{nonlinsol}__solAlg_{solalg}.tsv"
                df = pd.read_csv(
                    os.path.join(DIR_RESULTS_ALGORITHMS, f), sep='\t')
                failures[(solalg_s, nonlinsol_s, linsol_s, (atol, rtol))] = \
                    sum(df['failure'])
                successes[(solalg_s, nonlinsol_s, linsol_s, (atol, rtol))] = \
                    df.shape[0] - sum(df['failure'])


def to_arr(str_or_arr: str) -> List:
    """Keep if iterable, convert string to iterable."""
    if isinstance(str_or_arr, str):
        str_or_arr = [str_or_arr]
    return str_or_arr


def sumit(vals, solalgs=None, nonlinsols=None, linsols=None,
          tols=None) -> int:
    """Sum over non-specified variables"""
    # Default: all
    if solalgs is None:
        solalgs = SOLALG_DCT.values()
    if nonlinsols is None:
        nonlinsols = NONLINSOL_DCT.values()
    if linsols is None:
        linsols = LINSOL_DCT.values()
    if tols is None:
        tols = ATOL_RTOLS

    return sum(vals[(solalg, nonlinsol, linsol, (atol, rtol))]
               for solalg in to_arr(solalgs)
               for nonlinsol in to_arr(nonlinsols)
               for linsol in to_arr(linsols)
               for atol, rtol in to_arr(tols))


def fisher_test(fail1: int, pass1: int, fail2: int, pass2: int) -> None:
    """Perform an exact fisher test on failure and success numbers.
    :returns: oddsratio, p_value
    """
    table = [[fail1, pass1], [fail2, pass2]]
    print(table)
    print(stats.fisher_exact(table))


def sumit_both(solalgs=None, nonlinsols=None, linsols=None, tols=None
               ) -> Tuple[int, int]:
    """Shortform to get failure and success number as tuple."""
    return (sumit(failures, solalgs, nonlinsols, linsols, tols),
            sumit(successes, solalgs, nonlinsols, linsols, tols))


###############################################################################
# Various outputs

print("Adams vs BDF")
fisher_test(*sumit_both(solalgs='Adams'),
            *sumit_both(solalgs='BDF'))

for nonlinsol in NONLINSOL_DCT.values():
    print(f"\nAdams vs BDF for nonlinsol {nonlinsol}")
    fisher_test(*sumit_both(solalgs='Adams', nonlinsols=nonlinsol),
                *sumit_both(solalgs='BDF', nonlinsols=nonlinsol))
    for linsol in LINSOL_DCT.values():
        print(f"Adams vs BDF for nonlinsol {nonlinsol}, linsol {linsol}")
        fisher_test(*sumit_both(solalgs='Adams', nonlinsols=nonlinsol,
                                linsols=linsol),
                    *sumit_both(solalgs='BDF', nonlinsols=nonlinsol,
                                linsols=linsol))

print("\nFunctional vs Newton")
fisher_test(*sumit_both(nonlinsols='Functional'),
            *sumit_both(nonlinsols='Newton-type'))

for solalg in SOLALG_DCT.values():
    print(f"\nFunctional vs Newton for solalg {solalg}")
    fisher_test(*sumit_both(solalgs=solalg, nonlinsols='Functional'),
                *sumit_both(solalgs=solalg, nonlinsols='Newton-type'))
    for linsol in LINSOL_DCT.values():
        print(f"Functional vs Newton for solalg {solalg}, linsol {linsol}")
        fisher_test(*sumit_both(solalgs=solalg, nonlinsols='Functional',
                                linsols=linsol),
                    *sumit_both(solalgs=solalg, nonlinsols='Newton-type',
                                linsols=linsol))
