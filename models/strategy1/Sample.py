import logging
from core.piclModel import piclModel

class Sample(piclModel):

    def get_filtered(self, criteria):
        logging.info("Strategy 1 implementation of the model")
