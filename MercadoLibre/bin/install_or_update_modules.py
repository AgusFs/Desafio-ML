import pip
import importlib

librerias = ["os", "datetime", "google_auth_oauthlib", "googleapiclient", "google.oauth2",\
            "google.auth", "pandas", "mimetypes", "io", "base64", "typing", "time", "email"]

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
        # Luego, verificamos si hay actualizaciones disponibles para la librería con el comando pip list 
        pip.main(["list", "–outdated", "–format=freeze"]) 
        # Si la librería aparece en la lista de actualizaciones, mostramos un mensaje 
        if lib in pip.main(["list", "–outdated", "–format=freeze"]):
            print(f"La librería {lib} tiene una actualización disponible.") 
            # Entonces, actualizamos la librería con el comando pip install --upgrade y mostramos un mensaje 
            pip.main(["install", "–upgrade", lib]) 
            print(f"La librería {lib} se ha actualizado.")