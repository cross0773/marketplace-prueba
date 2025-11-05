import pytest
from fastapi.testclient import TestClient
from main import app, get_password_hash, verify_password
import bcrypt  # Usar bcrypt directamente

client = TestClient(app)

def test_password_hashing():
    # Prueba que el hash funcione correctamente
    password = "test123"
    hashed = get_password_hash(password)
    assert hashed is not None
    assert password not in hashed  # Asegura que el hash no sea texto plano
    # Verifica con bcrypt directamente
    assert bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def test_verify_password():
    # Prueba que la verificación de contraseña funcione
    password = "test123"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpass", hashed) is False

def test_register_user():
    # Prueba el endpoint de registro
    test_user = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "test123"
    }
    response = client.post("/register", json=test_user)
    assert response.status_code == 200
    assert "message" in response.json()
    assert "user" in response.json()
    assert "hashed_password" in response.json()["user"]
    assert test_user["password"] not in str(response.json())

def test_duplicate_email():
    # Prueba que no se puedan registrar emails duplicados
    test_user = {
        "username": "testuser2",
        "email": "test@example.com",  # Mismo email que el test anterior
        "password": "test123"
    }
    response = client.post("/register", json=test_user)
    assert response.status_code == 400
    assert "ya registrado" in response.json()["detail"].lower()