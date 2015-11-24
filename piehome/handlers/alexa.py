import tornado.web
import tornado.escape
import logging as log
import simplejson as json
from tornado import gen
import controller


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
                    current_device = devices[0]
                    log.debug("current device is [" + current_device.name + "]")
                    action_response = self._manager.perform_action(devices[0], intent)
                    if 'result' in action_response and action_response['result']:
                        AlexaSkillHandler.speechlet_response(response, "Done.", "", True, {})
                    else:
                        AlexaSkillHandler.speechlet_response(response,
                                                             "Error performing action on " + devices[0].name + " .",
                                                             "",
                                                             True,
                                                             {})

                except Exception as e:
                    log.error(e)
                    AlexaSkillHandler.speechlet_response(response,
                                                         "Error when trying to perform action on device" + device + " .",
                                                         "",
                                                         True,
                                                         {})
            elif device_count == 0:
                response['speechOutput'] = "No device found with name" + device + " ."
                AlexaSkillHandler.speechlet_response(response,
                                                     "No device found with name" + device + " .",
                                                     "",
                                                     True,
                                                     {})
            else:
                response['speechOutput'] = "Too many devices with name" + device + " ."
                AlexaSkillHandler.speechlet_response(response,
                                                     "Too many devices with name" + device + " .",
                                                     "Try again",
                                                     False,
                                                     {})

        elif intent == "ActivateScene":
            response['speechOutput'] = "In the near future I will activate a scene."
            response['shouldEndSession'] = True
        elif intent == "DeActivateScene":
            response['speechOutput'] = "In the near future I will deactivate a scene ."
            response['shouldEndSession'] = True
        elif intent == "NestMode":
            response['speechOutput'] = "In the near future I set mode on nest device."
            response['shouldEndSession'] = True
        elif intent == "NestLevel":
            response['speechOutput'] = "In the near future I set level on nest device."
            response['shouldEndSession'] = True
        elif intent == "NestStatus":
            response['speechOutput'] = "In the near future I will update status on nest device."
            response['shouldEndSession'] = True
        else:
            response['speechOutput'] = "I have no clue what you are trying to do"
            response['shouldEndSession'] = True

        return response

    @staticmethod
    def speechlet_response(response, speech_output, reprompt_text, should_end_session, session_attributes):
        response['speechOutput'] = speech_output
        response['repromptText'] = reprompt_text
        response['shouldEndSession'] = should_end_session
        response['sessionAttributes'] = session_attributes

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
    """
    Handler to support alexa light skill
    """

    def initialize(self, system_manager):
        self._manager = system_manager

    def check_xsrf_cookie(self):
        pass

    @gen.coroutine
    def get(self):
        log.debug("in AlexaLightHandler:get")
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        if not self.is_request_authorized():
            raise tornado.web.HTTPError(401)
        else:
            response = self.handle_get_request()

            self.write(response)

    def handle_get_request(self):
        """
        Get request to return all on and off capable devices
        :return:
        """
        namespace = self.get_argument("namespace", None)
        name = self.get_argument("name", None)
        response = AlexaLightHandler.get_response_object()

        if namespace == "Discovery":
            devices = self._manager.get_persisted_devices()
            appliances = []
            for d in devices:
                if 1 in d.capabilities or 2 in d.capabilities:
                    """
                    Make sure device on and off capability
                    """
                    appliance = self.get_appliance(d)
                    appliances.append(appliance)

            self.populate_response(response, True, appliances)
        else:
            # self.populate_response(response, False, "unknown namespace")
            raise tornado.web.HTTPError(400)

        return response

    @staticmethod
    def get_appliance(d):
        appliance = dict()
        appliance['applianceId'] = d.identifier
        appliance['manufacturerName'] = d.controller
        appliance['modelName'] = ''
        appliance['version'] = 1
        appliance['friendlyName'] = d.name
        appliance['friendlyDescription'] = d.name
        appliance['isReachable'] = True
        details = dict()
        details['controller_device_id'] = d.controller_device_id
        for key, value in d.attributes.items():
            details[key] = value
            if "manufacturer" == key:
                appliance['manufacturerName'] = value
            elif "model" == key:
                appliance['modelName'] = value
        appliance['additionalApplianceDetails'] = details
        return appliance

    @gen.coroutine
    def post(self):
        log.debug("in AlexaHandler:post")
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        if not self.is_request_authorized():
            raise tornado.web.HTTPError(401)
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
        response = AlexaLightHandler.get_response_object()

        event_header = body_json['header']
        event_payload = body_json['payload']

        namespace = event_header['namespace']
        name = event_header['name']

        if namespace == 'Control':
            if name == 'SwitchOnOffRequest':
                self._process_switch_on_off_request(event_payload, response)

            elif name == 'AdjustNumericalSettingRequest':
                log.debug('Control AdjustNumericalSetting Request received')
                raise tornado.web.HTTPError(501)
            else:
                # self.populate_response(response, False, 'Invalid control name')
                raise tornado.web.HTTPError(400)
        else:
            # self.populate_response(response, False, 'Unknown namespace')
            raise tornado.web.HTTPError(400)

        return response

    def _process_switch_on_off_request(self, event_payload, response):
        log.debug("Control SwitchOnOff Request received")
        device_id = event_payload['appliance']['applianceId']
        action = self._resolve_switch_control_action(event_payload['switchControlAction'])
        devices = self._manager.query_device_by_id(device_id)
        device_count = len(devices)
        log.debug(str(device_count) + " matching device with id [" + device_id + "]")
        if device_count == 1:
            try:
                action_response = self._manager.perform_action(devices[0], action)
                if 'result' in action_response and action_response['result']:
                    self.populate_response(response, True, {})
                else:
                    log.debug("performing action[" + action + "] on device[" + device_id + "] was unsuccessful")
                    raise Exception(
                        "performing action[" + action + "] on device[" + device_id + "] was unsuccessful")
            except Exception as e:
                log.error("error when processing switchonoff request")
                log.error(e)
                raise tornado.web.HTTPError(500)
        else:
            log.error("Either too many or no device found with  device id [" + device_id + "]")
            raise tornado.web.HTTPError(500)

    @staticmethod
    def populate_response(response, success, data):
        response['success'] = success
        response['data'] = data

    @staticmethod
    def get_response_object():
        response = {}
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

    @staticmethod
    def _resolve_switch_control_action(param):
        if param == "TURN_ON":
            return controller.POWER_ON
        elif param == "TURN_OFF":
            return controller.POWER_OFF
        else:
            return None
