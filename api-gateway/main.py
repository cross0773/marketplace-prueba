from fastapi import FastAPI, APIRouter, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

# Define la instancia de la aplicación FastAPI.
app = FastAPI(title="API Gateway Taller Microservicios")

# Configura CORS (Cross-Origin Resource Sharing).
# Esto es esencial para permitir que el frontend se comunique con el gateway.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000"],  # Permite peticiones desde cualquier origen (ajustar en producción)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Crea un enrutador para las peticiones de los microservicios.
router = APIRouter(prefix="/api/v1")

# Define los microservicios y sus URLs.
# La URL debe coincidir con el nombre del servicio definido en docker-compose.yml.
SERVICES = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001"),
    "productos": os.getenv("PRODUCTOS_SERVICE_URL", "http://productos-service:8004"),
    "pedidos": os.getenv("PEDIDOS_SERVICE_URL", "http://pedidos-service:8003"),
    "pagos": os.getenv("PAGOS_SERVICE_URL", "http://pagos-service:8002")
}

# Crea un cliente HTTP asíncrono que se reutilizará en todas las peticiones.
client = httpx.AsyncClient()

async def forward_request(service_name: str, path: str, request: Request):
    """Función genérica para redirigir peticiones a los microservicios."""
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found.")

    service_url = f"{SERVICES[service_name].rstrip('/')}/{path.lstrip('/')}"

    try:
        # Prepara los datos para la petición
        headers = {key: value for key, value in request.headers.items() if key.lower() not in ['host']} #ruta productos
        params = request.query_params
        content = await request.body()

        # Imprimir información de depuración
        print(f"Forwarding request to: {service_url}")
        print(f"Headers: {headers}")
        print(f"Params: {params}")

        # Usa httpx para enviar la petición de forma asíncrona
        response = await client.request(
            method=request.method,
            url=service_url,
            headers=headers,
            params=params,
            content=content,
            timeout=5  # Timeout de 5 segundos
        )

        response.raise_for_status()

        # Devuelve la respuesta del microservicio
        content_type = response.headers.get('content-type', '')
        if content_type.startswith('application/json'):
            return response.json()
        return response.text

    except httpx.ConnectError as e:
        print(f"Connection error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"No se pudo conectar al servicio {service_name}: {str(e)}"
        )
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {str(e)}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text
        )
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado: {str(e)}"
        )

# Rutas genéricas que capturan todas las peticiones
@router.get("/{service_name}/{path:path}")
async def get_route(service_name: str, path: str, request: Request):
    return await forward_request(service_name, path, request)

@router.post("/{service_name}/{path:path}")
async def post_route(service_name: str, path: str, request: Request):
    return await forward_request(service_name, path, request)

@router.put("/{service_name}/{path:path}")
async def put_route(service_name: str, path: str, request: Request):
    return await forward_request(service_name, path, request)

@router.delete("/{service_name}/{path:path}")
async def delete_route(service_name: str, path: str, request: Request):
    return await forward_request(service_name, path, request)

# Incluye el router en la aplicación principal.
app.include_router(router)

# Endpoint de salud para verificar el estado del gateway.
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API Gateway is running."}
