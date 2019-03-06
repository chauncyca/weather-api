#!/usr/bin/python

import datetime
import json
import requests

from . import config
from . import parser


##
# Returns true if input date is today.
#
# @param stringDate String representation of utc date.
# @return           True if input matches today's date.
def _isCurrent(stringDate):
    return str(datetime.date.today()) == stringDate


##
# Returns the cached weather values for selected city.
#
# @param searchData Json string of city and state names.
#                   Format: {"city" : "Seattle", "state":"Washington"}
# @return           Found values if any.
#                   Format: {"day":"2019-03-02", "weather" {}}
def _findWeatherVals():
    with open(config.CACHE_LOCATION) as f:
        try:
            jsonCache = json.load(f)
        except json.decoder.JSONDecodeError:
            jsonCache = {}
    try:
        # Our cache is a set up in such a way that we support the addition of multiple states and cities in the future.
        # For now though, each is only one level deep.
        for state, cityList in jsonCache["state"].items():
            for city, data in cityList["city"].items():
                retval = data
                retval["state"] = state
                retval["city"] = city
                return retval
    except KeyError:
        return {}


##
# Polls the cache and returns forecast if available.
#
# @return           Found weather values if any exist.
#                   Format: {'today': {}, 'tomorrow': {}. 'overmorrow': {}}
def getWeather():
    weatherData = _findWeatherVals()

    # If we have no data || or our data is invalid || our data is out of date
    if (weatherData == {}) or ("day" not in weatherData) or (not _isCurrent(weatherData["day"])):
        # Poll the third party API for data and update the cache
        rawWeather = requests.get(config.WEATHER_API_URL)
        updateCache(rawWeather.json())

        # Read from the cache.
        weatherData = _findWeatherVals()

    # getWeather() is called only once per visitor so it is safe to log the visit here.
    # it is doubly convenient to do so as all useful data is exposed.
    log(weatherData["city"], weatherData["state"])
    # Return just the weather data
    return weatherData["weather"]

##
# Logs the date, city, and state where valid requests come from.
#
# @param city  City the requester is in.
# @param state State the requester is in.
def log(city, state):
    with open(config.LOG_FILE, "a") as f:
        outstring = "%s, %s, %s\n" % (str(datetime.date.today()), city, state)
        f.write(outstring)


##
# Updates the cache with new weather data.
#
# @param rawWeatherDump Raw json returned by Amazon's weather api.
def updateCache(rawWeatherDump):
    parsedDump = parser.parseData(rawWeatherDump)

    state = rawWeatherDump["today"]["state"]

    with open(config.CACHE_LOCATION, "r+") as f:
        data = {}
        try:
            data = json.load(f)
        # If the cache does not currently contain json data, this will fail.
        except json.decoder.JSONDecodeError:
            pass

        # If our value isn't garbage.
        if not json.dumps(data) or not data == {}:
            data = parsedDump
        else:
            # Flag for determining if we have already performed an operation.
            # If no operations are performed, we need to update the city data.
            updateCityFlag = True
            try:
                # To support a potential future iteration where we have multiple endpoints in multiple cities.
                for cachedState, cityList in data["state"].items():
                    if cachedState == state:
                        data["state"][state]["city"].update(parsedDump["state"][state]["city"])
                        updateCityFlag = False
            # Key errors mean that the "state" field does not exist. So we need to take our parsed data as our
            # new cache.
            except KeyError:
                data = parsedDump
                updateCityFlag = False
            # Update the weather for this city if it has not yet been updated.
            if updateCityFlag:
                data["state"].update(parsedDump["state"])

        # Write to the log.
        f.seek(0)
        f.write(json.dumps(data))
        f.truncate()
