#!/bin/bash

# Exit if a command fails
set -e

if [ -e SolverStudyTest ]; then
  echo "./SolverStudyTest exists already, remove it first"
  exit 1
fi

# Configure environment
export SOLVERSTUDY_DIR_BASE=TEST
export SOLVERSTUDY_JWS_MODEL_FILE="../Test/test_set_jws.txt"
export SOLVERSTUDY_BIOMODELS_MODEL_SLUG_FILE="../Test/test_set_biomodels_slug.txt"
export SOLVERSTUDY_BIOMODELS_MODEL_FILE="../Test/test_set_biomodels.txt"
export SOLVERSTUDY_INCLUDE_FROEHLICH="No"

# Go to base directory
cd Python_Scripts

# Run download
time python script_download_all_sedml_models.py
time python script_download_all_sbml_biomodels.py

# run model regrouping
time python script_regroup_models.py

# Run amici import and compilation
time python sbml2amici.py
# time python sbml2copasi.py # TBD: automated Copasi import

# Run JWS trajectory comparison
time python compare_state_trajectories.py

# Select models to include in main study
time python filter_models_by_error.py

# Run main study
# time python execute_WholeStudy.py
# time python execute_Tolerances.py

# TODO Run Plots
