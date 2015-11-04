import logging as log
import controller as controller


import veralite

from controller.exceptions import MissingParameterError
from controller.exceptions import ControllerNotInitializedError
from controller.exceptions import UnsupportedActionError
from controller.exceptions import InvalidDeviceError


class VeraliteController(controller.Controller):
    """

    """

    def __init__(self):
        self._key = 'VERALITE'
        self._vera_api = None
        self._actions = set()
        self._actions.update(controller.capabilities[1].actions)
        self._actions.update(controller.capabilities[2].actions)
        self._actions.update(controller.capabilities[3].actions)

    @property
    def key(self):
        return self._key

    def get_config_arguments(self):
        config = {'ip': 'number', 'username': 'string', 'password': 'secure'}
        return config

    def initialize(self, **kwargs):
        log.debug("initializing vera controller")
        if 'ip' in kwargs and 'username' in kwargs and 'password' in kwargs:
            ip = kwargs['ip']
            username = kwargs['username']
            password = kwargs['password']

            self._vera_api = veralite.Veralite(ip, username, password)
            self._vera_api.update_devices()
            log.info("initialized vera controller")
        else:
            raise MissingParameterError("an initialize parameter is missing")

    @property
    def actions(self):
        return list(self._actions)

    def perform_action(self, device_id, action_code, action_arguments=None):
        """
        Method to perform action on device
        :param device_id: the device identifier
        :param action_code: the action to perform
        :param action_arguments: action arguments if required by action code
        :return:
        :raises ControllerNotInitializedError: when action is trying to be performed before initializing controller
        """
        if self._vera_api is None:
            raise ControllerNotInitializedError("controller has not been initialized")

        if action_code == controller.ON:
            response = self._handle_on_action(device_id)
        elif action_code == controller.OFF:
            response = self._handle_off_action(device_id)
        elif action_code == controller.ARM:
            response = self._handle_arm_action(device_id)
        elif action_code == controller.DISARM:
            response = self._handle_disarm_action(device_id)
        elif action_code == controller.BRIGHTNESS:
            response = self._handle_brightness_action(action_arguments, device_id)
        else:
            raise UnsupportedActionError("action[" + action_code + "] not supported")

        return response

    def _handle_brightness_action(self, action_arguments, device_id):
        if action_arguments is not None and "level" in action_arguments:
            level = action_arguments["level"]
        else:
            raise MissingParameterError("parameter ['level'] is missing for arguments")
        if device_id in self._vera_api.dimming_lights:
            device = self._vera_api.dimming_lights[device_id]
            response = self._vera_api.set_brightness_level_dimming_light(device, level)
        else:
            raise InvalidDeviceError("No Device with id[" + device_id + "] found")

        return response

    def _handle_disarm_action(self, device_id):
        if device_id in self._vera_api.motion_sensors:
            device = self._vera_api.motion_sensors[device_id]
            response = self._vera_api.disarm_motion_sensor(device)
        else:
            raise InvalidDeviceError("No Device with id[" + device_id + "] found")

        return response

    def _handle_arm_action(self, device_id):
        if device_id in self._vera_api.motion_sensors:
            device = self._vera_api.motion_sensors[device_id]
            response = self._vera_api.arm_motion_sensor(device)
        else:
            raise InvalidDeviceError("No Device with id[" + device_id + "] found")

        return response

    def _handle_off_action(self, device_id):
        if device_id in self._vera_api.dimming_lights:
            device = self._vera_api.dimming_lights[device_id]
            response = self._vera_api.turn_off_dimming_light(device)
        elif device_id in self._vera_api.switches:
            device = self._vera_api.switches[device_id]
            response = self._vera_api.turn_off_switch(device)
        else:
            raise InvalidDeviceError("No Device with id[" + device_id + "] found")

        return response

    def _handle_on_action(self, device_id):
        if device_id in self._vera_api.dimming_lights:
            device = self._vera_api.dimming_lights[device_id]
            response = self._vera_api.turn_on_dimming_light(device)
        elif device_id in self._vera_api.switches:
            device = self._vera_api.switches[device_id]
            response = self._vera_api.turn_on_switch(device)
        else:
            raise InvalidDeviceError("No Device with id[" + device_id + "] found")

        return response
