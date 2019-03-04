#!/usr/bin/python

import asyncio
import datetime
import threading
import websockets

import socketserver

from . import config
from . import handler

STAY_ALIVE = True

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
        with open(config.LOG_FILE, "a") as f:
            outstring = datetime.date.today() + ", " + city + ", " + state
            f.write(outstring)



##
# Class: JunoWebSocketServer
#        A simple to use websocket server that makes use of an event queue.
class JunoWebSocketServer(object):

    ##
    # Creates the event loop and starts the server.
    def serveForever(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop()
        serverStart = websockets.serve(self.handler, config.HOST, config.SOCKET_PORT)

    ##
    # Main server loop. Handles the send and receiving of message asyncronously.
    #
    # @param websocket Websocket to send and recv from.
    # @param path      Optional filepath paramater.
    #                  NOTE: Not currently in use.
    async def handler(self, websocket, path):
        # loop = asyncio.get_event_loop()
        eventHandler = JunoEventHandler(websocket)
        while STAY_ALIVE:
            listener = asyncio.ensure_future(eventHandler.getMessage())
            done, pending = await asyncio.wait(
                                        [listener], return_when=asyncio.FIRST_COMPLETED
                                        )
            if listener in done:
                await eventHandler.handleEvent()
            else:
                listener.cancel()

##
# Class: JunoEventHandler
#        Does the event handling for an instance of JunoWebSocketServer.
class JunoEventHandler(object):
    ##
    # Init required member variables.
    def __init__(self, websocket):
        self.websocket = websocket
        self.incoming = asyncio.Queue()
        self.outgoing = asyncio.Queue()

    ##
    # Retrieves message from the queue.
    #
    # @return Retrieved message.
    async def getMessage(self):
        rcvdMsg = await self.websocket.recv()
        await self.incoming.put(rcvdMsg)

    ##
    # Sends messages over the websocket.
    #
    # @param message Message to send.
    async def sendMessage(self, message):
        await self.websocket.send(message)

    ##
    # Main event handler.
    #      NOTE: Message handling should exist here.
    async def handleEvent(self):
        eventToHandle = await self.incoming.get()

        response = {}

        if eventToHandle["city"] and eventToHandle["state"]:
            self.log(eventToHandle["city"], eventToHandle["state"])
            response = handler.getWeather(eventToHandle)
        else:
            try:
                handler.updateCache(eventToHandle)
            # Blanket catch is used here because a messages other than
            # what we expect are a "don't care" state.
            except:
                pass
        self.sendMessage(response)

    ##
    # Adds Retrieves the outbound message queue.
    #   NOTE: Not currently in use.
    async def produce(self):
        return await self.outgoing.get()

    ##
    # Logs the date, city, and state where valid requests come from.
    #
    # @param city  City the requester is in.
    # @param state State the requester is in.
    def log(self, city, state):
        with open(config.LOG_FILE, "a") as f:
            outstring = datetime.date.today() + ", " + city + ", " + state
            f.write(outstring)


##
# Starts the websocket server and event queue.
def run():
    # server = socketserver.UDPServer((config.HOST, config.UDP_PORT), JunoListener)
    # server.serve_forever()
    server = JunoWebSocketServer()
    thread = threading.Thread(target=server.serveForever())
    thread.daemon = True
    thread.start()

    while STAY_ALIVE:
        asyncio.sleep(5)
