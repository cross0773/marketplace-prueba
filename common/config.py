import os
from dotenv import load_dotenv

# Carga las variables de entorno del archivo .env
# Esto asegura que las configuraciones se obtengan desde el entorno de ejecución,
# lo que es una buena práctica para entornos de desarrollo y producción.
load_dotenv()

class Settings:
    """Clase para gestionar las configuraciones de la aplicación."""
    
    # URLs de los servicios
    # La URL del API Gateway se obtiene de las variables de entorno.
    API_GATEWAY_URL: str = os.getenv("API_GATEWAY_URL", "http://localhost:8000")
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")
    PRODUCTOS_SERVICE_URL: str = os.getenv("PRODUCTOS_SERVICE_URL", "http://productos-service:8004")
    PEDIDOS_SERVICE_URL: str = os.getenv("PEDIDOS_SERVICE_URL", "http://pedidos-service:8003")
    PAGOS_SERVICE_URL: str = os.getenv("PAGOS_SERVICE_URL", "http://pagos-service:8002")

    # Configuraciones para la autenticación con JWT.
    SECRET_KEY: str = os.getenv("SECRET_KEY", "c3a3b7a9f8e1d6c0b5a4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2") # Clave secreta para firmar tokens
    ALGORITHM: str = "HS256"

# Crea una instancia de la clase de configuración.
settings = Settings()

# --------------------------------------------------------------------------
# Los estudiantes pueden importar este objeto settings en cualquier parte 
# de su código para acceder a las configuraciones de manera consistente.
# 
# Ejemplo de uso en un microservicio
# from common.config import settings
# 
# Ahora puedes acceder a las variables de configuración
# api_url = settings.API_GATEWAY_URL
# 