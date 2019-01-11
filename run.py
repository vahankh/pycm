#!/usr/bin/python3

import sys
import traceback

from core.pycmRouter import pycmRouter
from core.pycmMonitor import pycmMonitor
from core.pycmUtils import remove_non_ascii

# import core.pycmLogger as pycmLogger

from config import logging

# Just to clean no ascii characters from exception messages to be able to log the in couchbase or log files
# without a lot of conversions
def format_exc(limit=None, chain=True):
    return remove_non_ascii("".join(traceback.format_exception(*sys.exc_info(), limit=limit, chain=chain)))
traceback.format_exc = format_exc

# pycmRouter.log_file = logging.FILEPATH % sys.argv[1:2][0].replace("/", ".")
pycmRouter.log_file = logging.FILEPATH
pycmRouter.log_level = logging.LEVEL
pycmRouter.route(sys.argv[1:2], sys.argv[2:])

