from plistlib import InvalidFileException
import urllib
import json
import logging
import requests

logger = logging.getLogger()
device_IP = '10.68.0.60'
"""
modosGoogle ={
        'on':1, #mapea con on en el dispositivo
        'off':0,#mapea con off en el dispositivo
        'heat':2#mapea con auto en el dispositivo
}
"""
modosGoogle = ['off','on','heat']

def termostato_query(custom_data):    
    """
    Peticion:
    http://10.68.1.60/estado
    Ejemplo de respuesta:
    {"medidas":{"temperatura":22.1,"consigna":10,"humedad":51.5,"presion":936.3,"altitud":749.1},"salidas":{"caldera":0,"seguridad":1},"modo":[2,0]}
    """
    respuesta = {}
    medidas = {}
    url = 'http://' + device_IP + '/estado'
    logger.debug("Peticion de estado: accediendo al dispositivo en %s",url)

    r = requests.get(url)
    logger.debug("respuesta: %s",r)#json.dumps(r,indent=2))
    r.json()
    respuesta = r.json()
    medidas=respuesta['medidas']
    modo=modosGoogle[respuesta['modo'][0]]
    logger.debug("modo: %s",modo)
    
    return {"status": "SUCCESS","states": {"online": "true","thermostatMode": modo,"thermostatTemperatureSetpoint": medidas['consigna'],"thermostatTemperatureAmbient": medidas['temperatura'],"thermostatHumidityAmbient": medidas['humedad']}}

def termostato_action(custom_data, command, params):
    logger.debug("commands: %s\nparamas: %s",command,params)

    if command == "action.devices.commands.ThermostatTemperatureSetpoint":
        consigna=params["thermostatTemperatureSetpoint"]
        logger.debug("Nueva consigna: %s",consigna)
        url = 'http://' + device_IP + '/consignaTemperatura?consigna=' + str(consigna)
        logger.debug("Cambio consigna: accediendo al dispositivo en %s",url)

        r = requests.get(url)
        logger.debug("respuesta: %s",r)

    if command == "action.devices.commands.ThermostatSetMode":
        indice=0
        modoDisp=0
        modo = params["thermostatMode"]
        for m in modosGoogle:
            if m==modo: modoDisp=indice
            else: indice = indice+1

        logger.debug("Nuevo modo del termostato: %s-->%s (%s)", modo,modoDisp,indice)
        url = 'http://' + device_IP + '/modo?modo=' +  str(modoDisp)
        logger.debug("Cambio de modo: accediendo al dispositivo en %s",url)

        r = requests.get(url)
        logger.debug("respuesta: %s",r)
        
    return termostato_query(custom_data)
    #return {"status": "SUCCESS","online": "true","thermostatMode": "cool","thermostatTemperatureSetpoint": 23,"thermostatTemperatureAmbient": 25.1,"thermostatHumidityAmbient": 45.3}
