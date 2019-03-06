#!/usr/bin/python

import http.server
import json
import logging
import datetime

from . import config
from . import handler


##
# Class: JunoHttpServer
#        extends http.server.BaseHTTPRequestHandler
#
#        Provides access to a simple HTTP server that handles GET requests and page views.
class JunoHttpServer(http.server.BaseHTTPRequestHandler):

    ##
    # Sets header data and the HTTP response code.
    def _setHeaders(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    ##
    # Prints JSON weather data to the webpage when accessed.
    def do_HEAD(self):
        self._returnData()

    ##
    # Responds to GET requests with JSON weather data.
    def do_GET(self):
        self._returnData()

    ##
    # Method to retrieve and write the data to the page.
    def _returnData(self):
        self._setHeaders()
        self.output = handler.getWeather()
        self.wfile.write(json.dumps(self.output).encode())

##
# Sets logging variables and starts the server.
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
    stopMsg = "Server Stops at %s" % str(datetime.datetime.now())
    logging.warning(stopMsg)
