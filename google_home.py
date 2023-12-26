# coding: utf8

import config
from flask import Flask
from flask import request
from flask import render_template
from flask import send_from_directory
from flask import redirect
from flask import jsonify
import sys
import os
import requests
import urllib
import json
import random
import string
from time import time
import importlib
import logging

import MySQLdb
from hashlib import md5

# Enable log if need

if hasattr(config, 'LOG_FILE'):
    logging.basicConfig(level=config.LOG_LEVEL,
                    format=config.LOG_FORMAT,
                    datefmt=config.LOG_DATE_FORMAT,
                    filename=config.LOG_FILE,
                    filemode='a')
logger = logging.getLogger()

# Path to device plugins
sys.path.insert(0, config.DEVICES_DIRECTORY)

last_code = None
last_code_user = None
last_code_time = None

app = Flask(__name__)

logger.info("Started.")#, extra={'remote_addr': '-', 'user': '-'})

#config de BBDD
try:
    db = MySQLdb.connect(config.DB_IP,config.DB_USUARIO,config.DB_PASSWORD,config.DB_NOMBRE)
    db.autocommit(True)
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    logger.info('OK: Conectado a la base de datos ' + config.DB_NOMBRE)
except MySQLdb.Error as e:
    #logger.warning("No puedo conectar a la base de datos:",e)
    logger.error("No puedo conectar a la base de datos:",e)
    sys.exit(1)


#---------------------------------------- Funciones -------------------------------
# Function to load user info
"""
def get_user(username):
    filename = os.path.join(config.USERS_DIRECTORY, username + ".json")
    logger.info("busco fichero %s", filename)#, extra={'remote_addr': '-', 'user': '-'})
    if os.path.isfile(filename) and os.access(filename, os.R_OK):
        logger.info("abriendo fichero %s", filename)#, extra={'remote_addr': '-', 'user': '-'})
        with open(filename, mode='r') as f:
            text = f.read()
            data = json.loads(text)
            return data
    else:
        logger.warning("user not found")#, extra={'remote_addr': request.remote_addr, 'user': username})
        return None
"""

def get_device_type(username, device_name):
    sql="select * from Dispositivos where CID='" + username + "' and SID='" + device_name +"'"
    try:
        cursor.execute(sql)
    except Exception as e: 
        print(e)  
        print("Error en la consulta")       

    #Si he encontrado el usaurio
    if (cursor.rowcount>0): 
        registro = cursor.fetchone()
        return registro["DeviceType"]
    else:
        return None

# Function to load device info
def get_device(device_type):
    filename = os.path.join(config.DEVICES_DIRECTORY, device_type + ".json")
    if os.path.isfile(filename) and os.access(filename, os.R_OK):
        with open(filename, mode='r') as f:
            text = f.read()
            data = json.loads(text)
            #data['id'] = device_id
            return data
    else:
        return None

# Random string generator
def random_string(stringLength=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for i in range(stringLength))

# Function to retrieve token from header
def get_token():
    auth = request.headers.get('Authorization')
    parts = auth.split(' ', 2)
    if len(parts) == 2 and parts[0].lower() == 'bearer':
        return parts[1]
    else:
        logger.warning("invalid token: %s", auth)#, extra={'remote_addr': request.remote_addr, 'user': '-'})
        return None

# Function to check current token, returns username
def check_token():
    access_token = get_token()
    access_token_file = os.path.join(config.TOKENS_DIRECTORY, access_token)
    if os.path.isfile(access_token_file) and os.access(access_token_file, os.R_OK):
        with open(access_token_file, mode='r') as f:
            return f.read()
    else:
        return None
#---------------------------------------- Fin funciones -------------------------------

#---------------------------------------- Routers -------------------------------
@app.route('/test', methods=['GET', 'POST'])
def test():
    return jsonify('{"mensaje":"Hola"}')
        
