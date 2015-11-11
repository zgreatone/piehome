import tornado.web
import tornado.escape
import logging as log
import simplejson as json

from tornado import gen


class AlexaSkillHandler(tornado.web.RequestHandler):
    """
    Handler responsible for responding to alexa home_automation skill requests
    """

    def initialize(self, system_manager):
        self._manager = system_manager

    def check_xsrf_cookie(self):
        pass

    @gen.coroutine
    def get(self):
        log.debug("in AlexaSkillHandler:get")
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
        response = AlexaSkillHandler.get_response_object(intent)
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

            log.debug("message from: " + body)

            body_json = json.loads(body)

            response = self.process_post_body(body_json)
            self.write(response)

    def process_post_body(self, body_json):
        """

        :param body_json:
        :return:
        """
        intent = body_json['intent']
        log.debug("intent=" + intent + " received")
        response = AlexaSkillHandler.get_response_object(intent)
        if intent == "PowerOn" or intent == "PowerOff" or intent == "PowerToggle" \
                or intent == "Arm" or intent == "DisArm":
            device = body_json['device']
            log.debug("asking to perform action=" + intent + "on device=" + device)

            devices = self._manager.query_device(device)

            device_count = len(devices)
            log.debug(str(device_count) + " matching device with name [" + device + "]")
            if device_count == 1:
                try:
                    action_response = self._manager.perform_action(devices[0], intent)
                    if 'result' in action_response and action_response['result']:
                        response['speechOutput'] = "Done."
                    else:
                        response['speechOutput'] = "Error performing action on " + devices[0].name + " ."

                except Exception as e:
                    log.error(e)
                    response['speechOutput'] = "Error when trying to perform action on device" + device + " ."
            elif device_count == 0:
                response['speechOutput'] = "No device found with name" + device + " ."
            else:
                response['speechOutput'] = "Too many devices with name" + device + " ."

        elif intent == "ActivateScene":
            response['speechOutput'] = "In the near future I will activate a scene."
        elif intent == "DeActivateScene":
            response['speechOutput'] = "In the near future I will deactivate a scene ."
        elif intent == "NestMode":
            response['speechOutput'] = "In the near future I set mode on nest device."
        elif intent == "NestLevel":
            response['speechOutput'] = "In the near future I set level on nest device."
        elif intent == "NestStatus":
            response['speechOutput'] = "In the near future I will update status on nest device."
        else:
            response['speechOutput'] = "I have no clue what you are trying to do"

        return response

    @staticmethod
    def get_response_object(intent):
        response = dict()
        response['intent'] = intent
        return response

    def is_request_authorized(self):
        """
        Method to verify that api key is valid for query
        :return:
        """
        api_key = self.get_argument("api_key", None)
        if api_key is None or api_key != self._manager.system_key:
            return False
        else:
            return True


class AlexaLightHandler(tornado.web.RequestHandler):
    def initialize(self, system_manager):
        self._manager = system_manager

    def check_xsrf_cookie(self):
        pass

    @gen.coroutine
    def get(self):
        log.debug("in AlexaLightHandler:get")
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
        response = AlexaLightHandler.get_response_object(intent)
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

            log.debug("message from: " + body)

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
        response = AlexaLightHandler.get_response_object(intent)
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
