# AMICI import of a JWS sbml model from the model collection

import libsbml
import tempfile
import amici
import os
import logging
import pandas as pd

from C import (
    DIR_BASE, DIR_MODELS_REGROUPED, DIR_MODELS,
    DIR_COPASI_BIN, DIR_MODELS_COPASI)


# important paths
models_path = DIR_MODELS_COPASI
models_base_path = DIR_MODELS
base_path = DIR_MODELS_REGROUPED

# create directory for all future amici models
if not os.path.exists(models_path):
    os.makedirs(models_path)

# create logger object
logger = logging.getLogger()

# initialize the log settings
logging.basicConfig(filename=os.path.join(DIR_BASE, 'sbml2copasi.log'),
                    level=logging.DEBUG)

def import_sbmls_in_copasi(model_info):
    # list of all directories + SBML files
    list_directory = sorted(os.listdir(base_path))

    # set row-counter for .tsv file and list all model
    for i_model in list_directory:
        list_files = os.listdir(os.path.join(base_path, i_model))
        list_files = sorted(list_files)

        for i_file in list_files:
            sbml_file = os.path.join(base_path, i_model, i_file)
            print('Current Model: ' + i_model + '_' + i_file.split(".")[0])

            # Get the current row in .tsv file
            regrouped_path = os.path.relpath(sbml_file, DIR_MODELS)
            model_row = model_info.loc[model_info['regrouped_path'] == regrouped_path]
            idx = int(model_row.index.values)
            # check if amici_import went well
            if model_row.loc[idx, 'amici_import'] != 'OK':
                continue

            # create temporary filename for an adapted sbml file for Copasi
            temp_file_name, sbml_model_name, output_table = \
                _adapt_sbml_file(sbml_file)
            # create a Copasi readable file
            cps_file = _create_copasi_file(model_row, idx, temp_file_name)
            # Id Copasi import did not work, skip
            if cps_file is None:
                continue
            # adapt this Copasi readable file
            _adapt_copasi_file(model_row, idx, cps_file, sbml_model_name,
                               output_table)
            # update the model info table
            model_info.loc[idx, 'copasi_path'] = \
                os.path.relpath(cps_file, DIR_MODELS)

    return model_info


def _adapt_sbml_file(sbml_file):
    # create temporary filename for an adapted sbml file for Copasi
    temp = sbml_file.split('.')
    temp_file_name = temp[0] + '_deleteme.xml'

    # get the sbml model, adapt it for Copasi
    sbml_model = (libsbml.readSBML(sbml_file)).getModel()
    sbml_model_name = sbml_model.getName()
    output_table = []
    for species in sbml_model.getListOfSpecies():
        # Copasi prioritizes species names over IDs
        # We have to remove them to user IDs as identifiers in Copasi
        species.unsetMetaId()
        species.unsetName()
        output_table.append((species.getCompartment(), species.getId()))

    # save changed sbml files and the accompaniying sedml file
    libsbml.writeSBMLToFile(sbml_model.getSBMLDocument(),
                            temp_file_name)
    return temp_file_name, sbml_model_name, output_table


def _create_copasi_file(model_row, idx, temp_file_name):
    # we want to create a cps-file for copasi:
    model_folder = model_row.loc[idx, 'regrouped_path'].split('/')[-2]
    model_folder = os.path.join(DIR_MODELS_COPASI, model_folder)
    # parse the temporary file name
    cps_file = (model_row.loc[idx, 'regrouped_path'].split('/')[-1]).split(
        '.')[0] + '.cps'
    cps_file =  os.path.join(model_folder, cps_file)
    # create the folder
    if not os.path.exists(model_folder):
        os.makedirs(model_folder)

    # run the Copasi import and remove temporary file
    CopasiSE = os.path.join(DIR_COPASI_BIN, 'CopasiSE')
    os.system(f'{CopasiSE} -i {temp_file_name} -s {cps_file}')
    os.system(f'rm {temp_file_name}')

    # return
    if os.path.exists(cps_file):
        return cps_file
    else:
        print(f'Copasi import did not work for model {temp_file_name}')