# Function to load user info
@app.route('/usuario/<username>')##Solo para depuracion
def get_user_db(username):
    #logger.info("A por ello...")
    respuesta={"password":"","devices": []}
    
    sql="select * from Usuarios where Usuario='" + username + "'"
    try:
        cursor.execute(sql)
    except Exception as e: 
        print(e)  
        print("Error en la consulta")       

    #Si he encontrado el usaurio
    if (cursor.rowcount>0): 
        registro = cursor.fetchone()
        #print(registro["Nombre"],registro["Apellidos"],registro["Correo"],registro["Telefono"],registro["Direccion_ppal"],username)

        respuesta["password"]=registro["Password"]

        sql="select * from Dispositivos where CID='" + username + "'"
        try:
            cursor.execute(sql)
        except Exception as e: 
            print(e)  
            print("Error en la consulta")       

        #Si he encontrado dispositivos
        for i in range(cursor.rowcount): 
            registro = cursor.fetchone()
            #respuesta["devices"].append(registro["SID"])
            respuesta["devices"].append({"name": registro["SID"], "type": registro["DeviceType"]})

        #return jsonify(respuesta)
        return respuesta
    else:
        logger.warning("user not found")#, extra={'remote_addr': request.remote_addr, 'user': username})
        return None

@app.route('/login.html')
def send_login():
    return render_template('login.html')
        
@app.route('/statics/<path:path>')
def send_statics(path):
    return send_from_directory('statics', path)

# OAuth entry point
@app.route('/auth', methods=['GET', 'POST'])
def auth():
    global last_code, last_code_user, last_code_time
    if request.method == 'GET':
        # Ask user for login and password
        return render_template('login.html')#('main.html')
    elif request.method == 'POST':
        if ("username" not in request.form
            or "password" not in request.form
            or "state" not in request.args
            or "response_type" not in request.args
            or request.args["response_type"] != "code"
            or "client_id" not in request.args
            or request.args["client_id"] != config.CLIENT_ID):               
                logger.warning("invalid auth request", extra={'remote_addr': request.remote_addr, 'user': request.form['username']})
                return "Invalid request", 400
            
        # Check login and password
        user = get_user_db(request.form["username"])
        password_txt = str(request.form["password"])
        password = md5(password_txt.encode("utf-8")).hexdigest()
        """
        print("----------------->usuario: %s",user)
        print("----------------->pass_db: %s",password)
        print("----------------->pass_form: %s",user["password"])
        """
        
        if (user == None or user["password"] != password):
            logger.warning("invalid password")#, extra={'remote_addr': request.remote_addr, 'user': request.form['username']})
            return render_template('login.html', login_failed=True)

        # Generate random code and remember this user and time
        last_code = random_string(8)
        last_code_user = request.form["username"]
        last_code_time = time()

        params = {'state': request.args['state'], 
                  'code': last_code,
                  'client_id': config.CLIENT_ID}
        logger.info("generated code")#, extra={'remote_addr': request.remote_addr, 'user': request.form['username']})
        return redirect(request.args["redirect_uri"] + '?' + urllib.parse.urlencode(params))

# OAuth, token request
@app.route('/token', methods=['GET', 'POST'])
def token():    
    global last_code, last_code_user, last_code_time

    print("-------------------->Me piden un token por POST. cliente ID: ", config.CLIENT_ID," cliente secret: ", config.CLIENT_SECRET)
    print("-------------------->con datos: ", request.form)

    # Check code
    if request.form["code"] != last_code:
        logger.warning("invalid code")#, extra={'remote_addr': request.remote_addr, 'user': last_code_user})
        return "Invalid code", 403
    # Check time
    if  time() - last_code_time > 10:
        logger.warning("code is too old")#, extra={'remote_addr': request.remote_addr, 'user': last_code_user})
        return "Code is too old", 403
    
    # Generate and save random token with username
    access_token = random_string(32)
    access_token_file = os.path.join(config.TOKENS_DIRECTORY, access_token)
    with open(access_token_file, mode='wb') as f:
        f.write(last_code_user.encode('utf-8'))
    logger.info("access granted")#, extra={'remote_addr': request.remote_addr, 'user': last_code_user})
    # Return just token without any expiration time
    print("-------------------->Le doy el token %s", access_token)
    return jsonify({'access_token': access_token})

