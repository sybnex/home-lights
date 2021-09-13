#!/bin/bash

set -e

python3 -m compileall *.py
rm -rf __pycache__/

read -p "Commit Message: " MSG
git commit -am "$MSG"
git push
