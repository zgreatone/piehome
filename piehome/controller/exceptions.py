#!/usr/bin/python
"""Python Veralite™
   Okpe Pessu <opessu@zgreatone.net>

   Module holding exceptions
"""


class UnsupportedActionError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class MissingParameterError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class ControllerNotInitializedError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class InvalidDeviceError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)