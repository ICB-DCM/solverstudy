"""Utility functions."""

import pandas as pd
from typing import Any


def is_empty(obj: Any) -> bool:
    """Check whether variable `obj`, typically a pandas cell, is,
    in an intuitive sense, empty."""
    return pd.isnull(obj) or obj == ""
