import logging as log
import os
import tornado.web
import simplejson as json
import database
from smarthome import main as smarthome


class AlexaHandler(tornado.web.RequestHandler):
    def get(self):
        log.debug("in AlexaHandler:get")
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        intent = self.get_argument("intent", None)

        response = {}
        response['intent'] = intent
        response['speechOutput'] = "System is currently up and functional"

        json_output = json.dumps(response)

        self.write(json_output)

    def post(self):
        log.debug("in AlexaHandler:post")
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write("{response: 'hello'}")