# Main URL to interact with Google requests
@app.route('/fulfillment', methods=['GET', 'POST'])
def fulfillment():
    logger.debug("Entramos en fulfillment")
    # Google will send POST requests only, some it's just placeholder for GET
    if request.method == 'GET': return "Quizas deberias utilizar POST para esta peticion...."

    # Check token and get username
    user_id = check_token()
    if user_id == None:
        return "Access denied", 403
    r = request.get_json()
    logger.debug("request: \r\n%s", json.dumps(r, indent=4))#, extra={'remote_addr': request.remote_addr, 'user': user_id})

    result = {}
    result['requestId'] = r['requestId']

    # Let's check inputs array. Why it's array? Is it possible that it will contain multiple objects? I don't know.
    inputs = r['inputs']
    for i in inputs:
        intent = i['intent']
        # Sync intent, need to response with devices list
        if intent == "action.devices.SYNC":
            result['payload'] = {"agentUserId": user_id, "devices": []}
            # Loading user info
            user = get_user_db(user_id)
            # Loading each device available for this user
            for device in user['devices']:
                # Loading device info        
                device_name=device['name']
                device_type=device['type']
                device_json = get_device(device_type)
                device_json['id'] = device_name
                device_json['name']['name']=device_name
                device_json['name']['nicknames'].append(device_name)
                
                #logger.debug("Dispositivo: %s\r\n",device)
                result['payload']['devices'].append(device_json)

        # Query intent, need to response with current device status
        if intent == "action.devices.QUERY":
            logger.debug("Intent Query")
            
            ###Mi codigo para leer los dispositivos del usuario y compararlos con los que vienen en la peticion                        
            user = get_user_db(user_id)
            dev = dict()
            # Loading each device available for this user            
            for user_device in user['devices']:
                dev.update({user_device['name']:{"type": user_device['type']}}) 
            logger.debug("Dispositivos de %s %s\r\n", user_id, json.dumps(dev))#, extra={'remote_addr': request.remote_addr, 'user': user_id})                
            ###Fin de la lectura de dispositivos del usuario

            result['payload'] = {}
            result['payload']['devices'] = {}
            for device in i['payload']['devices']:
                ###compruebo si existe el id
                device_name = device['id']
                if device_name in dev:
                    logger.debug("\n\nEsta el dispositivo %s\n\n", device_name)
                    device_type=dev[device_name]['type']
                    custom_data = device.get("customData", None)
                    # Load module for this device
                    device_module = importlib.import_module(device_type)
                    # Call query method for this device
                    query_method = getattr(device_module, device_type + "_query")
                    result['payload']['devices'][device_name] = query_method(user_id,device_name,custom_data)
                ###Si no esta no lo incluyo en la respuesta
                else:
                    logger.debug("\n\nNo esta el dispositivo %s\n\n", device_name)

        # Execute intent, need to execute some action
        if intent == "action.devices.EXECUTE":
            result['payload'] = {}
            result['payload']['commands'] = []
            for command in i['payload']['commands']:
                for device in command['devices']:
                    device_name = device['id']
                    #Habria que comprobar que el dispositivo esta en la config del cleinte
                    custom_data = device.get("customData", None)
                    logger.debug("Accion sobre device_id: %s",device_name)
                    
                    device_type=get_device_type(user_id,device_name)
                    
                    # Load module for this device
                    device_module = importlib.import_module(device_type)
                    # Call execute method for this device for every execute command                    
                    action_method = getattr(device_module, device_type + "_action")
                    logger.debug("action_method: %s",action_method)
                    for e in command['execution']:
                        command = e['command']
                        params = e.get("params", None)             
                        action_result = action_method(user_id,device_name,custom_data, command, params)
                        logger.debug("action_result_return: %s",json.dumps(action_result))
                        action_result['ids'] = [device_name]
                        #action_result['status']=action_result_return['status']
                        #action_result['states']=action_result_return['states']
                        result['payload']['commands'].append(action_result)
        
        # Disconnect intent, need to revoke token
        if intent == "action.devices.DISCONNECT":
            access_token = get_token()
            access_token_file = os.path.join(config.TOKENS_DIRECTORY, access_token)
            if os.path.isfile(access_token_file) and os.access(access_token_file, os.R_OK):
                os.remove(access_token_file)
                logger.debug("token %s revoked", access_token)#, extra={'remote_addr': request.remote_addr, 'user': user_id})
            return {}    

    logger.debug("response: \r\n%s", json.dumps(result, indent=4))#, extra={'remote_addr': request.remote_addr, 'user': user_id})
    return jsonify(result)
#---------------------------------------- Fin routers -------------------------------