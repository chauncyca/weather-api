#!/usr/bin/python

from Juno import handler

print(handler.pollCacheForLocation({"state": "Texas", "city": "Fort Worth"}))