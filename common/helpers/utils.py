import json
import requests
import httpx
from datetime import datetime
from typing import Any

# TODO: Define funciones de ayuda que puedan ser útiles en varios microservicios.


def format_date(dt_object: datetime):
    """Formatea un objeto datetime a una cadena de texto."""
    return dt_object.strftime("%Y-%m-%d %H:%M:%S")

async def send_async_request(url: str, method: str = "GET", json_data: Any = None):
    """
    Envía una petición HTTP asíncrona a otro microservicio usando httpx.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(method, url, json=json_data, timeout=5.0)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            print(f"Error en la petición asíncrona: {e}")
            # En un caso real, podrías querer manejar diferentes tipos de errores
            # o relanzar una excepción personalizada.
            return None

# TODO: Agrega más funciones de utilidad según sea necesario.

# ------------------------------------------------------------------------------
# Ejemplo de uso en un microservicio
# from common.helpers.utils import send_request_to_service
# from common.config import settings
# 
# URL del servicio de autenticación
# auth_url = f"{settings.AUTH_SERVICE_URL}/users"
# 
# try:
#     # Envía una petición para obtener todos los usuarios del servicio de autenticación
#     users = send_request_to_service(auth_url)
#     print("Usuarios obtenidos:", users)
# except requests.exceptions.RequestException:
#     print("No se pudo obtener la lista de usuarios.")
#