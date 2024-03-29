#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime, subprocess, random, time, os

url        = ""
weekdays   = (1,2,3,4,5)
weekends   = (6,7)
lightpower = "01:01:52:b1:d8"
aquapower  = "01:01:52:ad:cf"
aqua2power = "01:01:52:c5:d3"
finallog   = ""
tv_dns     = "192.168.1.99"
rain       = False
thunder    = False
snow       = False
now        = datetime.datetime.now()
hour       = now.hour
minute     = now.minute
weekday    = now.isoweekday()
log        = str(hour).zfill(2) + ":" + str(minute).zfill(2)

def getData(obj):
  url = "https://notes.julina.ch/%s" % obj
  try:
    import requests
    try:  
      response = requests.get(url, timeout=5)
      return response.json()
    except: 
      print(log + u": Could not get any weather data!")
  except:
    print("Could not load requests library!")
    os.system("find /usr -name '*.pyc' -delete")

# get Serial numbers from connected devices
proc = subprocess.Popen(["sispmctl", "-s"], stdout=subprocess.PIPE, shell=False)
(out, err) = proc.communicate()
lines      = out.decode("utf-8").split("\n")
devices    = []
for line in lines:
  if "serial" in line: devices.append(line.split(" ")[5])
if not devices:
  print(log + u": Found no devices!")
  exit(0)

weather = getData("weather")

if len(weather) > 0:
  city      = weather["name"]
  cloud_prc = weather["clouds"]["all"]
  pressure  = weather["main"]["pressure"]
  humidity  = weather["main"]["humidity"]
  temp_now  = weather["main"]["temp"]
  temp_min  = weather["main"]["temp_min"]
  temp_max  = weather["main"]["temp_max"]
  sunset    = weather["sys"]["sunset"]
  sunrise   = weather["sys"]["sunrise"]
  for stte in weather["weather"]:
    if   stte["main"] == "Rain":         rain    = True
    elif stte["main"] == "Thunderstorm": thunder = True
    elif stte["main"] == "Snow":         snow    = True

  sun   = datetime.datetime.fromtimestamp(sunrise)
  night = datetime.datetime.fromtimestamp(sunset) - datetime.timedelta(hours = 1)
else:
  sun       = None
  night     = None
  cloud_prc = None
  humidity  = None
  pressure  = None
  temp_now  = None
  city      = None

def checkOnline(hostname):
  response = os.system("ping -qc 3 " + hostname + " >/dev/null")
  if response == 0:                    return True
  else:                                return False

def checkDay():
  # sunset and sunrise can be outdated! Take values with care
  if checkRange(23,5):                 return False
  if sun and night:
    if   now <= sun:                   return False
    elif now >  sun and now < night:   return True
    elif now >= night:                 return False
  else:                                return False

def checkClouds(limit):
  if cloud_prc:
    if snow:                           return False
    elif cloud_prc >= limit:           return True
  return False

def checkNight():
  if checkRange(22, 4):
    if checkOnline(tv_dns):            return True
  return False

def workDay():
  if weekday in weekdays:              return True
  else:                                return False
  
def weekEnd():
  if weekday in weekends:              return True
  else:                                return False
  
def checkRange(min, max):
  if min < max:
    if hour >= min and hour < max:     return True
    else:                              return False
  else:
    if hour >= min or  hour < max:     return True
    else:                              return False

def setSwitch(serial, options, spoud = None):
  os.system("sispmctl -D" + serial + " " + options + " >/dev/null")
  if spoud:
    global finallog
    finallog += spoud + u", "

# -------------------------------------------------
# lightpower > 1: mainlight 2: worklight 3: charlielight 4: fishlight
# aquapower  > 1: powerpump 2: heater    3: extralight   4: mintlight
# aqua2power > 1: heater    2: aqualight 3: minilight    4: nightpump

if lightpower in devices:
  # Smalllight
  if   workDay() and checkRange( 5, 8):           setSwitch(lightpower, "-o2", "Morning light")
  elif               checkRange(21,23):           setSwitch(lightpower, "-o2", "Book light")
  elif checkNight():                              setSwitch(lightpower, "-o2", "TV is still on")
  else:                                           setSwitch(lightpower, "-f2")

  # Mainlight
  if   workDay() and checkRange( 7, 8):           setSwitch(lightpower, "-o1", "Gooood Morning")
  elif not checkDay() and checkRange(17, 22):     setSwitch(lightpower, "-o1", "It is getting dark now")
  elif light:                                     setSwitch(lightpower, "-o1", "Simon said: light on!")
  elif checkDay() and hour <= 9:                  setSwitch(lightpower, "-f1", "Too early for light")
  #elif weekEnd() and checkDay() and (checkClouds(72) or rain):
  #                                                setSwitch(lightpower, "-o1", "weekEnd and rainy")
  #elif workDay() and hour >= 15 and (checkClouds(72) or rain):
  #                                                setSwitch(lightpower, "-o1", "workDay and rainy")
  else:                                           setSwitch(lightpower, "-f1", "Darkness is there")
  
  # Aqualights
  if   checkRange( 8, 13) or checkRange(15, 20):  setSwitch(lightpower, "-o4", "Aqua light on")
  else:                                           setSwitch(lightpower, "-f4", "Aqua light off")
  if   checkRange(12, 16):                        setSwitch(lightpower, "-o3", "Heat light on")
  else:                                           setSwitch(lightpower, "-f3", "Heat light off")

if aquapower in devices:
  # Aqua1 stuff
  if checkRange( 8, 12) or checkRange(16, 20):    setSwitch(aquapower, "-o1", "Aqua light on")
  else:                                           setSwitch(aquapower, "-f1", "Aqua light off")
  if checkRange(23,  4):                          setSwitch(aquapower, "-f2", "Heater off")
  else:                                           setSwitch(aquapower, "-o2", "Heater on")
  if checkRange(12, 16):                          setSwitch(aquapower, "-o3", "Heat light on")
  else:                                           setSwitch(aquapower, "-f3", "Heat light off")
  if not checkDay() and hour > 5 and hour < 22:   setSwitch(aquapower, "-o4", "xMas on")
  else:                                           setSwitch(aquapower, "-f4", "xMas off")

if aqua2power in devices:
  # Aqua2 stuff
  if checkRange(23,  4):                          setSwitch(aqua2power, "-f1", "Heater2 off")
  else:                                           setSwitch(aqua2power, "-o1", "Heater2 on")
  if checkRange( 9, 12) or checkRange(17, 21):    setSwitch(aqua2power, "-o2", "Aqua2 lights on")
  else:                                           setSwitch(aqua2power, "-f2", "Aqua2 lights off")
  if checkRange( 9, 12) or checkRange(17, 21):    setSwitch(aqua2power, "-o3", "Mini light on")
  else:                                           setSwitch(aqua2power, "-f3", "Mini light off")
  if checkRange( 8, 19):                          setSwitch(aqua2power, "-o4", "CO2 on")
  else:                                           setSwitch(aqua2power, "-f4", "CO2 off")

if len(weather) > 0:
  print(log + u": " + city + u" => Clouds at: " + str(cloud_prc).zfill(2) + u"%. Temp is: " + str(temp_now) + u"*C. Sunrise: " + str(sun) + u", Sunset: " + str(night) + u". Pressure: " + str(pressure).zfill(4) + u". Humidity: " + str(humidity).zfill(2) + u"%. Rain is " + str(rain))

print(log + u": " + finallog + u"done!")
exit(0)
