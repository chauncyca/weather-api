#!/usr/bin/python
import json
import datetime

TODAY = datetime.date.today()
TOMORROW = TODAY + datetime.timedelta(days=1)
OVERMORROW = TODAY + datetime.timedelta(days=2)


##
# Returns one day's weather
#
# @param jsonOneDay Json string representing exactly one day of weather.
# @return           Description, high, and low for the day in json format.
def _getDailyWeather(jsonOneDay):
    return {"description": jsonOneDay["description"], "high": jsonOneDay["highTemperature"],
            "low": jsonOneDay["lowTemperature"]}


##
# Returns one day's date
#
# @param jsonOneDay Json string representing exactly one day of weather.
# @return           Utc date for the input day.
def _getDate(jsonOneDay):
    return jsonOneDay["utcTime"][:10]


##
# Returns a three day forecast.
#
# @param rawWeatherDump Raw json string returned from the Amazon weather api.
# @return               Three days of description, high, and low for the day in json format.
def _getForecast(rawWeatherDump):
    jsonWeatherData = json.loads(str({}))

    day = rawWeatherDump["today"]
    today = str(_getDate(day))

    if str(TODAY) == today:
        jsonWeatherData["today"] = _getDailyWeather(day)

    dayList = rawWeatherDump["daily"]
    for day in dayList:
        jsonDay = str(_getDate(day))
        if str(TOMORROW) == jsonDay:
            jsonWeatherData["tomorrow"] = _getDailyWeather(day)
        elif str(OVERMORROW) == jsonDay:
            jsonWeatherData["overmorrow"] = _getDailyWeather(day)
    return jsonWeatherData


##
# Returns a the Juno approved weather forecast.
#
# @param rawWeatherDump Raw json string returned from the Amazon weather api.
# @return               Forecasted weather in an easily parsable format.
def parseData(rawWeatherDump):
    jsonToday = rawWeatherDump["today"]
    return {"state": {jsonToday["state"]: {"city": {jsonToday["city"]: {"day": str(TODAY),
                                                                        "weather": _getForecast(rawWeatherDump)}}}}}
