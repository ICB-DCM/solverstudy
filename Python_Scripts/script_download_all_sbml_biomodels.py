"""Download specified models from the biomodels database"""

import logging
import pandas as pd
import os

from sbml_bio_import import (
    download_specified_models_from_biomodels,
    add_Froehlich2018, add_BioModels_Folder)
from logging_util import log_to_console, log_to_file, LOGGER_NAME
from C import DIR_BASE

try:
    os.mkdir(DIR_BASE)
except OSError:
    print(f"Creation of directory {DIR_BASE} failed")
else:
    print(f"Created directory {DIR_BASE}")

log_to_console(level=logging.INFO)
log_to_file(level=logging.WARN,
            filename=os.path.join(DIR_BASE, "import_warnings_biomodels.log"))
logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.INFO)

# all unique model identifications consisting of pairs of id and name
#  Remark: all ids at BioModels are unique and don't change over time
models = pd.DataFrame(columns=['model_id', 'model_name'], data=[])
model_ids = [
    'BIOMD0000000334', 'BIOMD0000000332', 'BIOMD0000000333', 'BIOMD0000000451',
    'BIOMD0000000161', 'BIOMD0000000070', 'BIOMD0000000560', 'BIOMD0000000574',
    'BIOMD0000000583', 'BIOMD0000000021', 'BIOMD0000000014', 'BIOMD0000000303',
    'BIOMD0000000568', 'BIOMD0000000611', 'BIOMD0000000147', 'BIOMD0000000559',
    'BIOMD0000000491', 'BIOMD0000000492', 'BIOMD0000000172', 'BIOMD0000000286',
    'BIOMD0000000293', 'BIOMD0000000488', 'BIOMD0000000504', 'BIOMD0000000634',
    'BIOMD0000000543', 'BIOMD0000000544', 'BIOMD0000000049', 'BIOMD0000000579',
    'BIOMD0000000151', 'BIOMD0000000397', 'BIOMD0000000469', 'BIOMD0000000472',
    'BIOMD0000000022', 'BIOMD0000000205', 'BIOMD0000000106', 'BIOMD0000000505']

model_names = [
    'Bungay2003', 'Bungay2006', 'Bungay2006a', 'Carbo2013',
    'Eungdamrong2007', 'Holzhutter2004', 'Hui2014', 'Lai2014',
    'Leber2015', 'Leloup1999', 'Levchenko2000a', 'Liu2011',
    'Mueller2015', 'Nayak2015', 'ODea2007', 'Ouzounoglou2014',
    'Pathak2013', 'Pathak2013a', 'Pritchard2002', 'Proctor2010',
    'Proctor2010a', 'Proctor2013', 'Proctor2013a', 'Proctor2013b',
    'Qi2013', 'Qi2013a', 'Sasagawa2005', 'Sengupta2015',
    'Singh2006', 'Sivakumar2011c', 'Smallbone2013d', 'Smallbone2013g',
    'Ueda2001', 'Ung2008', 'Yang2007', 'vanEunen2013']

# download all specified models
download_specified_models_from_biomodels(model_ids, model_names)

# add Froehlich model from github
add_Froehlich2018()

# create an additional folder consisting of all models form the BioModels
#  database (TODO remove)
add_BioModels_Folder(model_names)

