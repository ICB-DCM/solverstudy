"""Download all models from the JWS database"""

import os
import logging

from sedml_import import download_all_sedml_models_from_jws
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
            filename=os.path.join(DIR_BASE, "import_warnings_jws.log"))
logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.INFO)

# download all models
download_all_sedml_models_from_jws()
