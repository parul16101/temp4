"""
Django tools for project ucs
"""
import os, json, shutil, threading, requests
import datetime
from time import strftime, time
from ucs.settings import BASE_DIR
from django import db
db.reset_queries()

## Read configuration file.
# Function for reading configuration file stored at location "UCS\\static\\UCS\\configurations.json".
def readConfiguration(key):
    configurationLocation = os.path.join(BASE_DIR, "UCS\\static\\UCS\\configurations.json")
    with open(configurationLocation) as configuration_file:
        configurations = json.load(configuration_file)
        return configurations[key]

## Write to configuration file.
# Function for writing into configuration file stored at location "UCS\\static\\UCS\\configurations.json".
def writeConfiguration(key, value):
    configurationLocation = os.path.join(BASE_DIR, "UCS\\static\\UCS\\configurations.json")
    with open(configurationLocation, "w") as configuration_file:
        configurations = json.load(configuration_file)
        configurations[key] = value
        configuration_file.write(json.dumps(configurations))

## Generate Unified Timestamp.
# This function normalize any input type of time into the format "yyyy-mm-dd".
def date_norm(raw_date=""):
    from dateutil import parser
    try:
        d = parser.parse(raw_date)
        return d.strftime("%Y-%m-%d")
    except:
        return ""

# This function normalize any input type of time into the format "mm/dd/yyyy".
def date_by_slash(raw_date=""):
    from dateutil import parser
    try:
        d = parser.parse(raw_date)
        return d.strftime("%m/%d/%Y")
    except:
        return ""		
		
# This function attached "hours, minute, and seconds" to the input
def get_timestamp():
    now = datetime.datetime.now()
    return "%d:%d:%d"%(now.hour, now.minute, now.second)

# This function removes  "hours, minute, and seconds" from the input
def rmv_timestamp(raw_time=""):
    format_date = date_norm(raw_time)
    if not format_date:
        return ""
    else:
        time = raw_time.split("-")
        return date_norm("%s-%s-%s"%(time[0], time[1], time[2]))