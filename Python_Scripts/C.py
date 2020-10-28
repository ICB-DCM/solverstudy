"""Constant definitions."""

import os

###############################################################################
# Base folder

# The simulation scripts write their output to `DIR_WORK_BASE` by default.
DIR_WORK_BASE = os.path.abspath('../SolverStudyWork')
# The output of the study has been conserved in `DIR_CACHE_BASE`.
DIR_CACHE_BASE = os.path.abspath('../SolverStudyCache')
# The `DIR_TEST_BASE` folder contains a smaller test model set
DIR_TEST_BASE = os.path.abspath('../SolverStudyTest')

# All scripts expect their in/output relative to `DIR_BASE`.
DIR_BASE = os.getenv('SOLVERSTUDY_DIR_BASE', None)
if DIR_BASE is None:
    raise ValueError(
        "The environment variable SOLVERSTUDY_DIR_BASE must be set.")

# Some convenience default short-forms
if DIR_BASE == 'WORK':
    DIR_BASE = DIR_WORK_BASE
elif DIR_BASE == 'CACHE':
    DIR_BASE = DIR_CACHE_BASE
elif DIR_BASE == 'TEST':
    DIR_BASE = DIR_TEST_BASE

###############################################################################
# Configuration of the model list

# List of JWS sedml models
JWS_MODEL_FILE = os.getenv(
    'SOLVERSTUDY_JWS_MODEL_FILE', 'jws_models.txt')
# List of Biomodels model slugs
BIOMODELS_MODEL_SLUG_FILE = os.getenv(
    'SOLVERSTUDY_BIOMODELS_MODEL_SLUG_FILE', 'biomodels_model_slugs.txt')
# List of Biomodels sbml models
BIOMODELS_MODEL_FILE = os.getenv(
    'SOLVERSTUDY_BIOMODELS_MODEL_FILE', 'biomodels_models.txt')
INCLUDE_FROEHLICH = os.getenv('SOLVERSTUDY_INCLUDE_FROEHLICH', 'YES')

###############################################################################
# Data directories

# Simulation data base folder
DIR_DATA = os.path.join(DIR_BASE, 'Data')
# Folder for most of the sub-studies
DIR_DATA_WHOLESTUDY = os.path.join(DIR_DATA, 'WholeStudy')
# Folder for the tolerances sub-study
DIR_DATA_TOLERANCES = os.path.join(DIR_DATA, 'TolerancesStudy')

###############################################################################
# Model directories

# Base folder for all models
DIR_MODELS = os.path.join(DIR_BASE, 'Models')
# Folder for sedml and sbml model definitions
DIR_MODELS_SEDML = os.path.join(DIR_MODELS, 'sedml')
# Folder for a copy of the biomodels models
DIR_MODELS_BIOMODELS = os.path.join(DIR_MODELS, 'biomodels')  # TODO remove
# Base folder for the AMICI compilation files
DIR_MODELS_AMICI_BASE = os.path.join(DIR_MODELS, 'amici')
# Folder for all possible AMICI compilation files
DIR_MODELS_AMICI = os.path.join(DIR_MODELS_AMICI_BASE, 'models')
# Folder for only the final models for the main part of the study
DIR_MODELS_AMICI_FINAL = os.path.join(DIR_MODELS_AMICI_BASE, 'models_final')
# Folder for trajectories simulated with AMICI
DIR_MODELS_TRAJ_AMICI = os.path.join(DIR_MODELS, 'trajectories_amici')
# Folder for reference trajectories
DIR_MODELS_TRAJ_REF = os.path.join(DIR_MODELS, 'trajectories_reference')
# Folder for the original COPASI simulations of the biomodels models
DIR_MODELS_TRAJ_REF_BIOMODELS = os.path.join(
    DIR_MODELS, 'trajectories_reference_biomodels')
