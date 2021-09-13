#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
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
if sunrise:
    now = datetime.datetime.now()
    sun = datetime.datetime.fromtimestamp(sunrise) - datetime.timedelta(hours = 0.5)
    if now < sun:
        print(f"WARN: too dark, we can't see nothing!")
        sys.exit(1)

camera = PiCamera()
camera.resolution = (1920, 1080)
camera.framerate = 10
camera.zoom = (0.3,0.1,0.8,0.8)
camera.start_preview()

time.sleep(15)

camera.capture(org_image)
camera.stop_preview()

subprocess.run(f"sudo cp {org_image} {new_image}", shell=True)
