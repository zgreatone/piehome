import os
import tornado.web
import tornado.escape
import logging as log
import simplejson as json

from tornado import gen


class HomeHandler(tornado.web.RequestHandler):
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
