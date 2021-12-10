#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
try:
    from jinja2 import Template
    jinja = True
except:
    jinja = False
    print("could not import jinja2")
    pass
import base64
import requests
import datetime
import subprocess
from picamera import PiCamera

# config
stamp = datetime.datetime.now().strftime("%y%m%d-%H%M%S")
notes_url = "https://notes.julina.ch"
org_image = "/home/pi/nas/latest.jpg"
new_image = f"/home/pi/nas/{stamp}.jpg"
now = datetime.datetime.now()
weekday = now.isoweekday()
weekdays = (1,2,3,4,5)
script_path = os.path.abspath(".")
template_path = f"{script_path}/template.jinja2"

def check_path():
    if not os.path.exists(org_image):
        return False
    return True

# note data
def getData(ident):
  url = f"{notes_url}/{ident}"
  try:
    response = requests.get(url, timeout=5).json()
    return response["sys"]["sunset"], response["sys"]["sunrise"]
  except Exception as err:
    print(f"WARN: Could not get {ident} data: {err}")
    return None, None

def sunshine():
    sunset, sunrise = getData("weather")
    if sunrise and sunset:
        sun_am = datetime.datetime.fromtimestamp(sunrise) - datetime.timedelta(hours = 0.5)
        sun_pm = datetime.datetime.fromtimestamp(sunset) + datetime.timedelta(hours = 0.5)
        if now < sun_am:
            print(f"{now}: too early: {sun_am}")
            return False
        if now > sun_pm:
            print(f"{now}: too late: {sun_pm}")
            return False
    return True

def make_picture(location=org_image):
    camera = PiCamera()
    camera.resolution = (1920, 1080)
    camera.framerate = 10
    camera.zoom = (0.3,0.1,0.8,0.8)
    camera.start_preview()
    time.sleep(15)
    camera.capture(location)
    camera.stop_preview()

if __name__ == "__main__":

    if not check_path():
        sys.exit(1)

    if sunshine:
        make_picture()
        if weekday in weekdays:
            subprocess.run(f"sudo cp {org_image} {new_image}", shell=True)

        if jinja:
            stamp = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
            jinja2_template_string = open(template_path, 'r').read()
            template = Template(jinja2_template_string)
            html_template_string = template.render(timestamp=stamp)
            with open("/home/pi/nas/index.html", "w") as result_file:
                result_file.write(html_template_string)
