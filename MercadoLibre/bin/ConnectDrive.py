import pandas as pd
from googleapiclient.http import MediaFileUpload
import mimetypes
import io
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload

def upload_file (validate_service, filename, file):
	service = validate_service

	folder_id = '1nCwLMoU6atrV-5YN4DUoi51mrEZn6etc' # PULIR ESTO, DEBERIA SER UN PARAMETRO EL FOLDER
	query = f"parents = '{folder_id}'"

	response = service.files().list(q=query).execute()
	files = response.get('files')
	nextPageToken = response.get('nextPageToken')
		
	while nextPageToken:
		response = service.files().list(q=query).execute()
		files.extend(response.get('files'))
		nextPageToken = response.get('nextPageToken')

	pd.set_option('display.max_columns',100)
	pd.set_option('display.max_rows',500)
	pd.set_option('display.min_rows',500)
	pd.set_option('display.max_colwidth',150)
	pd.set_option('display.width',200)
	pd.set_option('expand_frame_repr',True)
	df= pd.DataFrame(files)

	return(df)

# Definir la función upload_data
def upload_data (validate_object, file_name, file):
    # Asignar el valor de validate_object a una variable local
    service = validate_object
    # Definir el id de la carpeta donde se quieren subir los archivos
    folder_id = '1nCwLMoU6atrV-5YN4DUoi51mrEZn6etc'
    # Definir la lista de nombres de archivos
    file_names = file_name
    # Recorrer la lista de nombres de archivos con un bucle for

    # Crear un diccionario con los metadatos del archivo
    file_metadata = {'name':file_name,'parents': [folder_id]}
    # Obtener el tipo MIME del archivo según su nombre o extensión
    mime_type = mimetypes.guess_type(file_name)[0]
    # Crear un objeto de tipo archivo a partir de los bytes del parámetro file
    file_object = io.BytesIO(file)
    if mime_type is None:
        # Asignar un valor por defecto como "application/octet-stream"
        mime_type = "application/octet-stream"
    # Crear un objeto media usando la clase MediaIoBaseUpload con el objeto de tipo archivo y el tipo MIME del archivo
    media = MediaIoBaseUpload(file_object,mimetype=mime_type)
    # Llamar al método files().create() del servicio de Google Drive para crear el archivo
    try:
        service.files().create(body=file_metadata,media_body=media,fields='id').execute()
    except:
        print("Error al subir archivo")