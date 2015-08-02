import logging as log
import os
import tornado.web
import tornado.escape
from tornado import gen
import simplejson as json
import database
from smarthome import main as smarthome


class AlexaHandler(tornado.web.RequestHandler):
    def check_xsrf_cookie(self):
        pass

    @gen.coroutine
    def get(self):
        log.debug("in AlexaHandler:get")
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        if not self.is_request_authorized():
            self.write({'speechOutput': "Invalid authorization Error when accessing home automation service"})
        else:
            response = self.handle_get_request()

            # json_output = json.dumps(response)

            # self.write(json_output)
            self.write(response)

    def handle_get_request(self):
        intent = self.get_argument("intent", None)
        response = AlexaHandler.get_response_object(intent)
        if intent == "GetStatus":
            response['speechOutput'] = "System is currently up and functional"
        elif intent == "GetSensorStatus":
            # perform command to get status of device
            self.handle_get_sensor_status_request(response)
        return response

    def handle_get_sensor_status_request(self, response):
        """
        Method handles request for getting status for motion sensor device.
        The result in converted to string put in the 'speechOutput' key
        of the response arg.
        :param response: dictionary to hold speech output
        :return:
        """
        device = self.get_argument("device")
        response['speechOutput'] = "The " + device + " sensor is currently enabled"

    @gen.coroutine
    def post(self):
        log.debug("in AlexaHandler:post")
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        if not self.is_request_authorized():
            self.write({'speechOutput': "Invalid authorization Error when accessing home automation service"})
        else:
            # TODO error check below in case body doest exists
            body = tornado.escape.to_basestring(self.request.body)

            body_json = json.loads(body)

            response = self.process_post_body(body_json)
            self.write(response)

    @staticmethod
    def process_post_body(body_json):
        """

        :param body_json:
        :return:
        """
        intent = body_json['intent']
        response = AlexaHandler.get_response_object(intent)
        if intent == "TurnOn":
            device = body_json['device']
            response['speechOutput'] = "In the near future I will turn on " + device + " ."
        elif intent == "TurnOff":
            device = body_json['device']
            response['speechOutput'] = "In the near future I will turn off " + device + " ."
        elif intent == "Arm":
            device = body_json['device']
            response['speechOutput'] = "In the near future I will arm " + device + " ."
        elif intent == "DisArm":
            device = body_json['device']
            response['speechOutput'] = "In the near future I will disarm " + device + " ."
        else:
            response['speechOutput'] = "I have no clue what you are trying to do"

        return response

    @staticmethod
    def get_response_object(intent):
        response = {}
        response['intent'] = intent
        return response

    def is_request_authorized(self):
        """
        Method to verify that api key is valid for query
        :return:
        """
        api_key = self.get_argument("api_key", None)
        if api_key is None:
            return False
        else:
            return True
