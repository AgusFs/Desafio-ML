import sys, os, time
import argparse
import yaml
import mysql.connector; from mysql.connector import Error

from bin import api_validator
from bin import ConnectDrive
from bin import Gmail

from dateutil.relativedelta import relativedelta
from email.utils import parsedate_tz, mktime_tz
import datetime, re


# almacenar el archivo de configuracion
def get_config(file_config) -> dict:
    #Verificar que el archivo no esté vacio #############
    if file_config and os.path.exists(file_config):
        with open (file=file_config, mode="r") as file_config:
            #reader = file_config.read
            config = yaml.safe_load(file_config)
            return (config)

    else:
         sys.exit("El archivo de configuracion mencionado no existe. el path es: ", file_config,"\n")

    

# obtener variables dentro del archivo de configuracion
def get_content (config, value: str):
    line_config = config[value]
    return (line_config)


def database_connect (myql_host, myql_database, myql_user, myql_password, myql_port):
    try:
        connection = mysql.connector.connect(host=myql_host, database=myql_database, user=myql_user, password=myql_password, port=myql_port)
        #print("Test:",connection)
        return(connection)
    # Si falla la conexión indico error.
    except mysql.connector.errors.InterfaceError as e:
        # Imprimir el mensaje de error
        print("Error while connecting to MySQL", e)
        return None

    

def database_extract (database) -> list:
    cursor = database.cursor()
    
    
    """
    Esta query traerá la información si se cumplen las siguientes condiciones:
        La Fecha_expiracion_AoC está vacía o es menor o igual que la fecha actual más 60 días. (Nunca me enviaron un AOC o está proximo a vencer)
        La Fecha_envio_mail está vacía o la diferencia entre la fecha actual y la Fecha_envio_mail es mayor que 30 días. (en caso de haya enviado el mail de aviso)
    """
    
    query = "\
            SELECT id, Nombre_del_tercero, Mail_Prov, DATE_FORMAT(Fecha_expiracion_AoC, '%d/%m/%Y') AS Fecha_expiracion_AoC,\
            DATE_FORMAT(Fecha_envio_mail, '%d/%m/%Y') AS Fecha_envio_mail\
            FROM Base_de_Datos_prov\
            WHERE Fecha_expiracion_AoC IS NULL OR Fecha_expiracion_AoC <= DATE_ADD(CURDATE(), INTERVAL 30 DAY)\
            AND (Fecha_envio_mail IS NULL OR DATEDIFF(CURDATE(), Fecha_envio_mail) > 30)\
            ORDER BY Fecha_expiracion_AoC\
            "
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Cerrar conexión
        database.commit()      
        # Cerrar el cursor
        cursor.close()
        return(rows)  
    
    
    except mysql.connector.errors.ProgrammingError as e:
        # Imprimir el mensaje de error
        print(f"Error al ejecutar la consulta SQL: {e}") 
        # Cerrar conexión
        database.commit()      
        # Cerrar el cursor
        cursor.close() 
        return None
    
def update_database(database, id_proveedor, fecha_envio_mail, toRemitente, fecha_vencimiento):
    # Crear un cursor para ejecutar consultas SQL
    cursor = database.cursor()
    # Crear una consulta SQL para obtener la fecha de envio del mail almacenada en la base de datos
    sql = "SELECT id, Fecha_envio_mail FROM Base_de_Datos_prov WHERE id = %s"
    # Ejecutar la consulta con el valor del id_proveedor
    try:
        cursor.execute(sql, (id_proveedor,))
        # Obtener el resultado de la consulta
        result = cursor.fetchone()
    except mysql.connector.errors.ProgrammingError as e:
        # Imprimir el mensaje de error
        print(f"Error al ejecutar la consulta SQL: {e}")  
        result = None

    # Si el resultado no es None, significa que hay un registro con ese id
    if result is not None:
        # Crear una consulta SQL para actualizar los campos Fecha_envio_mail, toRemitente y Fecha_expiracion_AoC en la tabla proveedores
        sql = "UPDATE Base_de_Datos_prov SET Fecha_respuesta_prov = %s, To_Remitente = %s, Fecha_expiracion_AoC = %s WHERE id = %s"
        # Ejecutar la consulta con los valores recibidos por parámetro
        cursor.execute(sql, (fecha_envio_mail, toRemitente, fecha_vencimiento, id_proveedor))
        # Guardar los cambios en la base de datos
        database.commit()
    else:
        print("No existen proveedores que tengan el id: ",id_proveedor,"\nNo se va a actualizar la base de datos")
        # Este mensaje no debería imprimirse nunca, ya que el id_proveedor se extrae en algún momento desde la propia base de datos.

    # Guardar los cambios en la base de datos
    database.commit()      
    # Cerrar el cursor
    cursor.close()

