#!/usr/bin/python

import json
import datetime

from . import parser

CACHE_LOCATION = "cache.json"

def isCurrent(stringDate):
    return str(datetime.date.today()) == stringDate

def findWeatherVals(jsonCache, searchData):
    for state, cityList in jsonCache["state"].items():
        if state == searchData["state"]:
            for city, values in cityList["city"].items():
                if city == searchData["city"]:
                    return values
    return {}

def pollCacheForLocation(searchData):
    with open(CACHE_LOCATION) as f:
        jsonCache = json.load(f)

    weatherData = findWeatherVals(jsonCache, searchData)

    if weatherData == {} or not isCurrent(weatherData["day"]):
        return {"dataIntegrity": False}
    else:
        return weatherData["weather"]

def updateCache(rawWeatherDump):
    parsedDump = parser.parseData(rawWeatherDump)

    for state, cityList in parsedDump["state"].items():
        for city, weatherData in cityList["city"].items():
             pass

    with open(CACHE_LOCATION) as f:
        data = json.load(f)

        if not json.dumps(data):
            data = parsedDump
        else:
            foundState = False
            for cachedState, cityList in data["state"].items():
                if cachedState == state:
                    foundState = True

            if not foundState:
                data["state"].update(parsedDump["state"])
            else:
                data["state"][state]["city"].update(parsedDump["state"][state]["city"])