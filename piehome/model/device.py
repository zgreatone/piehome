__author__ = 'zgreatone'


class Device(object):
    def __init__(self, name, controller, controller_id, capabilities=[],
                 attributes={}):
        self.identifier = str(controller) + '-' + str(controller_id)
        self.name = name
        self.controller = controller
        self.controller_id = controller_id
        self.capabilities = capabilities
        self.attributes = attributes