def update_Fecha_envio_mail(database, id, fecha):
    # Declaro el cursor
    cursor = database.cursor()
    # Armo la query 
    sql = "UPDATE Base_de_Datos_prov SET Fecha_envio_mail = %s WHERE id = %s"
    try:
        # Ejecuto la query y le paso los parámetros
        cursor.execute(sql, (fecha, id))
    except mysql.connector.errors.ProgrammingError as e:
        # Imprimir el mensaje de error
        print(f"Error al ejecutar la consulta SQL, no se actualizó la fecha de envío: {e}")

    # Guardar los cambios en la base de datos
    database.commit()
    # Cerrar el cursor
    cursor.close()

def main (workdir, isdebug):
    # Busco dentro de la carpera de ejecución el archivo de configuración
    file_config = os.path.join(workdir, "config.yml")
    # llamo a la funcion get_config para procesar el archivo de configuración yml
    # La función get_config realiza la verificacion de la existencia del archivo
    # Se podría incorporar el caso en el que el archivo de configuración estuviera vacío
    config = get_config(file_config)


    # Obtengo las variables para conectarme a la base de datos por medio de la función get_content
    google_api_key      = get_content(config=config, value="google_api_key")
    CLIENT_SECRET_FILE  = get_content(config=config, value="CLIENT_SECRET_FILE")

    myql_host           = get_content(config=config, value="myql_host")
    myql_database       = get_content(config=config, value="myql_database")
    myql_user           = get_content(config=config, value="myql_user")
    myql_password       = get_content(config=config, value="myql_password")
    myql_port           = get_content(config=config, value="myql_port")

    GD_API_NAME         = get_content(config=config, value="GD_API_NAME")
    GD_API_VERSION      = get_content(config=config, value="GD_API_VERSION")
    GD_SCOPES           = get_content(config=config, value="GD_SCOPES")

    GM_API_NAME         = get_content(config=config, value="GM_API_NAME")
    GM_API_VERSION      = get_content(config=config, value="GM_API_VERSION")
    GM_SCOPES           = get_content(config=config, value="GM_SCOPES")
    
    # Conexión a la base de datos
    database = database_connect(myql_host=myql_host, myql_database=myql_database, myql_user=myql_user, myql_password=myql_password, myql_port=myql_port)
    # Obtengo listado de proveedores cuya AOC esta próxima a vencer
    
    prov = database_extract(database)   
    #print("El resultado de la query a la db es: ", prov)
    
    
    #if (len(prov) > 0):

    # Valido el servicio de gmail
    validate_object = api_validator.create_service(CLIENT_SECRET_FILE, GM_API_NAME, GM_API_VERSION, GM_SCOPES)
    validate_object_drive = api_validator.create_service(CLIENT_SECRET_FILE, GD_API_NAME, GD_API_VERSION, GD_SCOPES)
    # Obtengo la fecha actual
    fecha_actual = datetime.datetime.now()
    # Resto 6 meses a la fecha actual
    fecha_filtro = fecha_actual + relativedelta(months=-6)
    # Armo mi query de busqueda para obtener los mails no leidos de los últimos 6 meses, que contengan el asunto Renovación de AoC
    # Gmail no admite regex, por lo que se obtiene un listado de mails lo mas a cotado posible
    # Bloque para buscar los mails de renovación
    query_string = "is:unread in:inbox subject: (id- AROUND 10 Renovación de AoC) after:" + fecha_filtro.strftime("%d/%m/%Y")  
    
    # Extraigo los valores de forma recursiva de cada elemento de mi lista (Si no está vacía)
    email_messages = Gmail.search_emails(validate_object, query_string)
    
    if email_messages is not None:
        print("Buscando mails..") 
        # Recorrer la lista de correos recibido
        for email_message in email_messages:
            # Obtengo el detalle del mensaje
            messageDetail = Gmail.get_message_detail(validate_object, email_message['id'], msg_format='full', metadata_headers=['parts'])
            messageDetailPayload = messageDetail.get('payload')        
        
        if 'parts' in messageDetailPayload:
            # Obtengo los headers
            headers = messageDetailPayload.get('headers')
            # Buscar el encabezado que tenga el nombre "Subject" y obtener su valor
            subject = next(header['value'] for header in headers if header['name'] == 'Subject')
            # obtengo el mail del remitente en bruto  "nombre apellido" <example@example.com>
            remitente = next(header['value'] for header in headers if header['name'] == 'From')
            # Extraigo solamente el valor que se encuentra dentro de las llaves <>
            remitente = re.search(r"<(.*?)>", remitente).group(1)

            # Extraigo la fecha de envio del correo
            f_envio = next(header['value'] for header in headers if header['name'] == 'Date')
            # Es necesario parsear la fecha
            timestamp = mktime_tz(parsedate_tz(f_envio))
            # Cambio el formato de la fecha parseada
            f_envio = datetime.datetime.fromtimestamp(timestamp).strftime("%Y/%m/%d") 

            
            # Si el campo “payload” tiene una clave “parts”, significa que el mensaje tiene uno o más adjuntos.
            for msgPayload in messageDetailPayload['parts']:
                # extraigo los valores
                file_name = msgPayload['filename']
                body = msgPayload['body']

                # recorro el body en busqueda de los IDs, puede haber varios archivos
                if 'attachmentId' in body:
                    attachment_id = body['attachmentId']
                    print("Mail encontrado - Subject ", subject, "Att: ", file_name)
                    # Obtengo el binario del archivo
                    attachment_content = Gmail.get_file_data(validate_object, email_message['id'], attachment_id, file_name, workdir)
                    
                    # Expresión regular para buscar el ID dentro del asunto
                    id_from_subject = re.search(r"^(id|ID|Id)\s?-\s?(\d+)\s?-\s?Renovaci.n.de.(aoc|AOC|AoC)\s?-\s?\w+", subject).group(2)
                    # Expresión regular para buscar la fecha de vencimiento dentro del nombre de archivo
                    f_vencimiento = str(re.search(r"\d\d_\d\d_\d+",file_name).group(0))
                    # Cambio el formato de la fecha
                    f_vencimiento = datetime.datetime.strptime(f_vencimiento, "%d_%m_%Y").strftime("%Y/%m/%d")

                    ConnectDrive.upload_data(validate_object_drive, file_name, file=attachment_content)
                    #print("Remitente:",remitente,id_from_subject, "fecha envio: ", f_envio, "fecha vencimiento", f_vencimiento)
                    update_database(database, id_proveedor=id_from_subject, fecha_envio_mail=f_envio, toRemitente=remitente, fecha_vencimiento=f_vencimiento)
            time.sleep(0.5)
    else:
        pass
    
    print (prov)
    if prov is not None:
        ## Bloque para el envio de mails
        for i, values in enumerate(prov):
            id = values[0]
            nombre = values[1]
            Mail = values[2]
            fecha_vencimiento = values[3]

            # No se utiliza este valor ya que la query de sql ya está haciendo un filtrado.
            # ultimo_envio_mail = values[3]
            # print(id,nombre,fecha_vencimiento,Mail)
            # llamo a la función para disparar los mails y me retorna la fecha de envio del mail
            fecha_envio = Gmail.send_mail (id, nombre, Mail, fecha_vencimiento, fecha_actual, validate_object)
            # Actualizo la base de datos
            update_Fecha_envio_mail(database,id, fecha_envio)
      
    else:
        sys.exit("No hay ningún proveedor al que enviar un aviso de vencimiento")

    
              
        


if __name__=="__main__":
    """Definir objeto parser"""
    parseador = argparse.ArgumentParser("config", description="Archivo de configuracion .yml")

    # parseador.add_argument("-c", "--config", required=False, default="config.yml")
    parseador.add_argument("-d", "--debug", required=False, default=False, action='store_true')

    args = parseador.parse_args()
    # Obtengo carpeta de ejecución
    workdir = os.getcwd()
    
    #print("La carpeta de ejecución es: ", workdir)
    # Llamo a main y le paso los parámetros necesarios.
    main(workdir, isdebug=args.debug) 


