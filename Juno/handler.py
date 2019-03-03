#!/usr/bin/python

import json
import datetime

from . import parser

CACHE_LOCATION = "cache.json"

##
# Returns true if input date is today.
#
# @param stringDate String representation of utc date.
# @return           True if input matches today's date.
def isCurrent(stringDate):
    return str(datetime.date.today()) == stringDate

##
# Returns the cached weather values for selected city.
#
# @param jsonCache  Data read from the cache, will be searched through.
# @param searchData Json string of city and state names.
#                   Format: {"city" : "Seattle", "state":"Washington"}
# @return           Found values.
#                   Format: {"day":"2019-03-02", "weather" {}}
def findWeatherVals(jsonCache, searchData):
    for state, cityList in jsonCache["state"].items():
        if state == searchData["state"]:
            for city, values in cityList["city"].items():
                if city == searchData["city"]:
                    return values
    return {}

##
# Polls the cache and returns weather data if available.
#
# @param searchData Json string of city and state names.
#                   Format: {"city" : "Seattle", "state":"Washington"}
# @return           Found values if any exist.
#                   Format: {"day":"2019-03-02", "weather" {}}
def pollCacheForLocation(searchData):
    with open(CACHE_LOCATION) as f:
        jsonCache = json.load(f)

    weatherData = findWeatherVals(jsonCache, searchData)

    if weatherData == {} or not isCurrent(weatherData["day"]):
        return {}
    else:
        return weatherData["weather"]

##
# Updates the cache with new weather data.
#
# @param rawWeatherDump Raw json returned by Amazon's weather api.
def updateCache(rawWeatherDump):
    parsedDump = parser.parseData(rawWeatherDump)

    # Find the name of the state we will be updating.
    # There will only be one "state" in our json dict.
    # All other information is a "don't care" state at this time.
    for state in parsedDump["state"]:
         pass

    with open(CACHE_LOCATION, "r+") as f:
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
        f.seek(0)
        f.write(json.dumps(data))
        f.truncate()
