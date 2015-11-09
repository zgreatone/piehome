import database

from controller.veralite_controller import VeraliteController
from controller.harmony_controller import HarmonyController


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

    def _setup_vera_controller(self):
        vera_ctrl = VeraliteController()
        init_params = {
            'ip': str(self._options.vera_ip),
            'username': str(self._options.vera_auth_user),
            'password': str(self._options.vera_auth_password)
        }
        vera_ctrl.initialize(**init_params)
        self._controllers[vera_ctrl.key] = vera_ctrl

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
