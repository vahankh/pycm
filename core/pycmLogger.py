import logging
import logging.handlers

def init(log_file, log_level=logging.INFO):

    logging.basicConfig(level=logging.CRITICAL)
    logger = logging.getLogger()

    fh = logging.handlers.RotatingFileHandler(log_file, maxBytes=0, backupCount=10)
    fh.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)-15s %(levelname)-5s %(threadName)10s * %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.setLevel(log_level)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)
