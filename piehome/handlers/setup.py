import logging as log
import os
import tornado.web
import database
from smarthome import main as smarthome


def initialize_database():
    con = database.get_connection()
    try:
        with con:
            cur = con.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS 'light'(id INTEGER PRIMARY KEY not null, ctrl_device_id INT, controller TEXT, name TEXT, room INT);")
            cur.execute(
                "CREATE TABLE IF NOT EXISTS 'scene'(id INTEGER PRIMARY KEY not null, ctrl_device_id INT, controller TEXT, name TEXT, room INT);")
            cur.execute(
                "CREATE TABLE IF NOT EXISTS 'room'(id INTEGER PRIMARY KEY not null, ctrl_device_id INT, controller TEXT, name TEXT);")
            cur.execute(
                "CREATE TABLE IF NOT EXISTS 'motion_sensor'(id INTEGER PRIMARY KEY not null, ctrl_device_id INT, controller TEXT, name TEXT, room INT);")
    except Exception as e:
        log.exception(e)


def update_devices():
    update_room_table()
    update_light_table()
    update_motion_sensor_table()
    # motion_sensors = smarthome.retrieve_motion_sensor_data()


def update_room_table():
    log.debug("in update room table")
    rooms = smarthome.retrieve_room_data()
    con = database.get_connection()
    for room in rooms:
        with con:
            query_string = "SELECT * FROM room where ctrl_device_id=" + str(room["id"]) + " and controller='VERA'"
            cur = con.cursor()
            cur.execute(query_string)
            rows = cur.fetchall()
            if len(rows) == 0:
                insert_query_string = "INSERT INTO room (id, ctrl_device_id, controller, name) VALUES (null," + str(
                    room['id']) + ", 'VERA', '" + str(room['name']) + "');"
                cur.execute(
                    insert_query_string)
                log.debug("inserted room into " + room['name'] + " database")


def update_light_table():
    log.debug("in update ligh table")
    lights = smarthome.retrieve_light_data()
    con = database.get_connection()
    for light_id in lights:
        light = lights[light_id]
        with con:
            query_string = "SELECT * FROM light where ctrl_device_id=" + str(light.id) + " and controller='VERA'"
            cur = con.cursor()
            cur.execute(query_string)
            rows = cur.fetchall()
            if len(rows) == 0:
                query_string = "SELECT * FROM room where name='" + str(light.room) + "' and controller='VERA'"
                cur = con.cursor()
                cur.execute(query_string)
                rows = cur.fetchall()
                if len(rows) == 0:
                    room_id = -1
                else:
                    room_id = rows[0]['id']
                insert_query_string = "INSERT INTO light (id, ctrl_device_id, controller, name, room) VALUES (null," + str(
                    light.id) + ", 'VERA', '" + str(light.name) + "'," + str(room_id) + ");"
                cur.execute(
                    insert_query_string)
                log.debug("inserted light  '" + light.name + "' into database")


def update_motion_sensor_table():
    log.debug("in update motion table")
    motion_sensors = smarthome.retrieve_motion_sensor_data()
    con = database.get_connection()
    for motion_sensor_id in motion_sensors:
        motion_sensor = motion_sensors[motion_sensor_id]
        with con:
            query_string = "SELECT * FROM motion_sensor where ctrl_device_id=" + str(
                motion_sensor.id) + " and controller='VERA'"
            cur = con.cursor()
            cur.execute(query_string)
            rows = cur.fetchall()
            if len(rows) == 0:
                query_string = "SELECT * FROM room where name='" + str(motion_sensor.room) + "' and controller='VERA'"
                cur = con.cursor()
                cur.execute(query_string)
                rows = cur.fetchall()
                if len(rows) == 0:
                    room_id = -1
                else:
                    room_id = rows[0]['id']
                insert_query_string = "INSERT INTO motion_sensor (id, ctrl_device_id, controller, name, room) VALUES (null," + str(
                    motion_sensor.id) + ", 'VERA', '" + str(motion_sensor.name) + "'," + str(room_id) + ");"
                cur.execute(
                    insert_query_string)
                log.debug("inserted motion sensor  '" + motion_sensor.name + "' into database")


class SetupHandler(tornado.web.RequestHandler):
    def get(self):
        log.debug("in SetupHandler")
        initialize_database()
        update_devices()
        self.write("hello world")
