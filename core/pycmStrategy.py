import logging
import inspect

from core.pycm import pycm

from config.database import MMS_DB

class pycmStrategy(pycm):
    """
    Defines strategy for model classes and their implementations

    Usage:
    1. Add decorator `@pycmStrategy._strategy` before model function definition.
    2. Add strategy directory in the models folder if doesn't exist
    3. Add model and class into that directory
    """

    isp_id = None
    md_id = None

    strategies = {}

    def _strategy(fnc):
        def magic(*args, **kwargs):

            logging.debug("Looking for strategy implementations for `%s.%s`" % (type(args[0]).__name__, fnc.__name__))
            # logging.debug(type(args[0]).__name__)
            # logging.debug(fnc.__name__)
            # logging.debug(kwargs)
            """ Begin parsing arguments and looking for isp_id and md_id """
            signatureParams = inspect.signature(fnc).parameters
            i = 0
            # check positional arguments
            for name, param in signatureParams.items():
                try:
                    if name == 'isp_id':
                        pycmStrategy.isp_id = args[i]
                    if name == 'md_id':
                        pycmStrategy.md_id = args[i]
                    i += 1
                except IndexError:
                    break

            # check keyword arguments
            if 'isp_id' in kwargs:
                pycmStrategy.isp_id = kwargs['isp_id']

            if 'md_id' in kwargs:
                pycmStrategy.md_id = kwargs['md_id']
            """ End argument parsing """

            # Check if strategy has been loaded already
            if not pycmStrategy.isp_id is None and not pycmStrategy.md_id is None:
                key = "%d-%d" % (pycmStrategy.isp_id, pycmStrategy.md_id)
                if not key in pycmStrategy.strategies:
                    mMd = pycmStrategy.loader.model("Md", MMS_DB)
                    pycmStrategy.strategies[key] = mMd.get_warming_strategy(pycmStrategy.isp_id, pycmStrategy.md_id)
            elif not pycmStrategy.isp_id:
                key = "%d" % (pycmStrategy.isp_id)
                if not key in pycmStrategy.strategies:
                    mIsp = pycmStrategy.loader.model("mIsp", MMS_DB)
                    pycmStrategy.strategies[key] = mIsp.get_warming_strategy(pycmStrategy.isp_id)

            if pycmStrategy.strategies[key] is None:
                logging.debug("No strategy found. Go to default implementation")
                return fnc(*args, **kwargs)

            logging.debug("Strategy `%s` found. Check for method implemention" % pycmStrategy.strategies[key])
            model_name = args[0].__class__.__name__;
            sMd = pycm.loader.strategy(pycmStrategy.strategies[key], model_name, MMS_DB)

            if not hasattr(sMd, fnc.__name__) or not callable(getattr(sMd, fnc.__name__)):
                logging.info("Method `%s` is not implemented in `%s` strategy. Loading default implementation"
                             % (fnc.__name__, pycmStrategy.strategies[key]))
                return fnc(*args, **kwargs)

            s_method = getattr(sMd, fnc.__name__)

            args = args[1:]

            logging.debug("Implementation `%s` is found in strategy `%s`" % (fnc.__name__, pycmStrategy.strategies[key]))
            return s_method(*args, **kwargs)

        return magic
