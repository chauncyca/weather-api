#!/usr/bin/python

import datetime
import socketserver

from . import handler

HOST = "127.0.0.1"
UDP_PORT = 55400

STAY_ALIVE = True
LOG_FILE = "visitors.txt"


##
# Class: JunoListener extends socketserver.BaseRequestHandler
#        Provides a synchronous queue and handling of incoming events.
class JunoListener(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0]
        socket = self.request[1]

        response = {}

        if data["city"] and data["state"]:
            response = handler.getWeather(data)
        else:
            try:
                handler.updateCache(data)
            # Blanket catch is used here because a messages other than
            # what we expect are a "don't care" state.
            except:
                pass

        socket.sendto(response, self.client_address)

    def log(self, city, state):
        with open(LOG_FILE, "a") as f:
            outstring = datetime.date.today() + ", " + city + ", " + state
            f.write(outstring)


def run():
    server = socketserver.UDPServer((HOST, UDP_PORT), JunoListener)
    server.serve_forever()
