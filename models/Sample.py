import logging

from core.piclModel import piclModel

class Sample(piclModel):

    def get_filtered(self, criteria):
        logging.info("Default implementation of the model")
