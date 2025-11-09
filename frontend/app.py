from flask import Flask, render_template
import os
import requests

# URL para el navegador del usuario
API_GATEWAY_URL_PUBLIC = os.getenv("API_GATEWAY_URL_PUBLIC", "http://localhost:8000")
# URL para la comunicación interna entre contenedores (Docker)
API_GATEWAY_URL_INTERNAL = os.getenv("API_GATEWAY_URL", "http://api-gateway:8000")
app = Flask(__name__)


def gw(path):
    return f"{API_GATEWAY_URL_INTERNAL.rstrip('/')}/{path.lstrip('/')}"


@app.route("/")
def index():
    return render_template("index.html", gateway_url=API_GATEWAY_URL_PUBLIC)


# Panel del Gateway
@app.route("/gateway")
def gateway():
    # Intenta leer /health del gateway
    try:
        r = requests.get(gw("/health"), timeout=3)
        health = (
            r.json()
            if r.headers.get("content-type", "").startswith("application/json")
            else r.text
        )
    except Exception as e:
        health = {"error": str(e)}
    return render_template(
        "gateway.html", gateway_url=API_GATEWAY_URL_PUBLIC, health=health
    )


# Pagos UI
@app.route("/pagos/")
def pagos():
    return render_template("pagos.html", gateway_url=API_GATEWAY_URL_PUBLIC)


# Pedidos UI
@app.route("/pedidos/")
def pedidos():
    return render_template("pedidos.html", gateway_url=API_GATEWAY_URL_PUBLIC)


# Productos UI
@app.route("/productos/")
def productos():
    return render_template("productos.html", gateway_url=API_GATEWAY_URL_PUBLIC)


# Auth UI
@app.route("/auth/")
def auth():
    return render_template("auth.html", gateway_url=API_GATEWAY_URL_PUBLIC)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
