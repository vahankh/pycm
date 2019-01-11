import logging
import requests
import json

from enum import Enum


class pycmMonitor(object):

    _api_endpoint = None
    _api_token = None

    class Type(Enum):
        CRITICAL = 'CRITICAL'
        ERROR = 'ERROR'
        WARNING = 'WARNING'
        INFO = 'INFO'
        DEBUG = 'DEBUG'

        def __str__(self):
            return str(self.value)


    @staticmethod
    def init(api_endpoint, api_token):
        print('init')
        pycmMonitor._api_endpoint = api_endpoint
        pycmMonitor._api_token = api_token

        print(pycmMonitor._api_endpoint)

    @staticmethod
    def report(name, message, type, params={}):
        post_data = {
            'process_name': name,
            'message': message,
            'type': str(type),
            'params': params
        }

        headers = {
            "x-pycm_api_token": pycmMonitor._api_token,
            "Content-Type": "application/json"
        }
        print(pycmMonitor._api_endpoint)
        print(json.dumps(post_data, indent=2))

        try:
            r = requests.post(pycmMonitor._api_endpoint + "/monitoring/report_message/", data=json.dumps(post_data),
                              headers=headers)
            logging.debug(r)
        except:
            return False

        return r

    @staticmethod
    def debug(name, message, params={}):
        return pycmMonitor.report(name, message, pycmMonitor.Type.DEBUG, params)

    @staticmethod
    def info(name, message, params={}):
        return pycmMonitor.report(name, message, pycmMonitor.Type.INFO, params)

    @staticmethod
    def warning(name, message, params={}):
        return pycmMonitor.report(name, message, pycmMonitor.Type.WARNING, params)

    @staticmethod
    def error(name, message, params={}):
        return pycmMonitor.report(name, message, pycmMonitor.Type.ERROR, params)

    @staticmethod
    def critical(name, message, params={}):
        return pycmMonitor.report(name, message, pycmMonitor.Type.CRITICAL, params)
