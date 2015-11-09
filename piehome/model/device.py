__author__ = 'zgreatone'


class Device(object):
    def __init__(self, name, controller, controller_device_id, capabilities=[],
                 attributes={}):
        self.identifier = str(controller) + '-' + str(controller_device_id)
        self.name = name
        self.controller = controller
        self.controller_device_id = controller_device_id
        self.capabilities = capabilities
        self.attributes = attributes
