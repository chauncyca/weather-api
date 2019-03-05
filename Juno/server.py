#!/usr/bin/python

import asyncio
import datetime
import json
import logging
import threading
import websockets

from . import config
from . import handler

STAY_ALIVE = True

logging.basicConfig(filename=config.ERROR_LOG)


##
# Class: JunoWebSocketServer
#        A simple to use websocket server that makes use of an event queue.
class JunoWebSocketServer(object):

    ##
    # Creates the event loop and starts the server.
    def serveForever(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        serverStart = websockets.serve(self.handler, config.HOST, config.SOCKET_PORT)
        asyncio.get_event_loop().run_until_complete(serverStart)
        asyncio.get_event_loop().run_forever()

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
            listener = asyncio.ensure_future(eventHandler.getIncoming())
            sender = asyncio.ensure_future(eventHandler.getOutgoing())
            done, pending = await asyncio.wait(
                                        [listener, sender], return_when=asyncio.FIRST_COMPLETED
                                        )
            if listener in done:
                await eventHandler.handleEvent()
            else:
                listener.cancel()
            if sender in done:
                outboundMsg = sender.result()
                await eventHandler.sendMessage(outboundMsg)
            else:
                sender.cancel()


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
    async def getIncoming(self):
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

        logging.debug("eventToHandle: " + eventToHandle)

        response = {"action":"sendReq"}

        eventMessage = {}

        try:
            eventMessage = json.loads(eventToHandle)
        except json.decoder.JSONDecodeError as e:
            pass

        try:
            logging.debug("\neventMessage: " + str(eventMessage))

            # If the client asks for the weather AND we have a city AND we have a state, we can return the weather.

            if "action" in eventMessage and "city" in eventMessage and "state" in eventMessage:
                if eventMessage["action"] == "retrieve":
                    self.log(eventMessage["city"], eventMessage["state"])
                    response = handler.getWeather(eventMessage)
                else:
                    response = {"action": "failure"}
            elif not eventMessage == {}:
                handler.updateCache(eventMessage)
                response = {"action": "updatedCache"}
        # If we fail to parse a string, log the error and the input string.
        except Exception:
            logging.exception("\nReceived unexpected JSON data")
        await self.outgoing.put(json.dumps(response))

    ##
    # Adds Retrieves the outbound message queue.
    async def getOutgoing(self):
        return await self.outgoing.get()

    ##
    # Logs the date, city, and state where valid requests come from.
    #
    # @param city  City the requester is in.
    # @param state State the requester is in.
    def log(self, city, state):
        with open(config.LOG_FILE, "a") as f:
            outstring = str(datetime.date.today()) + ", " + city + ", " + state + "\n"
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
