#!/bin/bash

DATE=$(date +"%Y-%m-%d_%H%M")
fswebcam -q -r 1280x720 --no-banner /opt/demo/images/webcam$DATE.jpg
python3 -W ignore /opt/demo/image.py -i /opt/demo/images/webcam$DATE.jpg 2>/dev/null
