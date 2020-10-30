"""Imports the SED-ML models and the SBML models from Biomodels and regroups them according to model properties (state variables, reactions, names) in a newly created folder structure.
One folder then corresponds to one benchmark model, but still, multiple SBML files may blong to one benchmark model."""

# Attention:    boundary conditions are not being simulated by JWS!

# Note: libsedml must be imported before libsbml for whatever reason

import libsedml
import libsbml
import amici.plotting
import numpy as np
import pandas as pd
import os
import urllib.request
import tempfile

from execute_loadModels import all_settings
from JWS_changeValues import JWS_changeValues

from C import (
    DIR_MODELS_SEDML, DIR_MODELS_BIOMODELS, DIR_MODELS_FINAL)


