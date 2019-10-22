#!/bin/bash

if [ ! -f /tmp/.installed ]; then
  # install files
  sudo apt update
  sudo apt install python3-cryptography python3-pip git -y

  # python stuff
  sudo pip3 install --upgrade pip
  sudo pip3 install --upgrade -r requirements.txt

  touch /tmp/.installed
fi

# add crontabfile
crontab crontab.file
