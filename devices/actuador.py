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

def leerEstadoSalida():
    """
    Peticion:
    http://10.68.1.60/estadoSalidas
    Ejemplo de respuesta:
    {"salidas":[
        {"id":0,"nombre":"Regleta","pin":32,"modo":"Manual","controlador":-1,"estado":0,"nombreEstado":"Apagado","anchoPulso":1000,"finPulso":0},
        {"id":1,"nombre":"Otros","pin":33,"modo":"Manual","controlador":-1,"estado":0,"nombreEstado":"Apagado","anchoPulso":1000,"finPulso":0}
        ]
    }
    {
    "datos": [{"id": 0,"nombre": "led","pin": 32,"modo": "Manual","controlador": -1,"estado": 0,"nombreEstado": "Apagado","anchoPulso": 1000,"finPulso": 0}]
    }    
    """
    url = 'http://' + device_IP + '/estadoSalidas'
    logger.debug("Peticion de estado salidas: accediendo al dispositivo en %s",url)

    r = requests.get(url)
    logger.debug("respuesta: %s",r)#json.dumps(r,indent=2))
    r.json()
    respuesta = r.json()

    datos=respuesta['datos'] 
    estado=modosGoogle[datos[0]['estado']]

    logger.debug("modo: %s",estado)
    
    return estado

def leerEstadoSecuenciador():
    """
    Peticion:
    http://10.68.1.60/estadoSecuenciador
    Ejemplo de respuesta:
    {"estado":1,
    "planes":[{"id":0,"nombre":"Luces","salida":0,"estado":0}]
    }

    """
    url = 'http://' + device_IP + '/estadoSecuenciador'
    logger.debug("Peticion de estado secuenciador: accediendo al dispositivo en %s",url)

    r = requests.get(url)
    logger.debug("respuesta: %s",r)#json.dumps(r,indent=2))
    r.json()
    respuesta = r.json()
    
    estadoSec=modosGoogle[respuesta['estado']]
    #if (respuesta['estado']): estadoSec=True
    #else: estadoSec=False
    
    return estadoSec

def generaRespuestaQuery():
    estadoSalida=leerEstadoSalida()
    #estadoSecuenciador=leerEstadoSecuenciador()
    if leerEstadoSecuenciador()==0 :
        ToggleSecuenciador=False
        ModoSecuenciador="Manual"
    else:
        ToggleSecuenciador=True
        ModoSecuenciador="Automatico"
    return {
#        "status": "SUCCESS", 
        "on": estadoSalida, 
        "online": True,
        "currentToggleSettings": {"secuenciador": ToggleSecuenciador },
        "currentModeSettings": {"modo": ModoSecuenciador}        
        }

def generaRespuestaExecute():
    estadoSalida=leerEstadoSalida()
    if leerEstadoSecuenciador()==0 :
        ToggleSecuenciador=False
        ModoSecuenciador="Manual"
    else:
        ToggleSecuenciador=True
        ModoSecuenciador="Automatico"

    return {
        "status": "SUCCESS", 
        "states":{
            "on": estadoSalida, 
            "online": True,
            "currentToggleSettings": {"secuenciador": ToggleSecuenciador },
            "currentModeSettings": {"modo": ModoSecuenciador}
            }
        }

def actuador_query(user_id,device_name,custom_data):
    logger.debug("Query en adornos:\n")

    #respuesta = {}
    respuesta= generaRespuestaQuery()

    return respuesta

def actuador_action(user_id,device_name,custom_data, command, params):
    logger.debug("commands: %s\nparamas: %s",command,params)
    
    if command == "action.devices.commands.OnOff":
        if params['on']:
                url = 'http://' + device_IP + '/activaRele?id=0'
                logger.debug("Cambio consigna: accediendo al dispositivo en %s",url)

                r = requests.get(url)
                logger.debug("respuesta: %s",r)
        else:
                url = 'http://' + device_IP + '/desactivaRele?id=0'
                logger.debug("Cambio consigna: accediendo al dispositivo en %s",url)

                r = requests.get(url)
                logger.debug("respuesta del dispositivo: %s",r)
        '''
        return {"status": "SUCCESS", 
                "states": {
#                    "online": True,
                    "on": params['on'] 
                    }
                }
        '''
        return generaRespuestaExecute()
        
    elif command == "action.devices.commands.SetToggles":                    
        if 'updateToggleSettings' in params:
            toggles=params.get('updateToggleSettings',None)
            if 'secuenciador' in toggles:
                toggle = toggles["secuenciador"]
                logger.debug("Valor de toggle: %s",toggle)                
                
                if(toggle):
                    url = 'http://' + device_IP + '/activaSecuenciador'
                else:
                    url = 'http://' + device_IP + '/desactivaSecuenciador'
                logger.debug("Cambio el modo del secuenciador: accediendo al dispositivo en %s",url)

                r = requests.get(url)
                logger.debug("respuesta del dispositivo: %s",r)
                

                return generaRespuestaExecute()
                    
            else:
                return {"status": "ERROR"}
        else:
            return {"status": "ERROR"}
            
    elif command == "action.devices.commands.SetModes":
        if 'updateModeSettings' in params:
            modos=params.get('updateModeSettings',None)
            if 'Modo' in modos:
                modo = modos["Modo"]
                logger.debug("Valor de Modo: %s",modo)         
               
                if modo=="Manual":
                    url = 'http://' + device_IP + '/desactivaSecuenciador'
                elif modo=="Automatico":
                    url = 'http://' + device_IP + '/activaSecuenciador'
                logger.debug("Cambio el modo del secuenciador: accediendo al dispositivo en %s",url)

                r = requests.get(url)
                logger.debug("respuesta del dispositivo: %s",r)
                
                #return {"status": "SUCCESS", "currentModeSettings": {"modo": modo}}                
                return generaRespuestaExecute()
            
            else:
                return {"status": "ERROR"}                
        else:
            return {"status": "ERROR"}

    else:
        return {"status": "ERROR"}

