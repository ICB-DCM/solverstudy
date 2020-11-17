# Solver Study

This repository contains all python files and (supplementary) figures for the manuscript 'Benchmarking of numerical integration methods for ODE models of biological systems'.

## Preparations

The study was performed on Linux (Ubuntu 20.10) with Anaconda python 3.8.5
(for Minoconda minor changes are necessary).
All scripts can be found under `Python_Scripts`, which we henceforth assume
to be the working directory (`cd Python_Scripts`).

### Installation

We recommend the installation of a virtual environment:

    conda create -n solverstudy python=3.8
    conda activate solverstudy

Make sure you use the correct python environment (e.g. `which pip`).

As the employed simulation tool AMICI requires BLAS support and swig, those
need to be installed. This is done for anaconda (on Linux) via

    conda install -n solverstudy -c conda-forge openblas
    conda install -n solverstudy -c anaconda swig

Check also the
[AMICI installation requirements](https://github.com/amici-dev/amici/INSTALL.md).

All further required dependencies are defined, including the versions used in
the study, in a file `requirements.txt`, and can be installed via

    pip install -r ../requirements.txt

### Environment configuration

The study writes and loads its data from a data base folder
`SolverStudy{Work|Test}` located/created in the repository base folder,
which can be configured via the environment variable

    export SOLVERSTUDY_DIR_BASE=WORK|TEST

where WORK, TEST are conventions for dedicated folders:
WORK for development work, and TEST is for a smaller test collection.

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

## 1 Create model collection 

### 1.1 Download all sedml and sbml models from the JWS Online Database

	script_download_jws_sedml_sbml.py

### 1.2 Download chosen sbml models from the BioModels Database

	script_download_biomodels_sbml.py

### 1.3 Import all sbml models to AMICI

	sbml2amici.py

### 1.4 Compare the state trajectories of the local simulation of all JWS models to the in-built simulation routine of JWS

	compareStateTrajectories_JWS_1.py
	compareStateTrajectories_JWS_2.py

### 1.6 Compare the state trajectories of the local simulation of all selected BioModels models who can be simulated to the in-built simulation routine of COPASI

	compareStateTrajectories_BioModels_1.py
	compareStateTrajectories_BioModels_2.py

### 1.7 Finalize the model collection by excluding all models that could not be imported of have non-matching trajectories

	selectModelsForMain.py

To skip step 1, the whole benchmark collection is available in 'Solver_Study/Models'.
If step 1 was skipped, the main folder 'Benchmarking_of_numerical_ODE_integration_methods' or the subfolders 'BioModelsDatabase_models', 'json_files', 'sbml2amici' and 'sedml_models' will not exist. 
In this case, the next functions will automatically take the results from 'Solver_Study/Models' of the repository.
Additionally, the main folder 'Benchmarking_of_numerical_ODE_integration_methods' will be created. 

## 2 Solver settings study

### 2.1 Get all Data

	execute_WholeStudy.py
	execute_Tolerances.py

To skip step 2.1, all data files can be found in 'Solver_Study/Data'
If step 2.1 was skipped, the subfolder 'Data' will not exist.
If step 1 was skipped, the subfolder 'json_files' will not exist.
In this case, the next functions will automatically take the results from 'Solver_Study/Data' of the repository. 

### 2.2 Visualize all results according to the order seen in the paper

Remark: All figures created by the following scripts are not stored automatically! Thus, the main folder 'Benchmarking_of_numerical_ODE_integration_methods' will not be created if it does not already exists.

##### 2.2.1 Basic Properties

	plot_BasicProperties_Main.py (Main Manuscript, Figure 1)
 	plot_BasicProperties_Supp.py (Supplementary, Figure S1)

##### 2.2.2 Non-linear solver study

Remark: plot_NonLinSol_Main.py displays only the bottom part of Figure 2 while the upper part was created via InkScape

	plot_NonLinSol_Main.py (Main Manuscript, Figure 2)
	plot_NonLinSol_Supp.py (Supplementary, Figure S2)

##### 2.2.3 Linear solver study

	plot_LinearSolver_Main.py (Main Manuscript, Figure 3)
	plot_LinearSolver_Supp1.py (Supplementary, Figure S3)
	plot_LinearSolver_Supp2.py (Supplementary, Figure S4)

##### 2.2.4 Tolerances study
	
	plot_Tolerances_Main.py (Main Manuscript, Figure 4)
	plot_Tolerances_Supp.py (Supplementary, Figure S5)

##### 2.2.5 Solver algorithm study

	plot_SolAlg_Main.py (Main Manuscript, Figure 5)
	plot_SolAlg_Supp1.py (Supplementary, Figure S6)
	plot_SolAlg_Supp2.py (Supplementary, Figure S7)

To skip step 2.2, all figures can be found in 'Solver_Study/Figures'.

### 2.3 Get the complete benchmark collection list containing all 167 models

	TableOfAllBenchmarkModels.py

If the folder 'Benchmarking_of_numerical_ODE_integration_methods/Data' does not exist, to display the table, please save it manually on some directory of your choice
