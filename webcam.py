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

# check
if not os.path.exists(org_image):
  sys.exit(1)

# note data
def getData(ident):
  url = f"{notes_url}/{ident}"
  try:
    response = requests.get(url, timeout=5).json()
    return response["sys"]["sunset"], response["sys"]["sunrise"]
  except Exception as err:
    print(f"WARN: Could not get {ident} data: {err}")
    return None, None

sunset, sunrise = getData("weather")
if sunrise and sunset:
    sun_am = datetime.datetime.fromtimestamp(sunrise) - datetime.timedelta(hours = 0.5)
    sun_pm = datetime.datetime.fromtimestamp(sunset) + datetime.timedelta(hours = 0.5)
    if now < sun_am:
        sys.exit(1)
    if now > sun_pm:
        sys.exit(1)

camera = PiCamera()
camera.resolution = (1920, 1080)
camera.framerate = 10
camera.zoom = (0.3,0.1,0.8,0.8)
camera.start_preview()

time.sleep(15)

camera.capture(org_image)
camera.stop_preview()

if weekday in weekdays:
    subprocess.run(f"sudo cp {org_image} {new_image}", shell=True)

if jinja:
    stamp = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    jinja2_template_string = open(template_path, 'r').read()
    template = Template(jinja2_template_string)
    html_template_string = template.render(timestamp=stamp)
    with open("/home/pi/nas/index.html", "w") as result_file:
        result_file.write(html_template_string)
