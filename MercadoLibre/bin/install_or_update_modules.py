import pip
import importlib

librerias = ["os", "datetime", "google_auth_oauthlib", "googleapiclient", "google.oauth2", "google-api-python-client",\
            "google.auth", "pandas", "mimetypes", "io", "base64", "typing", "time", "email", "mysql-connector-python", "oauth2client"]

for lib in librerias: 
    # Para cada librería, intentamos importarla con el módulo importlib 
    try: 
        importlib.import_module(lib) 
        # Si se puede importar, significa que la librería está instalada y mostramos un mensaje 
        print(f"La librería {lib} está instalada.") 
        # Si no se puede importar, significa que la librería no está instalada y capturamos el error 
    except ImportError: 
        # Entonces, instalamos la librería con el comando pip install y mostramos un mensaje 
        pip.main(["install", lib]) 
        print(f"La librería {lib} se ha instalado.") 
