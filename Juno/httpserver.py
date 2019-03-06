#!/usr/bin/python

import http.server
import json
import logging
import datetime

from . import config
from . import handler


class JunoHttpServer(http.server.BaseHTTPRequestHandler):
    def _setHeaders(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_HEAD(self):
        self._returnData()

    def do_GET(self):
        self._returnData()

    def _returnData(self):
        self._setHeaders()
        self.output = handler.getWeather()
        self.wfile.write(json.dumps(self.output).encode())

def run():
    logging.basicConfig(filename=config.ERROR_LOG)
    serverClass = http.server.HTTPServer
    httpd = serverClass((config.HOST, config.PORT), JunoHttpServer)

    try:
        httpd.serve_forever()
    # If we intentionally disable the server, do nothing.
    except KeyboardInterrupt:
        pass
    # If the server crashes suddenly, log it.
    except:
        logging.exception("Unresolved exception, Juno Server failure.")
    httpd.server_close()
    logging.log("Server Stops at %s" % str(datetime.date.today()))
