"""
Django tools for project ucs


import sys
sys.path

import os, json, shutil, threading, requests
from osgeo import gdal
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


http://stackoverflow.com/questions/68477/send-file-using-post-from-a-python-script


## Generate a Keyword Weight List.
# This function accepts the pulication location as input and returns the "Keyword Weight list".
def kwGenerator(publication_location):
    # might need to change to \\ for windows
    fname = publication_location[publication_location.rindex(os.path.sep)+1:]
    keyword_weightList = None
    with open(publication_location, 'rb') as f:
        keyword_weightList = requests.post(
            'http://128.194.140.230:8889/get_signature',
            data={'fname':fname},
            files={fname: f})
    return json.loads(keyword_weightList.text)
"""
