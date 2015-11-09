import logging as log
import tornado.web


class SetupHandler(tornado.web.RequestHandler):
    """

    """

    def initialize(self, system_manager, db_connection):
        self._system_manager = system_manager
        self._db_connection = db_connection

    def get(self):
        log.debug("in SetupHandler")

        self._update_devices()
        self.write("hello world")

    def _update_devices(self):
        log.debug("updating device")
        all_devices = self._system_manager.get_devices()
        with self._db_connection as con:
            for d in all_devices:
                self._update_device(con, d)
                self._update_device_capability(con, d)
                self._update_device_attribute(con, d)
                log.debug("device update complete")

    @staticmethod
    def _update_device(con, d):
        query_string = "SELECT * FROM device where identifier='" + str(
            d.identifier) + "' and controller='" + str(d.controller) + "'"
        cur = con.cursor()
        cur.execute(query_string)
        rows = cur.fetchall()
        if len(rows) == 0:
            insert_query_string = "INSERT INTO device (" \
                                  "identifier, name, controller, controller_device_id) " \
                                  "VALUES ( '" + str(d.identifier) + "', '" + str(d.name) + "', '" + \
                                  str(d.controller) + "', '" + str(d.controller_device_id) + "' );"
            cur.execute(insert_query_string)
            log.debug("inserted device  '" + d.name + "' into database")

    @staticmethod
    def _update_device_capability(con, d):
        for c in d.capabilities:
            query_string = "SELECT * FROM device_capabilty where device_identifier='" + str(
                d.identifier) + "' and capability=" + str(c) + ""
            cur = con.cursor()
            cur.execute(query_string)
            rows = cur.fetchall()
            if len(rows) == 0:
                insert_query_string = "INSERT INTO device_capabilty (" \
                                      "device_identifier, capability) " \
                                      "VALUES ( '" + str(d.identifier) + "', " + str(c) + " );"
                cur.execute(insert_query_string)
                log.debug("inserted device '" + d.name + "' capability " + str(c) + " into database")

    @staticmethod
    def _update_device_attribute(con, d):
        for key, value in d.attributes.items():
            query_string = "SELECT * FROM device_attribute where device_identifier='" + \
                           str(d.identifier) + "' and attribute_key='" + str(key) + \
                           "' and attribute_value='" + str(value) + "'"
            cur = con.cursor()
            cur.execute(query_string)
            rows = cur.fetchall()
            if len(rows) == 0:
                insert_query_string = "INSERT INTO device_attribute (" \
                                      "device_identifier, attribute_key, attribute_value) " \
                                      "VALUES ( '" + str(d.identifier) + "', '" + str(key) + \
                                      "', '" + str(value) + "' );"
                cur.execute(insert_query_string)
                log.debug("inserted device '" + d.name + "' attribute " + str(key) + " into database")
