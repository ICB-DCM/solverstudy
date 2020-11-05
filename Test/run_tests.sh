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
time python compareStateTrajectories_JWS_1.py
time python compareStateTrajectories_JWS_2.py

# We need to manually copy the trajectory references
cp -r ../Cache/trajectories_reference_biomodels ../SolverStudyTest/Models

# Run Biomodels trajectory comparison
time python compareStateTrajectories_BioModels_1.py
time python compareStateTrajectories_BioModels_2.py

# Select models to include in main study
time python selectModelsForMain.py

# Run main study
time python execute_WholeStudy.py
time python execute_Tolerances.py

# TODO Run Plots
