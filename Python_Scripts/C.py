"""Constant definitions."""

import os
import enum

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

# Folder with COPASI binaries, user-dependent, to reproduce LSODA simulations
DIR_COPASI_BIN = os.getenv('COPASI_DIR_BIN', 'COPASI-4.29.228-Linux-64bit/bin')


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
# Model directories

# Base folder for all models
DIR_MODELS = os.path.join(DIR_BASE, 'Models')
# Folder for sedml and sbml model definitions
DIR_MODELS_SEDML = os.path.join(DIR_MODELS, 'sedml')  # TODO remove
# Folder for a copy of the biomodels models
DIR_MODELS_BIOMODELS = os.path.join(DIR_MODELS, 'biomodels')  # TODO remove
# Folder with the final benchmark models (regrouped and adapted sbml files)
DIR_MODELS_REGROUPED = os.path.join(DIR_MODELS, 'regrouped')
# Base folder for the AMICI compilation files
DIR_MODELS_AMICI_BASE = os.path.join(DIR_MODELS, 'amici')
# Folder for all possible AMICI compilation files
DIR_MODELS_AMICI = os.path.join(DIR_MODELS_AMICI_BASE, 'models')
# Folder for only the final models for the main part of the study
DIR_MODELS_AMICI_FINAL = os.path.join(DIR_MODELS_AMICI_BASE, 'models_final')
# Folder for all possible Copasi files
DIR_MODELS_COPASI = os.path.join(DIR_MODELS, 'copasi', 'models')

# Folder for trajectories simulated with AMICI
DIR_MODELS_TRAJ_AMICI = os.path.join(DIR_MODELS, 'trajectories_amici')
# Folder for reference trajectories
DIR_MODELS_TRAJ_REF = os.path.join(DIR_MODELS, 'trajectories_reference')
# Folder for the original COPASI simulations of the biomodels models
DIR_MODELS_TRAJ_REF_BIOMODELS = os.path.join(
    DIR_MODELS, 'trajectories_reference_biomodels')


###############################################################################
# Result directories

# Simulation data base folder
DIR_RESULTS = os.path.join(DIR_BASE, 'results')
# Folder for most of the sub-studies
DIR_RESULTS_ALGORITHMS = os.path.join(DIR_RESULTS, 'algorithms')
# Folder for the tolerances sub-study
DIR_RESULTS_TOLERANCES = os.path.join(DIR_RESULTS, 'tolerances')


###############################################################################
# Configurations for simulations

# Using enum class create enumerations
class SIMCONFIG(enum.Enum):
    """Enumeration of study subtypes."""
    CPUTIME = 'cputime_study'
    FAILURE = 'failure_study'
    TRAJECTORY = 'trajectory_comparison'


# repetitions for simulation when measuring cpu times, to have a roobust result
repetitions_for_cpu_time_study = 25
