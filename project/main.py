import logging as log
import os
import tornado.httpserver
import tornado.ioloop
import tornado.web
import simplejson as json
import sys
import database

from tornado.escape import utf8, _unicode
from tornado import gen
from tornado.options import define, options, parse_command_line, parse_config_file
from handlers import setup as handler_setup
from handlers import alexa as handler_alexa

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "smarthome"))

from smarthome import main as smarthome
from smarthome.main import CustomJSONEncoder

curr_dir = os.path.dirname(os.path.realpath(__file__))

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")
define("vera_ip", default='192.168.1.33', help="The local ip to the veralite")
define("vera_auth", default=False, help="if veralite requires authentication")
define("vera_auth_user", default=None, help="username if veralite requires authentication")
define("vera_auth_passwd", default=None, help="password if veralite requires authentication")
define("config_file_path", default=curr_dir+"/config.py", help="config file location")


class MainHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        log.debug("MainHandler")
        # lights = smarthome.list_lights()
        log.info(os.path.dirname(os.path.realpath(__file__)))
        # if isinstance(lights, dict):
        # lights = escape.json_encode(lights)
        # lights = json.dumps(lights, cls=CustomJSONEncoder)
        # self.set_header("Content-Type", "application/json; charset=UTF-8")
        # lights = utf8(lights)
        # self.write(lights)
        # motion_sensors = smarthome.retrieve_motion_sensor_data()
        # motion_sensors = json.dumps(motion_sensors, cls=CustomJSONEncoder)
        # self.write(motion_sensors);
        # scenes = smarthome.retrieve_scene_data()
        # scenes = json.dumps(scenes, cls=CustomJSONEncoder)
        # connection = database.get_connection()
        # self.write(scenes)
        # with connection:
        #     cur = connection.cursor()
        #     cur.execute("CREATE TABLE Cars(Id INT, Name TEXT, Price INT)")
        # m_value = smarthome.modify_motion_sensor_state(20, 1)
        # value = smarthome.get_light(36)
        # value = smarthome.modify_light_state(36, 0)
        self.write("hello world")


def set_env_variables():
    """
    set vera connection parameters as environment variables

    """
    vera_auth_user = str(options.vera_auth_user)
    vera_auth_passwd = str(options.vera_auth_passwd)
    vera_ip = str(options.vera_ip)
    vera_auth = str(options.vera_auth)

    # logging
    log.debug("vera ip: " + vera_ip)
    log.debug("vera auth enabled: " + vera_auth)
    log.debug("vera auth user: " + vera_auth_user)
    log.debug("vera auth password: " + vera_auth_passwd)

    # setting the as env variables
    os.environ["VERA_AUTH_USER"] = str(vera_auth_user)
    os.environ["VERA_AUTH_KEY"] = str(vera_auth_passwd)
    os.environ["VERA_AUTH"] = str(vera_auth)
    os.environ["VERA_IP"] = str(vera_ip)


def main():
    parse_command_line()
    parse_config_file(options.config_file_path)
    set_env_variables()
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/setup", handler_setup.SetupHandler),
        (r"/alexa", handler_alexa.AlexaHandler)
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