def _adapt_copasi_file(model_row, idx, cps_file, sbml_model_name, output_table):
    # create another cps file with some specifications altered
    f_in = open(cps_file, 'r')
    f_out = open(cps_file + '.temp', 'w')

    # read out info from dataframe
    n_timepoints = model_row.loc[idx, 'n_timepoints']
    start_time = model_row.loc[idx, 'start_time']
    end_time = model_row.loc[idx, 'end_time']
    time_step = (end_time - start_time) / (n_timepoints - 1)
    for line in f_in:
        if 'type="timeCourse" scheduled="false" updateModel="false"' in line:
            # schedule time course, i.e., execute if called from command line
            f_out.write(line.replace('scheduled="false"', 'scheduled="true"'))

        elif '<Parameter name="StepNumber" type="unsignedInteger" ' in line:
            # adapt number of output steps
            f_out.write(line.replace('value="100"', f'value="{n_timepoints}"'))

        elif '<Parameter name="StepSize" type="float"' in line:
            # adapt step size for output
            f_out.write(line.replace('value="0.01"', f'value="{time_step}"'))

        elif '<Parameter name="Duration" type="float" value="1"/>' in line:
            # adapt simulated time
            f_out.write(line.replace('value="1"',
                                     f'value="{end_time - start_time}"'))

        elif '<Parameter name="OutputStartTime" type="float"' in line:
            # adapt simulation start time
            f_out.write(line.replace('value="0"', f'value="{start_time}"'))

        elif '<Parameter name="Relative Tolerance" type="unsigned' in line:
            # adapt relative integration error tolerance
            f_out.write('<Parameter name="Relative Tolerance" '
                        'type="unsignedFloat" value="1.0e-06"/>\n')

        elif '<Parameter name="Absolute Tolerance" type="unsigned' in line:
            # adapt absolute integration error tolerance
            f_out.write('<Parameter name="Absolute Tolerance" '
                        'type="unsignedFloat" value="1.0e-06"/>\n')

        elif '<Parameter name="Max Internal Steps" type="unsigned' in line:
            # adpapt number of integration steps
            f_out.write(line.replace('value="100000"', 'value="10000"'))

        elif 'taskType="timeCourse" separator="&#x09;" precision="6"' in line:
            # make Copasi write a report file with species IDs and solution
            f_out.write(line)
            f_out.write(f'      <Table printTitle="1"> \n')
            f_out.write(f'\t\t<Object cn="CN=Root,Model={sbml_model_name},'
                        f'Reference=Time"/> \n')
            for output in output_table:
                f_out.write(f'\t\t<Object cn="CN=Root,Model={sbml_model_name},'
                            f'Vector=Compartments[{output[0]}],'
                            f'Vector=Metabolites[{output[1]}],'
                            f'Reference=Concentration"/> \n')
            f_out.write(f'\t\t<Object cn="CN=Root,Timer=CPU Time"/> \n')
            f_out.write(f'\t\t<Object cn="CN=Root,Timer=Wall Clock Time"/> \n')
            f_out.write(f'      </Table> \n')

        else:
            f_out.write(line)

    # close files
    f_out.close()
    f_in.close()
    # remove old file and replace by new
    os.system(f'rm {cps_file}')
    os.system(f'mv {cps_file}.temp {cps_file}')


# read and adapt .tsv file
model_info = pd.read_csv(os.path.join(DIR_MODELS, 'model_summary.tsv'),
                         sep='\t')
if 'copasi_path' not in model_info.keys():
    # add path to amici_model
    model_info = model_info.join(pd.Series([''] * model_info.shape[0],
                                           name='copasi_path'))

# check for COPASI installation
if os.system(os.path.join(DIR_COPASI_BIN, 'CopasiSE') + ' --help') != 0:
    raise Exception("Copasi seems to be not installed or the path toe the "
                    "Copasi binaries is not properly set in "
                    "Python_Scripts/C.py. Stopping.")

model_info = import_sbmls_in_copasi(model_info)

# save .tsv file
model_info.to_csv(
    path_or_buf=os.path.join(models_base_path, 'model_summary.tsv'),
    sep='\t', index=False)
