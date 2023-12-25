#!/bin/bash

cd /home/pi/desarrollo/python/flask/google_assistant/sync_manual

curl -X POST -H "Authorization: Bearer AIzaSyDCCArMoW_ern2vuFrGtm7j718Jj3SJOMs" \
  -H "Content-Type: application/json" \
  -d @request-body.json \
  "https://homegraph.googleapis.com/v1/devices:requestSync"
