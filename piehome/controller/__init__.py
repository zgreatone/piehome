# -*- coding:utf-8 -*-

import abc


class Capability(object):
    """

    """

    def __init__(self, code, description="", actions=[]):
        self._code = code
        self._actions = actions
        self._description = description

    @property
    def code(self):
        return self._code

    @property
    def description(self):
        return self._description

    @property
    def actions(self):
        return self._actions


class Action(object):
    """

    """

    def __init__(self, code, description="", arguments=None):
        self._code = code
        self._description = description
        self._arguments = arguments

    @property
    def code(self):
        return self._code

    @property
    def description(self):
        return self._description

    @property
    def arguments(self):
        return self._description

        # create actions


ON = "ON"
OFF = "OFF"
ARM = "ARM"
DISARM = "DISARM"
BRIGHTNESS = "BRIGHTNESS"

_action_on = Action("ON", "Turn on Device Action")
_action_off = Action("OFF", "Turn on Device Action")
_action_brightness = Action("BRIGHTNESS", "Set Brightness Level of Device",
                            ["level"])
_action_arm = Action("ARM", "Arm on Sensor Device")
_action_disarm = Action("DISARM", "Disarm a Sensor Device")

actions = dict()
actions[_action_on.code] = _action_on
actions[_action_off.code] = _action_off
actions[_action_brightness.code] = _action_brightness
actions[_action_arm.code] = _action_arm
actions[_action_disarm.code] = _action_disarm


# create capabilities
_capability_switch = Capability(1, "can be switch on and off", [_action_on, _action_off])
_capability_dimming_light = Capability(2, "light can be switch on, switched off and brightness level modified",
                                       [_action_on, _action_off, _action_brightness])
_capability_sensor = Capability(3, "can be armed or disarmed", [_action_arm, _action_disarm])

capabilities = dict()
capabilities[_capability_switch.code] = _capability_switch
capabilities[_capability_dimming_light.code] = _capability_dimming_light
capabilities[_capability_sensor.code] = _capability_sensor


class Controller(object, metaclass=abc.ABCMeta):
    """

    """

    @property
    @abc.abstractmethod
    def key(self):
        raise NotImplementedError('users must define get_key to user this base class')

    @abc.abstractmethod
    def get_config_arguments(self):
        raise NotImplementedError('users must define get_config to use this base class')

    @abc.abstractmethod
    def initialize(self, **kwargs):
        raise NotImplementedError('users must define initialize to sue this base class')

    @property
    @abc.abstractmethod
    def actions(self):
        raise NotImplementedError('users must define initialize to use this base class')

    @property
    @abc.abstractmethod
    def perform_action(self, device_id, action_code, action_arguments=None):
        raise NotImplementedError('users must define perform_action to use this base class')
