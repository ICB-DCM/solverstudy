#!/bin/bash

# Exit if a command fails
set -ev

if [ -e SolverStudyWork ]; then
  echo "./SolverStudyWork exists already, remove it first"
  exit 1
fi

# Configure environment
export SOLVERSTUDY_DIR_BASE=WORK
export COPASI_DIR_BIN="../COPASI/bin"

# Go to base directory
cd Python_Scripts

# Run download
time python script_download_jws_sedml_sbml.py
time python script_download_biomodels_sbml.py

# Run model regrouping
time python script_regroup_models.py

# Run amici import and compilation
time python sbml2amici.py
time python sbml2copasi.py

# Get reference trajectories
time python script_get_reference_trajectories.py

# Run trajectory comparison
time python compare_state_trajectories_amici.py
time python compare_state_trajectories_copasi.py

# Select models to include in main study
time python filter_models_by_error.py

# Run main study
time python execute_study_algorithms.py
time python execute_study_tolerances.py

# Run plots
time python model_numbers.py
for plot_script in `ls plot_*`; do
  time python $plot_script
done

# Run further analyses
for script in `ls stats_*`; do
  python $script
done
