# Solver Study

This repository contains all python files and (supplementary) figures for the manuscript 'Benchmarking of numerical integration methods for ODE models of biological systems'.

## 0 Problems that can occur

### 0.1 downloading this repository on Windows:

names for specific models can be too long to save (error could occur e.g. for the model 'Morris2002')
Work-around: Omit or rename such models

### 0.2 using a different python interpreter than Anaconda

if a different python interpreter than Anaconda is used, the python package urlib or urlib3 might not work. 
Thus, the download of all sedml models from the JWS database might fail (cf. step 1.1). 

### 0.3 working with python packages

if the package tqdm does not show a progress bar, the button "Emulate terminal in output console" in the
python configurations must be switched on.

### 0.4 doing step 1 only partially

in step 1, the main folder 'Benchmarking_of_numerical_ODE_integration_methods' with its subfolders 'BioModelsDatabase_models', 'json_files', 'sbml2amici' and 'sedml_models' will be created. 
If some steps in 1 are skipped, other scripts from step 1 will fail!
If some but not all steps in 1 are executed, the following scripts in step 2 might not work as intended. 
To some extend, all scripts from step 2 onwards cover many possibilities, but maybe not all.
Hence, to guarantee a successful reproduction of the study, please either execute step 1 with all substeps,
or not at all.

The study can be reproduced by following the order in which all scripts have to be executed.
All python scripts can be found in 'Solver_Study/Python_Scripts'.
The study was done by using the software versions listed in `Solver_Study/Software/requirements.txt`.
When reproducing this study, all results are stored in a therefore created folder 'Benchmarking_of_numerical_ODE_integration_methods' on the same level as 
the downloaded repository.

### 0.5 different AMICI version used

The AMICI version used for this project was 0.10.19. However, it was a commit from a feature branch and had different functionality than AMICI 0.10.19 from the master branch. In order to reproduce result easily, it may be useful to use 0.10.20 from the master branch, which has these features included, if finding the commit from the feature branch is too complicated.

## 1 Create model collection 

### 1.1 Download all sedml and sbml models from the JWS Online Database

	script_download_all_sedml_models.py

### 1.2 Download chosen sbml models from the BioModels Database

	script_download_all_sbml_biomodels.py

### 1.3 Import all sbml models to AMICI

	sbml2amici.py
	sbml2amici_BioModelsDatabase.py

### 1.4 Compare the state trajectories of the local simulation of all JWS models to the in-built simulation routine of JWS

	compareStateTrajectories_JWS_1.py
	compareStateTrajectories_JWS_2.py

### 1.5 Derive the whole model collection for JWS and make a pre-selection of the biomodels based on their ability to be simulated 

	correctStateTrajectories_JWS.py

### 1.6 Compare the state trajectories of the local simulation of all selected BioModels models who can be simulated to the in-built simulation routine of COPASI

	compareStateTrajectories_BioModels_1.py
	compareStateTrajectories_BioModels_2.py

### 1.7 Finalize the model collection by excluding all biomodels which have wrong state trajectories

	correctStateTrajectories_BioModels.py

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
