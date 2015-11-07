import tornado.web
import tornado.escape
import logging as log
import simplejson as json

from tornado import gen


class DeviceHandler(tornado.web.RequestHandler):
    """

    """
    def initialize(self, system_manager):
        self._manager = system_manager

    def check_xsrf_cookie(self):
        pass

    @gen.coroutine
    def get(self):
        log.debug("in DeviceHandler:get")
        self.write("hello world")
