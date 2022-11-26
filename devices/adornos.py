
import subprocess
from plistlib import InvalidFileException
import urllib
import json
import logging
import requests

logger = logging.getLogger()
device_IP = '10.68.0.51'
"""
modosGoogle ={
        'on':1, #mapea con on en el dispositivo
        'off':0,#mapea con off en el dispositivo
}
"""
modosGoogle = [False,True]

def adornos_query(custom_data):
    """
    Peticion:
    http://10.68.1.60/estadoSalidas
    Ejemplo de respuesta:
    {"salidas":[
        {"id":0,"nombre":"Regleta","pin":32,"modo":"Manual","controlador":-1,"estado":0,"nombreE$
        {"id":1,"nombre":"Otros","pin":33,"modo":"Manual","controlador":-1,"estado":0,"nombreEst$
        ]
    }
    """
    logger.debug("Query en adornos:\n")

    respuesta = {}
    medidas = {}
    url = 'http://' + device_IP + '/estadoSalidas'
    logger.debug("Peticion de estado: accediendo al dispositivo en %s",url)

    r = requests.get(url)
    logger.debug("respuesta: %s",r)#json.dumps(r,indent=2))
    r.json()
    respuesta = r.json()

    salidas=respuesta['salidas']
    estado=modosGoogle[salidas[0]['estado']]
    """
    if salidas[0]['estado']==1: estado=true
    else: estado=false
    """
    logger.debug("modo: %s",estado)

    return {"status": "SUCCESS", "states": {"on": estado, "online": True}}

def adornos_action(custom_data, command, params):
    logger.debug("commands: %s\nparamas: %s",command,params)

    if command == "action.devices.commands.OnOff":
        if params['on']:
                url = 'http://' + device_IP + '/activaSalida?id=0'
                logger.debug("Cambio consigna: accediendo al dispositivo en %s",url)

                r = requests.get(url)
                logger.debug("respuesta: %s",r)
        else:
                url = 'http://' + device_IP + '/desactivaSalida?id=0'
                logger.debug("Cambio consigna: accediendo al dispositivo en %s",url)

                r = requests.get(url)
                logger.debug("respuesta: %s",r)

        return {"status": "SUCCESS", "states": {"on": params['on'], "online": True}}

    else:
        return {"status": "ERROR"}
