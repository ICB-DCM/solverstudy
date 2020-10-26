# execute script loadModels.py for model simulation

from setTime_BioModels import *
from loadModels import *
from changeValues import *
import numpy as np
import libsedml


def all_settings(iModel, iFile, skip_indicator):

    # insert specific model properties as strings, e.g.:
    if skip_indicator == 0:
        BioModels_path = '../Models/BioModelsDatabase_models'
        sedml_path = '../Models/all_models/' + iModel + '/' + iModel + '.sedml'
    elif skip_indicator == 1:
        BioModels_path = '../../Benchmarking_of_numerical_ODE_integration_methods/BioModelsDatabase_models'
        sedml_path = '../../Benchmarking_of_numerical_ODE_integration_methods/sedml_models/' + iModel + '/' + iModel + '.sedml'

    # iFile without extension
    try:
        iFile,_ = iFile.split('.',1)
    except:
        'No extension'

    # call function from 'loadModels.py'
    model = load_specific_model(iModel, iFile, skip_indicator)

    # call function from 'setTime_BioModels.py'
    if os.path.exists(BioModels_path + '/' + iModel):
        sim_start_time, sim_end_time, sim_num_time_points, y_bound = timePointsBioModels(iModel)
    else:
        # call function from 'changeValues.py'
        # change parameter and species according to SEDML file
        model = changeValues(model, iModel, iFile, skip_indicator)

        # tasks
        sedml_file = libsedml.readSedML(sedml_path)

        for iTask in range(0, sedml_file.getNumTasks()):
            all_tasks = sedml_file.getTask(iTask)
            task_simReference = all_tasks.getSimulationReference()

            # time courses
            try:
                all_simulations = sedml_file.getSimulation(iTask)
                sim_Id = all_simulations.getId()
            except:
                # need 'except' clause if more models have same time period
                if all_simulations == None:
                    all_simulations = sedml_file.getSimulation(0)
                    sim_Id = all_simulations.getId()
            try:
                while task_simReference != sim_Id:
                    iTask = iTask + 1
                    all_simulations = sedml_file.getSimulation(iTask)
                    sim_Id = all_simulations.getId()
            except:
                iTask = 0
                while task_simReference != sim_Id:
                    all_simulations = sedml_file.getSimulation(iTask)
                    sim_Id = all_simulations.getId()
                    iTask = iTask + 1

            sim_start_time = all_simulations.getOutputStartTime()
            sim_end_time = all_simulations.getOutputEndTime()
            sim_num_time_points = all_simulations.getNumberOfPoints()

    # set time points for which we want to simulate the model
    model.setTimepoints(np.linspace(sim_start_time, sim_end_time, sim_num_time_points))

    return model
