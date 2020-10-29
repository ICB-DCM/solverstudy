"""Download specified models from the biomodels database"""

import logging
import pandas as pd
import os

from sbml_bio_import import (
    download_specified_models_from_biomodels,
    add_Froehlich2018, add_BioModels_Folder)
from logging_util import log_to_console, log_to_file, LOGGER_NAME
from C import (
    DIR_BASE, BIOMODELS_MODEL_FILE, BIOMODELS_MODEL_SLUG_FILE,
    INCLUDE_FROEHLICH)

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

with open(BIOMODELS_MODEL_SLUG_FILE) as f:
    model_ids = f.readlines()
model_ids = [x.rstrip('\n') for x in model_ids]

with open(BIOMODELS_MODEL_FILE) as f:
    model_names = f.readlines()
model_names = [x.rstrip('\n') for x in model_names]

# download all specified models
download_specified_models_from_biomodels(model_ids, model_names)

# add Froehlich model from github
if INCLUDE_FROEHLICH == 'YES':
    add_Froehlich2018()

# create an additional folder consisting of all models form the BioModels
#  database (TODO remove)
add_BioModels_Folder(model_names)

