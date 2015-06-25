import logging
import os
import tornado.httpserver
import tornado.ioloop
import tornado.web

from tornado.options import define, options, parse_command_line

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        logging.debug("started applicationff ff")
        logging.info(os.path.dirname(os.path.realpath(__file__)))
        self.write("Hello, world")


def main():
    parse_command_line()
    application = tornado.web.Application([
        (r"/", MainHandler),
    ],
        xsrf_cookies=True,
        debug=options.debug, )
    http_server = tornado.httpserver.HTTPServer(application, ssl_options={
        "certfile": os.path.join(os.path.dirname(os.path.realpath(__file__)), "ssl", "server.crt"),
        "keyfile": os.path.join(os.path.dirname(os.path.realpath(__file__)), "ssl", "server.key")
    })
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
