from fastapi import FastAPI, APIRouter, HTTPException
import os
import httpx
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import (
    Payment,
    PaymentCreate,
    PaymentRead,
    PaymentUpdate,
    Base,
)  # Modelos personalizados y base de SQLAlchemy
from sqlalchemy.orm import Session
from fastapi import Depends
from common.config import settings  # Importar la configuración centralizada

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@localhost:5432/pagos_db"
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

# Inicializa la BD y crea tablas al iniciar
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(prefix="/api/v1/pagos", tags=["pagos"])


@app.get("/health")
def health_check():
    """Endpoint de salud para verificar el estado del servicio."""
    return {"status": "ok"}


@router.get("/", response_model=list[PaymentRead])
def get_pagos(db: Session = Depends(get_db)):
    pagos = db.query(Payment).all()
    return pagos


@router.post("/", response_model=PaymentRead)
async def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    # Este endpoint ahora es llamado por el servicio de pedidos para crear un registro PENDIENTE.
    # Las validaciones complejas se mueven al proceso de pago real (PUT).
    new_payment = Payment(**payment.dict())
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return new_payment


@router.put("/{id}", response_model=PaymentRead)
async def update_pago(id: int, pago: PaymentUpdate, db: Session = Depends(get_db)):
    db_pago = db.query(Payment).filter(Payment.id == id).first()
    if not db_pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    # --- INICIO: Lógica de procesamiento de pago ---
    # 1. Seguridad: El monto pagado debe ser >= al monto registrado en el pago pendiente.
    if pago.monto < db_pago.monto:
        raise HTTPException(
            status_code=400,
            detail=f"El monto a pagar ({pago.monto}) no puede ser menor al monto del pedido ({db_pago.monto}).",
        )

    # Actualizamos los campos del pago
    db_pago.monto = pago.monto  # Actualiza por si pagó de más
    db_pago.metodo_pago = pago.metodo_pago
    db_pago.estado = "completed"  # Se marca como completado
    db_pago.fecha_pago = datetime.utcnow()  # Se registra la fecha del pago

    # --- INICIO: Notificar al servicio de pedidos para actualizar el estado ---
    try:
        async with httpx.AsyncClient() as client:
            order_update_payload = {"estado": "completed"}
            url = f"{settings.PEDIDOS_SERVICE_URL}/api/v1/pedidos/{db_pago.id_pedido}"
            await client.put(url, json=order_update_payload)
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        # Si la notificación falla, no revertimos el pago, pero es importante registrarlo.
        # En un sistema de producción, esto podría encolarse para un reintento.
        print(
            f"ADVERTENCIA: El pago {db_pago.id} se completó, pero no se pudo actualizar el estado del pedido {db_pago.id_pedido}. Error: {e}"
        )
    # --- FIN: Notificación ---

    db.commit()
    db.refresh(db_pago)
    return db_pago


@router.put("/by-order/{order_id}", response_model=PaymentRead)
def update_pago_by_order_id(
    order_id: int, pago_update: PaymentUpdate, db: Session = Depends(get_db)
):
    """Actualiza un pago usando el ID del pedido. Usado por el servicio de pedidos."""
    db_pago = db.query(Payment).filter(Payment.id_pedido == order_id).first()
    if not db_pago:
        raise HTTPException(
            status_code=404, detail=f"No se encontró un pago para el pedido {order_id}"
        )

    # Solo actualizamos el monto, ya que es lo único que cambia si se edita la cantidad del pedido.
    if pago_update.monto is not None:
        db_pago.monto = pago_update.monto
        db.commit()
        db.refresh(db_pago)
    return db_pago


@router.delete("/{id}")
def delete_pago(id: int, db: Session = Depends(get_db)):
    db_pago = db.query(Payment).filter(Payment.id == id).first()
    if not db_pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    db.delete(db_pago)
    db.commit()
    return {"message": "Pago eliminado"}


app.include_router(router)
