import os
import datetime
#from collections import namedtuple
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

import google.auth.exceptions

def create_service(client_secret_file, api_name, api_version, scopes, prefix=''):
    
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    #SCOPES = [scope for scope in scopes[0]]
    SCOPES = scopes
    
    creds = None
    #Obtengo la carpeta de ejecución
    working_dir = os.getcwd()
    # token_dir es igual a la direccion de la 
    token_dir = 'token files'
    #print (token_dir)
    #Construcción del nombre del token para poder trabajar.
    token_file = f'token_{API_SERVICE_NAME}_{API_VERSION}{prefix}.json'
    #print (token_file)
    # Verifico si el directorio token_dir dentro del directorio "working_dir"
    if not os.path.exists(os.path.join(working_dir, token_dir)):
        #Si no existe creo existe creo las carpetas
        os.mkdir(os.path.join(working_dir, token_dir))
    
    # Verifico si existe el token_file dentro de los directorios
    if os.path.exists(os.path.join(working_dir, token_dir, token_file)):
        # Crear credenciales a partir del archivo JSON 
        creds = Credentials.from_authorized_user_file(os.path.join(working_dir, token_dir, token_file))#, SCOPES)
    
    # Verifico si las credenciales no existen o no son validas
    try:
        if not creds or not creds.valid:
            # Verifico si mi token expiró y si tengo un token de actualización
            if creds and creds.expired and creds.refresh_token:
                print ("Actualizando token de seguridad")
                request = Request()
                creds.refresh(request)
               

            # Si no existen o no tienen el token, proceso a solicitar una autorización manual    
            else:
                print("No existen los tokens de seguridad, favor de validar ventana")
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_local_server()
            
            # Abrir el archivo de token en modo escritura
            with open(os.path.join(working_dir, token_dir, token_file), 'w') as token:
                # Escribir las credenciales en formato JSON en el archivo
                token.write(creds.to_json())

    
    except google.auth.exceptions.TransportError as e:
        # Imprimir el mensaje de error
        print(f"Error de transporte: {e}")
        # Hacer algo más para manejar el error
        # ...
    # Si ocurre un error de actualización
    except google.auth.exceptions.RefreshError as e:
        # Imprimir el mensaje de error
        print(f"Error de actualización: {e}")
        # Hacer algo más para manejar el error

    print("Token: ", creds)

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=creds, static_discovery=False)
        print(API_SERVICE_NAME, API_VERSION, 'service created successfully')
        
        return service
    
    except Exception as e:
        print(e)
        print(f'Failed to create service instance for {API_SERVICE_NAME}')
        os.remove(os.path.join(working_dir, token_dir, token_file))
        return None

def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
    return dt


