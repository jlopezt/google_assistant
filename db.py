import config
import sys
import MySQLdb
import logging

#config de BBDD
def connectDB():
    try:
        mydb = MySQLdb.connect(config.DB_IP,config.DB_USUARIO,config.DB_PASSWORD,config.DB_NOMBRE)
        mydb.autocommit(True)
        cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
        logger.info('OK: Conectado a la base de datos ' + config.DB_NOMBRE)
        return (cursor)
    except MySQLdb.Error as e:
        logger.error("No puedo conectar a la base de datos:",e)
        return (None)

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
            
            respuesta["devices"].append({"name": registro["SID"], "type": registro["DeviceType"]})

        return respuesta
    else:
        logger.warning("user not found")#, extra={'remote_addr': request.remote_addr, 'user': username})
        return None


#--------------------------------------------------------------------------------------------------------
logger = logging.getLogger()

cursor=connectDB()

if cursor== None:
    sys.exit(1)
    
