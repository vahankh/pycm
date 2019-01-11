import logging
import copy

from importlib import import_module


class pycm(object):

    _id = 0

    @staticmethod
    def id():
        return pycm._id

    # Internal class for loading models and other objects
    class loader(object):

        models = {}
        buckets = {}
        strategies = {}
        controllers = {}

        @staticmethod
        def model(model_name, db_config):

            if model_name in pycm.loader.models:
                return pycm.loader.models[model_name]

            try:
                ctrl_module = import_module("models.%s" % model_name)
            except ModuleNotFoundError:
                logging.error("Model `%s` not found" % model_name)
                return False

            mdl_class = getattr(ctrl_module, model_name)
            mdl_object = mdl_class(db_config)
            pycm.loader.models[model_name] = mdl_object

            return mdl_object

        @staticmethod
        def helper(helper_name, db_config):

            if helper_name in pycm.loader.models:
                return pycm.loader.models[helper_name]

            try:
                ctrl_module = import_module("helpers.%s" % helper_name)
            except ModuleNotFoundError:
                logging.error("Model `%s` not found" % helper_name)
                return False

            mdl_class = getattr(ctrl_module, helper_name)
            mdl_object = mdl_class(db_config)
            pycm.loader.models[helper_name] = mdl_object

            return mdl_object

        @staticmethod
        def strategy(strategy_name, model_name, db_config):

            if strategy_name in pycm.loader.strategies:
                if model_name in pycm.loader.strategies[strategy_name]:
                    return pycm.loader.strategies[strategy_name][model_name]
            else:
                pycm.loader.strategies[strategy_name] = {}

            try:
                ctrl_module = import_module("models.%s.%s" % (strategy_name, model_name))
            except ModuleNotFoundError:
                logging.error("Model `%s` not found for strategy `%s`" % (model_name, strategy_name))
                return False

            mdl_class = getattr(ctrl_module, model_name)
            mdl_object = mdl_class(db_config)
            pycm.loader.strategies[strategy_name][model_name] = mdl_object

            return mdl_object

        @staticmethod
        def bucket(bucket_name, db_config, init_config=None):

            if bucket_name in pycm.loader.buckets:
                return pycm.loader.buckets[bucket_name]

            try:
                ctrl_module = import_module("buckets.%s" % bucket_name)
            except ModuleNotFoundError:
                logging.error("Bucket `%s` not found" % bucket_name)
                return False

            bkt_class = getattr(ctrl_module, bucket_name)

            # creds = [{"user": value['bucket_name'], "pass": value['bucket_pass']} for key, value in
            #          db_config["creds"].items()]

            bucket_name = db_config["buckets"][bucket_name.lower()]
            meta_config = copy.copy(db_config)
            del meta_config["buckets"]

            if init_config is None:
                # bkt_object = bkt_class(db_config['host'], **db_config["creds"][bucket_name.lower()], creds=creds)
                bkt_object = bkt_class(bucket_name, **meta_config)
            else:
                # config_data = db_config["creds"][bucket_name.lower()]
                meta_config.update(init_config)
                bkt_object = bkt_class(bucket_name, **meta_config)

            pycm.loader.buckets[bucket_name] = bkt_object

            return bkt_object

        @staticmethod
        def controller(controller_name):

            if controller_name in pycm.loader.controllers:
                return pycm.loader.controllers[controller_name]

            try:
                ctrl_module = import_module("controllers.%sController" % controller_name.lower())
            except ModuleNotFoundError:
                logging.error("Controller `%s` not found" % controller_name)
                return False

            ctrl_class = getattr(ctrl_module, "%sController" % controller_name.lower())
            ctrl_object = ctrl_class()
            pycm.loader.controllers[controller_name] = ctrl_object

            return ctrl_object

