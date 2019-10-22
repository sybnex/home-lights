#!/bin/bash

if [ ! -f ~/.installed ]; then
  # install files
  sudo apt update
  sudo apt install python3-pip git -y

  # python stuff
  sudo pip3 install --upgrade pip
  sudo pip3 install --upgrade -r requirements.txt

  touch ~/.installed
fi

# add crontabfile
crontab crontab.file

# ensure bot is running
test -n "$(pgrep -f bot.py)" || sudo python3 /home/pi/home-lights/bot.py

