import logging

CLIENT_ID = "DomoticaePre"
CLIENT_SECRET = "JorsadiPre"
API_KEY_PRE = "AIzaSyAyRHyVTo-1fCYnfNcoYkht0HP02p-6WUw"
#API_KEY = "AIzaSyDCCArMoW_ern2vuFrGtm7j718Jj3SJOMs"
USERS_DIRECTORY = "/home/pi/desarrollo/python/flask/google_assistant/users"
TOKENS_DIRECTORY = "/home/pi/desarrollo/python/flask/google_assistant/tokens"
DEVICES_DIRECTORY = "/home/pi/desarrollo/python/flask/google_assistant/devices"

# Uncomment to enable logging
#LOG_FILE = "/var/log/google-home.log"
LOG_FILE = "/home/pi/desarrollo/python/flask/google_assistant/log/google-home.log"
LOG_LEVEL = logging.DEBUG
#LOG_FORMAT = "%(asctime)s %(remote_addr)s %(user)s %(message)s"
LOG_FORMAT = "%(asctime)s %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

#Configuracion de la BBDD
DB_IP = "10.68.0.100"
DB_PUERTO = 3306
DB_USUARIO = "domoticae"
DB_PASSWORD = "88716"
DB_NOMBRE = "domoticae"
