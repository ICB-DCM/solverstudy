# script to change all values for the JWS simulation


def JWS_changeValues(iFile, sedml_file):

    # get all changes from the sedml file
    for iModels in range(0, sedml_file.getNumModels()):
        all_models = sedml_file.getModel(iModels)
        model_Id = all_models.getId()

        # take only the current sbml file
        list_of_strings = []
        if model_Id == iFile:
            for iAttribute in range(0, all_models.getNumChanges()):
                all_changes = all_models.getChange(iAttribute)
                new_targ = all_changes.getTarget()
                new_val = all_changes.getNewValue()

                # parse whole id out of new_targ string
                id = new_targ.split('\'', )[1]

                # append information into list_of_strings
                list_of_strings.append(id + '=' + new_val + ';')

    return list_of_strings
