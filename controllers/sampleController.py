import logging

from core.pycmController import pycmController
from core.pycm import pycm

from config.database import MYSQL_DB

class sampleController(pycmController):

    def default(self, argument):
        """ Default Controller Action

        Arguments:
            argument (int) - Will expect --argument as command line input
            """
        logging.info("Processing CLI Request")

        mSample = pycm.loader.model("Sample", MYSQL_DB)
        sSample = pycm.loader.strategy("strategy1", "Sample", MYSQL_DB)

        mSample.get_filtered([])
        sSample.get_filtered([])

