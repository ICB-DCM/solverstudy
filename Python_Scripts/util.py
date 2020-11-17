"""Utility functions."""

import pandas as pd
from typing import Any


def is_empty(obj: Any) -> bool:
    """Check whether variable `obj`, typically a pandas cell, is,
    in an intuitive sense, empty."""
    return pd.isnull(obj) or obj == ""


def solalg_from_fname(fname):
    return fname.split('.')[0].split('__')[4].split('_')[1]


def nonlinsol_from_fname(fname):
    return fname.split('.')[0].split('__')[3].split('_')[1]


def linsol_from_fname(fname):
    return fname.split('.')[0].split('__')[2].split('_')[1]


def rtol_from_fname(fname):
    return fname.split('.')[0].split('__')[1].split('_')[1]


def atol_from_fname(fname):
    return fname.split('.')[0].split('__')[0].split('_')[1]
