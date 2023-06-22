import os
import base64
from typing import List
import time

from email.mime.text import MIMEText
import datetime


class GmailException(Exception):
	"""gmail base exception class"""

class NoEmailFound(GmailException):
	"""no email found"""

# Función para obtener archivos dentro del mail
def get_file_data(validate_service, message_id, attachment_id, file_name, save_location):
	service = validate_service
	response = service.users().messages().attachments().get(
		userId='me',
		messageId=message_id,
		id=attachment_id
	).execute()

	file_data = base64.urlsafe_b64decode(response.get('data').encode('UTF-8'))
	return file_data

def get_message_detail(validate_service, message_id, msg_format='metadata', metadata_headers: List=None):
	service = validate_service
	message_detail = service.users().messages().get(
		userId='me',
		id=message_id,
		format=msg_format,
		metadataHeaders=metadata_headers
	).execute()
	return message_detail

def search_emails(validate_service, query_string: str, label_ids: List=None):
	# Valido el servicio
	service = validate_service
	# Intentar obtener listado de mensajes 
	try:
		# Obtengo una lista de mensajes que coinciden con mi query
		message_list_response = service.users().messages().list(
			userId='me',
			labelIds=label_ids,
			q=query_string
		).execute()
		#print("Mensaje_List_response ", message_list_response)
		message_items = message_list_response.get('messages')
		#print("Mensaje_items ", message_items)
		# Obtengo la referencia continuar en la siguiente pág
		next_page_token = message_list_response.get('nextPageToken')
		
		# Mientras el token sea valido, ejecuto
		while next_page_token:
			message_list_response = service.users().messages().list(
				userId='me',
				labelIds=label_ids,
				q=query_string,
				pageToken=next_page_token
			).execute()

			message_items.extend(message_list_response.get('messages'))
			
			next_page_token = message_list_response.get('nextPageToken')
		
			#Recorro el listado de mails y les cambio su estado "unread" a "read"
			for message in message_items:
			# Cambio el estado para un ID dado
				service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()

		#print("Resultado funcion:\n", message_items)
		return message_items
	except Exception as e:
		raise NoEmailFound('No emails returned')
	
def send_mail (id,nombre,Mail,fecha_vencimiento, fecha_actual, validate_object):
	# Si no tengo fecha de vencimiento significa que tengo ningún AOC en mis registros
	id = id
	prov = nombre
	Mail = Mail
	fe = fecha_vencimiento
	fecha_actual = fecha_actual
	service = validate_object

	# En este caso, al no haber una fecha de vencimiento, podemos decir que nunca envió un AOC
	if not fe:
		# Crear un mensaje de correo electrónico con el asunto y el cuerpo correspondientes
		mensaje = MIMEText(f"Estimado/a {nombre}\nDesde el equipo de Gestión de Riesgos de Terceras Partes de Seguridad Informática de \n\
		      					Mercado Pago, le informamos que como parte de nuestro proceso de evaluación de riesgo,\n\
		      					requerimos que nos envíe una copia de su AoC (Attestation of Conpliance) vigente.\n\
		      					\n\n\
		      					El Aoc es un documento que certifica que su empresa cumple con los estándares\n\
		      					de seguridad establecidos por PCI DSS. Para nosotros es un requisito indispensable para operar\n\
		      					como adquiriente en el ecosistema de MP\n\
		      					Le solicitamos que nos envíe una copia para evitar posibles inconvenientes en el servico")
		mensaje["to"] = Mail
		mensaje["subject"] = "Solicitud AoC"
		# Codificar el mensaje en formato base64url
		mensaje = base64.urlsafe_b64encode(mensaje.as_bytes())
		# Crear un diccionario con el campo "raw" que contiene el mensaje codificado
		mensaje = {"raw": mensaje.decode()}
		# Enviar el mensaje usando el servicio de Gmail y capturar la respuesta
		respuesta = service.users().messages().send(userId="me", body=mensaje).execute()
		# Imprimir el ID del mensaje enviado
		print(f"Mensaje enviado con ID: {respuesta['id']}")
		# Si la diferencia es negativa o cero, significa que no pasó la fecha de vencimiento
		return(fecha_actual)

    # Si no está en blanco, verificar si ya pasó la fecha de vencimiento
	else:
		
		fe = datetime.datetime.strptime(fe,"%d/%m/%Y")
		
		# Convertir la fecha de vencimiento a un objeto datetime
		# Obtener la fecha actual
		# Calcular la diferencia en días entre las dos fechas
		diferencia = (fecha_actual - fe).days
	
    	# Si la diferencia es positiva, significa que ya pasó la fecha de vencimiento

		if diferencia > 0:
			# Imprimir los días desde que venció
			print(f"La fecha de vencimiento fue hace {diferencia} días")
			# Crear un mensaje de correo electrónico con el asunto y el cuerpo correspondientes
			mensaje = MIMEText(f"Estimado/a {nombre}, le recordamos que la fecha de vencimiento de su AoC fue el {fe.strftime('%d/%m/%Y')}. \n\
		      					Por favor, comuníquese con nosotros a la brevedad.\n\
		      					Att: Equipo de Gestión de Riesgos de Terceras Partes de Seguridad Informática de \n\
		      					Mercado Pago")
			mensaje["to"] = Mail
			mensaje["subject"] = "AoC vencido"
			# Codificar el mensaje en formato base64url
			mensaje = base64.urlsafe_b64encode(mensaje.as_bytes())
			# Crear un diccionario con el campo "raw" que contiene el mensaje codificado
			mensaje = {"raw": mensaje.decode()}
			# Enviar el mensaje usando el servicio de Gmail y capturar la respuesta
			respuesta = service.users().messages().send(userId="me", body=mensaje).execute()
			# Imprimir el ID del mensaje enviado
			print(f"Mensaje enviado con ID: {respuesta['id']}")
			 # Si la diferencia es negativa o cero, significa que no pasó la fecha de vencimiento
			return(fecha_actual)
		# Aún no venció
		else:
			mensaje = MIMEText(f"Estimado/a {nombre}\nDesde el equipo de Gestión de Riesgos de Terceras Partes de Seguridad Informática de \n\
		      					Mercado Pago, le informamos que como parte de nuestro proceso de evaluación de riesgo,\n\
		      					requerimos que nos envíe una copia de su AoC (Attestation of Conpliance) vigente.\n\
		      					\n\n\
		      					El Aoc es un documento que certifica que su empresa cumple con los estándares\n\
		      					de seguridad establecidos por PCI DSS. Para nosotros es un requisito indispensable para operar\n\
		      					como adquiriente en el ecosistema de MP\n\n\
		      					Le solicitamos que nos envíe una copia para evitar posibles inconvenientes en el servico ")
			mensaje["to"] = Mail
			mensaje["subject"] = "Recordatorio de fecha de vencimiento"
			# Codificar el mensaje en formato base64url
			mensaje = base64.urlsafe_b64encode(mensaje.as_bytes())
			# Crear un diccionario con el campo "raw" que contiene el mensaje codificado
			mensaje = {"raw": mensaje.decode()}
			# Enviar el mensaje usando el servicio de Gmail y capturar la respuesta
			respuesta = service.users().messages().send(userId="me", body=mensaje).execute()
			# Imprimir el ID del mensaje enviado
			print(f"Mensaje enviado con ID: {respuesta['id']}")
			 # Si la diferencia es negativa o cero, significa que no pasó la fecha de vencimiento
			return(fecha_actual)


