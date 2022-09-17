#!/bin/bash

cd /home/pi/desarrollo/python/flask/google_assistant

export AUTHLIB_INSECURE_TRANSPORT=1

#export FLASK_APP=server:create_app
export FLASK_ENV=development
export FLASK_DEBUG=True

flask --app google_home run --host=10.68.0.101 --port=3100
#flask --app oauth2_server:create_flask_app run --host=10.68.0.101 --port=3100

