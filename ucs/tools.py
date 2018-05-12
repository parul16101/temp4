"""
Django tools for project ucs
"""
import os, json, shutil, threading, requests
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
def time_norm(time_string=""):
    from dateutil import parser
    try:
        d = parser.parse(time_string)
        return d.strftime("%Y-%m-%d")
    except:
        return ""
