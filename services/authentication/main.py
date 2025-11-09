from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.middleware.cors import (
    CORSMiddleware,
)  # No es necesario si el gateway maneja CORS
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from common.config import settings
import bcrypt

# Inicializar la aplicación FastAPI
app = FastAPI()


# Modelo para el registro de usuarios
class UserRegister(BaseModel):
    username: str
    email: str
    password: str


# Base de datos temporal en memoria (en producción, usa una base de datos real)
users_db: List[Dict[str, Any]] = []

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


# Creamos un router para seguir el patrón de los otros servicios
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


# Endpoint de salud
@app.get("/health")
def health_check():
    return {"status": "ok"}


# --- Endpoints de autenticación en el router ---


@router.post("/register")
async def register_user(user: UserRegister):
    # Verificar si el usuario ya existe
    for existing_user in users_db:
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email ya registrado")

    # Hashear la contraseña antes de guardarla
    hashed_password = get_password_hash(user.password)
    user_dict = user.model_dump()
    user_dict["hashed_password"] = hashed_password
    del user_dict["password"]  # No guardamos la contraseña en texto plano

    users_db.append(user_dict)
    # No devolver el hash de la contraseña al cliente por seguridad.
    return {
        "message": "Usuario registrado exitosamente",
        "user": {"email": user.email, "username": user.username},
    }


# Endpoint para el login
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=30
    )  # Puedes mover esto a settings si lo deseas
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Incluimos el router en la app principal
app.include_router(router)


# Función para obtener el hash de la contraseña
def get_password_hash(password: str) -> str:
    if not isinstance(password, str):
        password = str(password)
    # Generar un salt y hacer hash de la contraseña
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


# la función verify_password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not isinstance(plain_password, str):
        plain_password = str(plain_password)
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except Exception:
        return False


# Función para autenticar al usuario
def authenticate_user(email: str, password: str):
    user = next((u for u in users_db if u["email"] == email), None)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user


# Función para crear el token de acceso
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
