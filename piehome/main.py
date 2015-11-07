import logging as log
import os
import tornado.httpserver
import tornado.ioloop
import tornado.web
import sys

from manager import SystemManager

from tornado.options import define, options, parse_command_line, parse_config_file

from handlers import home as handler_home
from handlers import device as handler_device
from handlers import alexa as handler_alexa

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "piehome"))

curr_dir = os.path.dirname(os.path.realpath(__file__))

_default_config_file = os.path.sep.join(('~', '.config', 'piehome', 'config.py'))
if not os.path.exists(_default_config_file):
    _default_config_file = os.path.sep.join((curr_dir, "config.py"))

define("port", default=8443, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")
define("vera_ip", default='192.168.1.33', help="The local ip to the veralite")
define("vera_auth_user", default=None, help="username if veralite requires authentication")
define("vera_auth_password", default=None, help="password if veralite requires authentication")
define("harmony_ip", default='192.168.1.33', help="The local ip to the harmony hub")
define("harmony_email", default=None, help="harmony user email")
define("harmony_password", default=None, help="harmony password")
define("harmony_port", default=5222, help="harmony port", type=int)
define("config_file_path", default=_default_config_file, help="config file location")


def main():
    parse_command_line()
    parse_config_file(options.config_file_path)

    log.info("Starting piehome")
    system_manager = SystemManager(options)

    system_manager.initialize()
    d = system_manager.get_devices()

    application = tornado.web.Application([
        (r"/", handler_home.HomeHandler),
        (r"/device", handler_device.DeviceHandler, {'system_manager': system_manager}),
        (r"/alexa_skill", handler_alexa.AlexaSkillHandler, {'system_manager': system_manager}),
        (r"/alexa_light", handler_alexa.AlexaLightHandler, {'system_manager': system_manager})
    ],
        cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        xsrf_cookies=True,
        debug=options.debug)
    http_server = tornado.httpserver.HTTPServer(application, ssl_options={
        "certfile": os.path.join(os.path.dirname(os.path.realpath(__file__)), "ssl", "server.crt"),
        "keyfile": os.path.join(os.path.dirname(os.path.realpath(__file__)), "ssl", "server.key")
    })
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
