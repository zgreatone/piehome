import time
import logging as log
import controller as controller

from pyharmony import auth
from pyharmony import client as harmony_client

import model.device as device

from controller.exceptions import MissingParameterError
from controller.exceptions import ControllerNotInitializedError
from controller.exceptions import UnsupportedActionError
from controller.exceptions import InvalidDeviceError
from controller.exceptions import SessionTokenError
from controller.exceptions import LoginTokenError


class HarmonyController(controller.Controller):
    """

    """

    def __init__(self):
        self._key = 'HARMONY'
        self._harmony_api = None
        self._actions = set()
        self._actions.update(controller.capabilities[1].actions)
        self._actions.update(controller.capabilities[4].actions)

    @property
    def key(self):
        return self._key

    def get_config_arguments(self):
        config = {'ip': 'number', 'email': 'string',
                  'password': 'secure', 'port': 'number'}
        return config

    def initialize(self, **kwargs):
        log.debug("initializing harmony controller")
        if 'ip' in kwargs and 'email' in kwargs \
                and 'password' in kwargs and 'port' in kwargs:
            ip = kwargs['ip']
            email = kwargs['email']
            password = kwargs['password']
            port = kwargs['port']

            self._harmony_api = MyHarmonyClient(email, password, ip, port)
            log.info("initialized harmony controller")
        else:
            raise MissingParameterError("an initialize parameter is missing")

    @property
    def actions(self):
        return list(self._actions)

    @property
    def devices(self):
        device_list = []
        devices = None
        with self._harmony_api as hapi:
            config = hapi.get_config()
            devices = config['device']

        if devices is not None:

            for d in devices:
                attributes = dict()
                attributes['manufacturer'] = d['manufacturer']
                attributes['type'] = d['type']
                attributes['model'] = d['model']
                attributes['id'] = d['id']
                capabilities = self._resolve_capabilities(d)
                my_device = device.Device(d['label'], self.key, d['id'],
                                          capabilities, attributes)

                device_list.append(my_device)

        return device_list

    def perform_action(self, device_id, action_code, action_arguments=None):
        """
        Method to perform action on device
        :param device_id: the device identifier
        :param action_code: the action to perform
        :param action_arguments: action arguments if required by action code
        :return:
        :raises ControllerNotInitializedError: when action is trying to be performed before initializing controller
        """
        pass

    @staticmethod
    def _resolve_capabilities(d):
        capabilities = []
        for item in d['controlGroup']:
            if item['name'] == 'Power':
                if len(item['function']) == 3:
                    capabilities.append(1)
                    capabilities.append(4)
                elif len(item['function']) == 1:
                    capabilities.append(4)

        return capabilities


class MyHarmonyClient(object):
    """
    Harmony Client Wrapper that incorporates handling login key and session key
    """

    def __init__(self, email, password, ip, port):
        self._email = email
        self._password = password
        self._ip = ip
        self._port = port
        self._client = None

    def __enter__(self):
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False

    def close(self):
        self._client.disconnect(send_close=True)
        self._client = None

    def initialize(self):
        session_token = self.login_to_logitech()
        self._client = harmony_client.HarmonyClient(session_token)
        self._client.connect(address=(self._ip, self._port),
                             use_tls=False, use_ssl=False)
        self._client.process(block=False)

        while not self._client.sessionstarted:
            time.sleep(0.1)

    def get_config(self):
        if self._client is None:
            raise Exception("MyHarmonyClient has not be initialized")

        return self._client.get_config()

    def power_off(self):
        if self._client is None:
            raise Exception("MyHarmonyClient has not be initialized")

        self._client.power_off()

    def start_activity(self, the_activity):
        """Connects to the Harmony and starts an activity"""
        if self._client is None:
            raise Exception("MyHarmonyClient has not be initialized")

        config = self._client.get_config()
        activities = config['activity']
        labels_and_ids = dict([(a['label'], a['id']) for a in activities])
        ids_and_labels = dict([(a['id'], a['label']) for a in activities])
        matching_labels = [label for label in list(labels_and_ids.keys())
                           if the_activity.lower() in label.lower()]
        matching_ids = [ids for ids in list(ids_and_labels.keys())
                        if the_activity.lower() in ids.lower()]
        if len(matching_labels) == 1:
            activity = matching_labels[0]
            log.debug("Found activity named %s (id %s)" % (activity,
                                                           labels_and_ids[activity]))
            self._client.start_activity(labels_and_ids[activity])
        elif len(matching_ids) == 1:
            activity = matching_ids[0]
            log.debug("Found activity named %s (label %s)" % (activity,
                                                              ids_and_labels[activity]))
            self._client.start_activity(activity)
        else:
            raise Exception("No Activity Found with name/id[" + the_activity + "]")

    def send_command(self, device_id, command):
        """
        send a simple command.
        """
        if self._client is None:
            raise Exception("MyHarmonyClient has not be initialized")

        self._client.send_command(device_id, command)

    def login_to_logitech(self):
        """
        :return: Session token that can be used to log in to the Harmony device.
        """
        token = auth.login(self._email, self._password)
        if not token:
            raise LoginTokenError('Could not get token from Logitech server.')

        session_token = auth.swap_auth_token(self._ip, self._port, token)
        if not session_token:
            raise SessionTokenError('Could not swap login token for session token.')

        return session_token
