# download all models from the JWS database

from sedml_import import *
from logging_util import *
import logging
import os


log_to_console(level=logging.INFO)
try:
    os.mkdir("../../Benchmarking_of_numerical_ODE_integration_methods/")
except OSError:
    print ("Creation of the directory ../../Benchmarking_of_numerical_ODE_integration_methods/ failed")
else:
    print ("Successfully created the directory ../../Benchmarking_of_numerical_ODE_integration_methods/")
log_to_file(level=logging.WARN, filename="../../Benchmarking_of_numerical_ODE_integration_methods/import_warnings.log")
logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.INFO)

# download all models
download_all_sedml_models_from_jws()
