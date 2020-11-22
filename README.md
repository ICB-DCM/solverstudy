# Solver Study

This repository contains all python files and (supplementary) figures for the
manuscript "Benchmarking of numerical integration methods for ODE models of
biological systems'.

## Preparations

The study was performed on Linux (Ubuntu 20.10) with Anaconda python 3.8.5
(for Minoconda minor changes are necessary).

### Installation

We recommend the installation of a virtual environment:

    conda create -n solverstudy python=3.8
    conda activate solverstudy

Make sure you use the correct python environment (e.g. `which pip`,
`which python`).

As the employed simulation tool AMICI requires BLAS support and swig, those
need to be installed. This is done for anaconda via

    conda install -n solverstudy -c conda-forge openblas
    conda install -n solverstudy -c anaconda swig

Check also the
[AMICI installation requirements](https://github.com/amici-dev/amici/INSTALL.md).

All further required dependencies are defined, including the versions used in
the study, in a file `requirements.txt`, and can be installed via

    pip install -r requirements.txt

### Environment configuration

The study writes and loads its data from a data base folder
`SolverStudy{Work|Test}` located/created in the repository base folder,
which can be configured via the environment variable

    export SOLVERSTUDY_DIR_BASE=WORK|TEST|CACHE

where WORK, TEST, CACHE are conventions for dedicated folders:
WORK for development work, TEST is for a smaller test collection, and CACHE
contains a cached version of the essential data used in the study, shipped with
the repository.

All scripts can be found under `Python_Scripts`, which we henceforth assume
to be the working directory (`cd Python_Scripts`).

### Known problems

* Downloading this repository on Windows:
  Names for specific models can be too long to save (error could occur e.g. for
  the model 'Morris2002'). Work-around: Omit or rename such models

* Using a different python interpreter than Anaconda
  If a different python interpreter than Anaconda is used, the python package
  urlib or urlib3 might not work. 
  Thus, the download of all sedml models from the JWS database might fail (cf.
  step 1.1).

* Using more recent package versions
  The exact versions used in this study are given in `requirements.txt`.
  In principle, more recent versions should be applicable, which is desirable,
  however minor modifications may be necessary if some API changed.

### Tests

We run some very basic unit tests, using a smaller test set. The tests can be
found under `Test`, and are run automatically on GitHub via `.github`.

The tests can be run via

    bash Test/run_tests.sh

## 1 Create model collection 

Note: The whole study can also be run via a single call to

    bash Bash_Scripts/run_study.sh

### 1.1 Model download

Download SEDML and SBML models from JWS and SBML models from Biomodels:

    python script_download_jws_sedml_sbml.py
    python script_download_biomodels_sbml.py

### 1.2 Regroup models

    python script_regroup_models.py

### 1.3 Import to AMICI and COPASI

    python sbml2amici.py
    python sbml2copasi.py

### 1.4 Get reference trajectories

The reference trajectories are by default imported from local Cache, but can
be downloaded from JWS via setting the environment flag
`SOLVERSTUDY_USE_CACHED_REF_TRAJ="YES"`. Rerunning the Biomodels reference
trajectories currently requires manual compilation.

    python script_get_reference_trajectories.py

### 1.5 Compare AMICI and COPASI simulations to the reference trajectories

    python compare_state_trajectories_amici.py
    python compare_state_trajectories_copasi.py

### 1.6 Select models to include in the study

    python filter_models_by_error.py

## 2 Main study

The main study consists of two parts: an algorithm study and a tolerance study:

    python execute_study_algorithms.py
    python execute_study_tolerances.py

## 3 Analysis

All figures used in the main manuscript and the supplementary information
can be generated via the scripts entitled `Python_Scripts/plot_*`.
This can be automatized via

    bash Bash_Scripts/create_figures.sh

(requires the environment flag `SOLVERSTUDY_DIR_BASE` to be set).

Further analyses are contained ins scripts entitled
`Python_Scripts/stats_*`.
