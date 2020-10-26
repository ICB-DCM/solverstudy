# script to average simulation time of all models from the model collection

import os
import pandas as pd


def averaging(next_tsv):

    # create data frame with new values
    columns = next_tsv.columns
    new_df = pd.DataFrame(columns=columns, data=[])

    # get new names
    new_list = []
    for iFile in range(0, len(next_tsv['id'])):
        new_id = next_tsv['id'][iFile].split('_{')[0]
        new_list.append(new_id)
    next_tsv['id'] = new_list

    # get old but still valid data to new data frame
    # define iter object
    iter_object = iter(range(0, len(next_tsv['id'])))
    repetition = 0
    for iFile in iter_object:
        new_df = new_df.append({}, ignore_index=True)
        if iFile == 0:
            if next_tsv['id'][iFile] == next_tsv['id'][iFile + 1] and next_tsv['state_variables'][iFile] == next_tsv['state_variables'][iFile + 1]:
                # find all exceptions by hand and type them in manually --- no clear rule existing
                if next_tsv['id'][iFile] == '{kolodkin2010_figure2b}':
                    if 'id' in columns:
                        new_df.loc[iFile - repetition].id = next_tsv['id'][iFile]
                    if 't_intern_ms' in columns:
                        new_df.loc[iFile - repetition].t_intern_ms = next_tsv['t_intern_ms'][iFile]
                    if 't_extern_ms' in columns:
                        new_df.loc[iFile - repetition].t_extern_ms = next_tsv['t_extern_ms'][iFile]
                    if 'state_variables' in columns:
                        new_df.loc[iFile - repetition].state_variables = next_tsv['state_variables'][iFile]
                    if 'parameters' in columns:
                        new_df.loc[iFile - repetition].parameters = next_tsv['parameters'][iFile]
                    if 'status' in columns:
                        new_df.loc[iFile - repetition].status = next_tsv['status'][iFile]
                    if 'error_message' in columns:
                        new_df.loc[iFile - repetition].error_message = next_tsv['error_message'][iFile]
                    if 'reactions' in columns:
                        new_df.loc[iFile - repetition].reactions = next_tsv['reactions'][iFile]
                else:
                    if 'id' in columns:
                        new_df.loc[iFile - repetition].id = next_tsv['id'][iFile]
                    if 't_intern_ms' in columns:
                        new_df.loc[iFile - repetition].t_intern_ms = ''
                    if 't_extern_ms' in columns:
                        new_df.loc[iFile - repetition].t_extern_ms = ''
                    if 'state_variables' in columns:
                        new_df.loc[iFile - repetition].state_variables = next_tsv['state_variables'][iFile]
                    if 'parameters' in columns:
                        new_df.loc[iFile - repetition].parameters = next_tsv['parameters'][iFile]
                    if 'status' in columns:
                        new_df.loc[iFile - repetition].status = next_tsv['status'][iFile]
                    if 'error_message' in columns:
                        new_df.loc[iFile - repetition].error_message = next_tsv['error_message'][iFile]
                    if 'reactions' in columns:
                        new_df.loc[iFile - repetition].reactions = next_tsv['reactions'][iFile]
            else:
                if 'id' in columns:
                    new_df.loc[iFile - repetition].id = next_tsv['id'][iFile]
                if 't_intern_ms' in columns:
                    new_df.loc[iFile - repetition].t_intern_ms = next_tsv['t_intern_ms'][iFile]
                if 't_extern_ms' in columns:
                    new_df.loc[iFile - repetition].t_extern_ms = next_tsv['t_extern_ms'][iFile]
                if 'state_variables' in columns:
                    new_df.loc[iFile - repetition].state_variables = next_tsv['state_variables'][iFile]
                if 'parameters' in columns:
                    new_df.loc[iFile - repetition].parameters = next_tsv['parameters'][iFile]
                if 'status' in columns:
                    new_df.loc[iFile - repetition].status = next_tsv['status'][iFile]
                if 'error_message' in columns:
                    new_df.loc[iFile - repetition].error_message = next_tsv['error_message'][iFile]
                if 'reactions' in columns:
                    new_df.loc[iFile - repetition].reactions = next_tsv['reactions'][iFile]

        elif iFile != len(next_tsv['id']) - 1:
            # check in both directions
            if next_tsv['id'][iFile] == next_tsv['id'][iFile + 1] and next_tsv['state_variables'][iFile] == next_tsv['state_variables'][iFile + 1] or \
               next_tsv['id'][iFile] == next_tsv['id'][iFile - 1] and next_tsv['state_variables'][iFile] == next_tsv['state_variables'][iFile - 1]:
                # find all exceptions by hand and type them in manually --- no clear rule existing
                if next_tsv['id'][iFile] == '{kolodkin2010_figure2b}':
                    if 'id' in columns:
                        new_df.loc[iFile - repetition].id = next_tsv['id'][iFile]
                    if 't_intern_ms' in columns:
                        new_df.loc[iFile - repetition].t_intern_ms = next_tsv['t_intern_ms'][iFile]
                    if 't_extern_ms' in columns:
                        new_df.loc[iFile - repetition].t_extern_ms = next_tsv['t_extern_ms'][iFile]
                    if 'state_variables' in columns:
                        new_df.loc[iFile - repetition].state_variables = next_tsv['state_variables'][iFile]
                    if 'parameters' in columns:
                        new_df.loc[iFile - repetition].parameters = next_tsv['parameters'][iFile]
                    if 'status' in columns:
                        new_df.loc[iFile - repetition].status = next_tsv['status'][iFile]
                    if 'error_message' in columns:
                        new_df.loc[iFile - repetition].error_message = next_tsv['error_message'][iFile]
                    if 'reactions' in columns:
                        new_df.loc[iFile - repetition].reactions = next_tsv['reactions'][iFile]
                else:
                    if 'id' in columns:
                        new_df.loc[iFile - repetition].id = next_tsv['id'][iFile]
                    if 't_intern_ms' in columns:
                        new_df.loc[iFile - repetition].t_intern_ms = ''
                    if 't_extern_ms' in columns:
                        new_df.loc[iFile - repetition].t_extern_ms = ''
                    if 'state_variables' in columns:
                        new_df.loc[iFile - repetition].state_variables = next_tsv['state_variables'][iFile]
                    if 'parameters' in columns:
                        new_df.loc[iFile - repetition].parameters = next_tsv['parameters'][iFile]
                    if 'status' in columns:
                        new_df.loc[iFile - repetition].status = next_tsv['status'][iFile]
                    if 'error_message' in columns:
                        new_df.loc[iFile - repetition].error_message = next_tsv['error_message'][iFile]
                    if 'reactions' in columns:
                        new_df.loc[iFile - repetition].reactions = next_tsv['reactions'][iFile]

            else:
                if 'id' in columns:
                    new_df.loc[iFile - repetition].id = next_tsv['id'][iFile]
                if 't_intern_ms' in columns:
                    new_df.loc[iFile - repetition].t_intern_ms = next_tsv['t_intern_ms'][iFile]
                if 't_extern_ms' in columns:
                    new_df.loc[iFile - repetition].t_extern_ms = next_tsv['t_extern_ms'][iFile]
                if 'state_variables' in columns:
                    new_df.loc[iFile - repetition].state_variables = next_tsv['state_variables'][iFile]
                if 'parameters' in columns:
                    new_df.loc[iFile - repetition].parameters = next_tsv['parameters'][iFile]
                if 'status' in columns:
                    new_df.loc[iFile - repetition].status = next_tsv['status'][iFile]
                if 'error_message' in columns:
                    new_df.loc[iFile - repetition].error_message = next_tsv['error_message'][iFile]
                if 'reactions' in columns:
                    new_df.loc[iFile - repetition].reactions = next_tsv['reactions'][iFile]
        else:
            if next_tsv['id'][iFile] == next_tsv['id'][iFile - 1] and next_tsv['state_variables'][iFile] == next_tsv['state_variables'][iFile + 1]:
                # find all exceptions by hand and type them in manually --- no clear rule existing
                if next_tsv['id'][iFile] == '{kolodkin2010_figure2b}':
                    if 'id' in columns:
                        new_df.loc[iFile - repetition].id = next_tsv['id'][iFile]
                    if 't_intern_ms' in columns:
                        new_df.loc[iFile - repetition].t_intern_ms = next_tsv['t_intern_ms'][iFile]
                    if 't_extern_ms' in columns:
                        new_df.loc[iFile - repetition].t_extern_ms = next_tsv['t_extern_ms'][iFile]
                    if 'state_variables' in columns:
                        new_df.loc[iFile - repetition].state_variables = next_tsv['state_variables'][iFile]
                    if 'parameters' in columns:
                        new_df.loc[iFile - repetition].parameters = next_tsv['parameters'][iFile]
                    if 'status' in columns:
                        new_df.loc[iFile - repetition].status = next_tsv['status'][iFile]
                    if 'error_message' in columns:
                        new_df.loc[iFile - repetition].error_message = next_tsv['error_message'][iFile]
                    if 'reactions' in columns:
                        new_df.loc[iFile - repetition].reactions = next_tsv['reactions'][iFile]
                else:
                    if 'id' in columns:
                        new_df.loc[iFile - repetition].id = next_tsv['id'][iFile]
                    if 't_intern_ms' in columns:
                        new_df.loc[iFile - repetition].t_intern_ms = ''
                    if 't_extern_ms' in columns:
                        new_df.loc[iFile - repetition].t_extern_ms = ''
                    if 'state_variables' in columns:
                        new_df.loc[iFile - repetition].state_variables = next_tsv['state_variables'][iFile]
                    if 'parameters' in columns:
                        new_df.loc[iFile - repetition].parameters = next_tsv['parameters'][iFile]
                    if 'status' in columns:
                        new_df.loc[iFile - repetition].status = next_tsv['status'][iFile]
                    if 'error_message' in columns:
                        new_df.loc[iFile - repetition].error_message = next_tsv['error_message'][iFile]
                    if 'reactions' in columns:
                        new_df.loc[iFile - repetition].reactions = next_tsv['reactions'][iFile]
            else:
                if 'id' in columns:
                    new_df.loc[iFile - repetition].id = next_tsv['id'][iFile]
                if 't_intern_ms' in columns:
                    new_df.loc[iFile - repetition].t_intern_ms = next_tsv['t_intern_ms'][iFile]
                if 't_extern_ms' in columns:
                    new_df.loc[iFile - repetition].t_extern_ms = next_tsv['t_extern_ms'][iFile]
                if 'state_variables' in columns:
                    new_df.loc[iFile - repetition].state_variables = next_tsv['state_variables'][iFile]
                if 'parameters' in columns:
                    new_df.loc[iFile - repetition].parameters = next_tsv['parameters'][iFile]
                if 'status' in columns:
                    new_df.loc[iFile - repetition].status = next_tsv['status'][iFile]
                if 'error_message' in columns:
                    new_df.loc[iFile - repetition].error_message = next_tsv['error_message'][iFile]
                if 'reactions' in columns:
                    new_df.loc[iFile - repetition].reactions = next_tsv['reactions'][iFile]

    # repeat for round(max(repetition_of_else)/2) --- find out manually, otherwise high number will work as well
    repetition = 1
    for iEffcy in range(0, 1000):

        # for speed allocation --- break if nothing happens ~ break if repetition == 0
        if repetition == 0:
            print('Only ' + str(iEffcy - 1) + ' iterations needed for correct new data frame!')
            break

        repetition = 0
        for iFile in range(0, len(new_df['id'])):
            iter_counter = len(new_df['id'])
            if iFile < iter_counter - 1:
                if new_df['id'][iFile] == new_df['id'][iFile + 1] and new_df['state_variables'][iFile] == new_df['state_variables'][iFile + 1]:
                    # find all exceptions by hand and type them in manually --- no clear rule existing
                    if new_df['id'][iFile] == '{kolodkin2010_figure2b}':
                        'Do nothing for now'
                    else:
                        # delete next file + reset the index
                        new_df = new_df.drop(iFile)
                        new_df = new_df.reset_index(drop=True)

                        # jump over one file
                        for counter in range(0, 1):
                            repetition = repetition + 1
                else:
                    'Do nothing for now'
            else:
                'Do nothing for now'

    if 't_intern_ms' in columns or 't_extern_ms' in columns:
        # get right values --- only possible if t_intern_ms or t_extern_ms exist
        temp_1 = []
        temp_2 = []
        output_1 = []
        output_2 = []
        for iFile in range(0, len(new_df['id'])):
            # search for blank space
            if new_df['t_intern_ms'][iFile] == '':
                name = new_df['id'][iFile]
                for iOldFile in range(0, len(next_tsv['id'])):
                    if next_tsv['id'][iOldFile] == name:
                        temp_1.append(next_tsv['t_intern_ms'][iOldFile])
                        temp_2.append(next_tsv['t_extern_ms'][iOldFile])
                    else:
                        output_1.append(temp_1)
                        output_2.append(temp_2)
                        if output_1[len(output_1) - 1] == []:
                            del output_1[len(output_1) - 1]
                        temp_1 = []
                        if output_2[len(output_2) - 1] == []:
                            del output_2[len(output_2) - 1]
                        temp_2 = []

                if temp_1:
                    output_1.append(temp_1)
                if temp_2:
                    output_2.append(temp_2)

        # divide through values
        divided_numbers_1 = []
        divided_numbers_2 = []
        for iNum in range(0, len(output_1)):
            divided_numbers_1.append(sum(output_1[iNum])/len(output_1[iNum]))
        for iNum in range(0, len(output_2)):
            divided_numbers_2.append(sum(output_2[iNum]) / len(output_2[iNum]))

        # assign to right place by deleting the first argument
        for iFile in range(0, len(new_df['id'])):
            if new_df['t_intern_ms'][iFile] == '':
                new_df['t_intern_ms'][iFile] = divided_numbers_1[0]
                new_df['t_extern_ms'][iFile] = divided_numbers_2[0]
                divided_numbers_1.pop(0)
                divided_numbers_2.pop(0)

    # change id for uniquenes of kolodkin
    for iMod in range(0, len(new_df['id'])):
        if new_df['id'][iMod] == '{kolodkin2010_figure2b}':
            new_df['id'][iMod] = '{kolodkin2010_figure2b}' + '_' + str(iMod)

    return(new_df)
