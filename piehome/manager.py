import logging as log
import database
from controller.veralite_controller import VeraliteController
from controller.harmony_controller import HarmonyController
from model.device import Device

import controller


class SystemManager(object):
    def __init__(self, options):
        self._options = options
        self._connection = None
        self._controllers = None
        self._db_connection = database.get_connection()

    def initialize(self):
        self._controllers = dict()
        self._setup_vera_controller()
        self._setup_harmony_controller()

        database.initialize_database()

    def get_devices(self):
        devices = []

        for ctlr in self._controllers.values():
            devices.extend(ctlr.devices)

        return devices

    def query_device(self, device_name):
        devices = []

        with self._db_connection as con:
            query_string = "SELECT * FROM device where name LIKE '%" + str(
                device_name).lower() + "%' "
            cur = con.cursor()
            cur.execute(query_string)
            rows = cur.fetchall()
            if len(rows) > 0:
                for row in rows:
                    capabilities = self._get_device_capabilties(con, row['identifier'])
                    attributes = self._get_device_attributes(con, row['identifier'])
                    device = Device(row['name'], row['controller'], row['controller_device_id'],
                                    capabilities, attributes)
                    devices.append(device)

        return devices

    def perform_action(self, action, device):
        log.debug("perform action[" + action + "] on device[" + str(device.name) + "]")
        if self._support_action(device, action):
            ctlr = self._controllers[device.controller]
            response = ctlr.perform_action(device.controller_device_id, action)
            return response
        else:
            log.error("action[" + action + "] not supported on device[" + device.name + "] ")
            raise Exception("Action not supported on controller")

    @property
    def db_connection(self):
        return self._db_connection

    def _setup_vera_controller(self):
        vera_ctrl = VeraliteController()
        init_params = {
            'ip': str(self._options.vera_ip),
            'username': str(self._options.vera_auth_user),
            'password': str(self._options.vera_auth_password)
        }
        vera_ctrl.initialize(**init_params)
        self._controllers[vera_ctrl.key] = vera_ctrl

    @property
    def system_key(self):
        return self._options.system_key

    def _setup_harmony_controller(self):
        harmony_ctrl = HarmonyController()
        init_params = {
            'ip': str(self._options.harmony_ip),
            'email': str(self._options.harmony_email),
            'password': str(self._options.harmony_password),
            'port': str(self._options.harmony_port)
        }
        harmony_ctrl.initialize(**init_params)
        self._controllers[harmony_ctrl.key] = harmony_ctrl

    @staticmethod
    def _get_device_capabilties(con, device_identifier):
        capabilities = []
        query_string = "SELECT * FROM device_capabilty where device_capabilty.device_identifier='" + str(
            device_identifier) + "' "
        cur = con.cursor()
        cur.execute(query_string)
        rows = cur.fetchall()
        if len(rows) > 0:
            for row in rows:
                capabilities.append(row['capability'])

        return capabilities

    @staticmethod
    def _get_device_attributes(con, device_identifier):
        attributes = dict()
        query_string = "SELECT * FROM device_attribute where device_attribute.device_identifier='" + str(
            device_identifier) + "' "
        cur = con.cursor()
        cur.execute(query_string)
        rows = cur.fetchall()
        if len(rows) > 0:
            for row in rows:
                attributes[row['attribute_key']] = row['attribute_value']

        return attributes

    def _support_action(self, device, action):
        log.debug("checking action [" + action + "] support for device [" + device.name + "]")
        log.debug("device[" + device.name + "] has capabilities[" + str(device.capabilities) + "]")
        if (action is controller.POWER_ON or action is controller.POWER_OFF) and \
                (1 in device.capabilities or 2 in device.capabilities):
            return True
        elif action is controller.BRIGHTNESS and 2 in device.capabilities:
            return True
        elif (action is controller.ARM or action is controller.DISARM) and 3 in device.capabilities:
            return True
        elif action is controller.POWER_TOGGLE and 4 in device.capabilities:
            return True
        else:
            return False
