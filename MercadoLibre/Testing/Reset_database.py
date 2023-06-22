import csv
import sys, os
import yaml
import mysql.connector; from mysql.connector import Error

def get_config(file_config) -> dict:
    #Verificar que el archivo no esté vacio #############
    if file_config and os.path.exists(file_config):
        with open (file=file_config, mode="r") as file_config:
            #reader = file_config.read
            config = yaml.safe_load(file_config)

    else:
         sys.exit("El archivo de configuracion mencionado no existe\n")

    return (config)

# obtener variables dentro del archivo de configuracion
def get_content (config, value: str):
    line_config = config[value]
    return (line_config)

def process_csv_and_insert_to_db():
    # Obtener el directorio actual de trabajo
    work_dir = os.getcwd()

    #Unir el directorio actual con la carpeta Testing y el nombre del archivo datos.csv
    csv_file = os.path.join(work_dir, "Testing", "database.csv")
    file_config = os.path.join(work_dir, "Testing", "config.yml")
    #csv_file = os.path.join(workdir, "database.csv")
    print(csv_file) 
    

    # llamo a la funcion get_config para procesar el archivo de configuración yml
    print(file_config)
    config = get_config(file_config)


    # Obtener la información para conectarse a la base de datos
    myql_host = get_content(config=config, value="myql_host")
    myql_database = get_content(config=config, value="myql_database")
    myql_user = get_content(config=config, value="myql_user")
    myql_password = get_content(config=config, value="myql_password")
    myql_port = get_content(config=config, value="myql_port")

    
    # Establecer la conexión a la base de datos
    connection = mysql.connector.connect(host=myql_host, database=myql_database, user=myql_user, password=myql_password, port=myql_port)

    # Crear un cursor para ejecutar las consultas
    cursor = connection.cursor()

    
    # Ejecutar la query para obtener el nombre de la base de datos actual
    cursor.execute("DELETE FROM Base_de_Datos_prov")
    #nombre_bd = cursor.fetchone()[0]
    connection.commit()
    # Ejecutar la query para borrar todas las tablas de la base de datos
    #sql = "DROP DATABASE Base_de_Datos_prov"
    #cursor.execute(sql)


    # Definir la consulta SQL para insertar los datos en la tabla Base_de_Datos_prov
    """"""
    sql = sql = "INSERT INTO Base_de_Datos_prov (id, Nombre_del_tercero, Servicio, Clasificacion,\
                Fecha_envio_mail, Fecha_respuesta_prov, Mail_Prov, Fecha_expiracion_AoC) \
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"

    # Abrir el archivo csv en modo lectura
    with open(csv_file, "r") as f:
        # Crear un objeto reader para leer los datos del csv
        reader = csv.reader(f, delimiter = ";")

        # Saltar la primera fila que contiene los nombres de las columnas
        print (reader)
        next(reader)
        for row in reader:
            # Extraer los valores de cada campo y guardarlos en variables
            print(row)
            id = row[0]
            print(id)
            nombre = row[1]
            print(nombre)

            servicio = row[2]
            print(servicio)

            clasificacion = row[3]
            print(clasificacion)

            fecha_envio_mail = row[4]
            print(fecha_envio_mail)

            fecha_respuesta_prov = row[5]
            # datetime.datetime.strptime(row[5], "%Y-%m-%d").strftime("%Y-%m-%d")
            print(fecha_respuesta_prov)
            # datetime.datetime.strptime(row[5],"%d/%m/%Y")
            Mail_Prov = row[6]
            print(Mail_Prov)

            fecha_expiracion_aoc = row[7]
            print(fecha_expiracion_aoc)

            
            # Crear una tupla con los valores de cada campo
            values = (id, nombre, servicio, clasificacion, fecha_envio_mail, fecha_respuesta_prov, Mail_Prov, fecha_expiracion_aoc)

            # Ejecutar la consulta SQL con los valores de la tupla
            #cursor.execute(sql, (id, nombre, servicio, clasificacion, fecha_envio_mail, fecha_respuesta_prov, Mail_Prov, fecha_expiracion_aoc))
            cursor.execute(sql,values)
    # Hacer un commit para guardar los cambios en la base de datos
    connection.commit()

    # Cerrar el cursor y la conexión
    cursor.close()
    connection.close()



process_csv_and_insert_to_db()