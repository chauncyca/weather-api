#!/usr/bin/python
import json
import datetime

today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
overmorrow = today + datetime.timedelta(days=2)

def getDailyWeather(jsonOneDay):
    return {"description": jsonOneDay["description"], "high": jsonOneDay["highTemperature"], "low": jsonOneDay["lowTemperature"]}

def getDate(jsonOneDay):
    return jsonOneDay["utcTime"][:10]

def getForecast(rawWeatherDump):
    jsonWeatherData = json.loads(str({}))
    dayList = rawWeatherDump["daily"]

    for day in dayList:
        jsonDay = str(getDate(day))
        if str(today) == jsonDay:
            jsonWeatherData["today"] = getDailyWeather(day)
        elif str(tomorrow) == jsonDay:
            jsonWeatherData["tomorrow"] = getDailyWeather(day)
        elif str(overmorrow) == jsonDay:
            jsonWeatherData["overmorrow"] = getDailyWeather(day)
    return jsonWeatherData

def parseData(rawWeatherDump):
    jsonToday = rawWeatherDump["today"]
    return {"state": jsonToday["state"], "city": jsonToday["city"], "day": str(today), "weather": getForecast(rawWeatherDump)}
