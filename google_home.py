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

#config de BBDD
try:
    db = MySQLdb.connect(config.DB_IP,config.DB_USUARIO,config.DB_PASSWORD,config.DB_NOMBRE)
    db.autocommit(True)
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    print('OK: Conectado a la base de datos ' + config.DB_NOMBRE)
except MySQLdb.Error as e:
    print("No puedo conectar a la base de datos:",e)
    sys.exit(1)

app = Flask(__name__)

logger.info("Started.")#, extra={'remote_addr': '-', 'user': '-'})


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

@app.route('/test', methods=['GET', 'POST'])
def test():
    return jsonify('{"mensaje":"Hola"}')
        
# Function to load user info
@app.route('/usuario/<username>')##Solo para depuracion
def get_user_db(username):
    logger.info("A por ello...")
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
                logger.warning("invalid auth request")#, extra={'remote_addr': request.remote_addr, 'user': request.form['username']})
                print('request.form: ')
                print(request.form)
                print('request.args: ')
                print(request.args)
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
    """
    if (1 or("client_secret" not in request.form
        or request.form["client_secret"] != config.CLIENT_SECRET
        or "client_id" not in request.form
        or request.form["client_id"] != config.CLIENT_ID
        or "code" not in request.form)):

            if ("client_secret" not in request.form):
                print("No hay secreto")
            else: 
                if (request.form["client_secret"] != config.CLIENT_SECRET):
                    print("Secreto incorrecto %s", request.form["client_secret"])
                else:
                    if ("client_id" not in request.form):
                        print("no hay id")
                    else: 
                        if (request.form["client_id"] != config.CLIENT_ID):                            
                            print("id incirrecto %s",request.form["client_id"])
                        else:
                            if ("code" not in request.form):
                                print("No hay code")

            logger.warning("invalid token request")#, extra={'remote_addr': request.remote_addr, 'user': last_code_user})
            #####return "Invalid request", 400
    """
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
                device_id=device['name']        
                device_type=device['type']
                device_json = get_device(device_type)
                device_json['id'] = device_id
                #logger.debug("Dispositivo: %s\r\n",device)
                result['payload']['devices'].append(device_json)

        # Query intent, need to response with current device status
        if intent == "action.devices.QUERY":
            ###Mi codigo para leer los dispositivos del usuario y compararlos con los que vienen en la peticion
            dev = {"devices":[]}
            user = get_user_db(user_id)
            # Loading each device available for this user
            for device_id in user['devices']:
                # Loading device info                
                #logger.debug("Dispositivo: %s\r\n",device_id)
                dev['devices'].append(device_id)

            """logger.debug("Dispositivos configurados para %s\r\n",user_id)
            for dd in dev['devices']:
                logger.debug("Dispositivo: %s\r\n",dd)
            """
            ###Fin de la lectura de dispositivos del usuario

            result['payload'] = {}
            result['payload']['devices'] = {}
            for device in i['payload']['devices']:
                ###compruebo si existe el id
                device_id = device['id']
                if device_id in dev['devices']:
                    #logger.debug("\n\nEsta el dispositivo %s\n\n", device_id)

                    custom_data = device.get("customData", None)
                    # Load module for this device
                    device_module = importlib.import_module(device_id)
                    # Call query method for this device
                    query_method = getattr(device_module, device_id + "_query")
                    result['payload']['devices'][device_id] = query_method(custom_data)
                ###Si no esta no lo incluyo en la respuesta
                else:
                    logger.debug("\n\nNo esta el dispositivo %s\n\n", device_id)


        # Execute intent, need to execute some action
        if intent == "action.devices.EXECUTE":
            result['payload'] = {}
            result['payload']['commands'] = []
            for command in i['payload']['commands']:
                for device in command['devices']:
                    device_id = device['id']
                    #Habria que comprobar que el dispositivo esta en la config del cleinte
                    custom_data = device.get("customData", None)
                    logger.debug("Accion sobre device_id: %s",device_id)
                    # Load module for this device
                    device_module = importlib.import_module(device_id)
                    # Call execute method for this device for every execute command                    
                    action_method = getattr(device_module, device_id + "_action")
                    logger.debug("action_method: %s",action_method)
                    for e in command['execution']:
                        command = e['command']
                        params = e.get("params", None)             
                        action_result = action_method(custom_data, command, params)
                        logger.debug("action_result_return: %s",json.dumps(action_result))
                        action_result['ids'] = [device_id]
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
