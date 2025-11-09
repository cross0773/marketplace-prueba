from fastapi import FastAPI, APIRouter, HTTPException
import os
import httpx

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
    # --- INICIO: Validación de existencia y pertenencia del pedido ---
    async with httpx.AsyncClient() as client:
        try:
            # 1. Verificar si el pedido existe
            url = f"{settings.PEDIDOS_SERVICE_URL}/api/v1/pedidos/{payment.id_pedido}"
            response = await client.get(url)
            response.raise_for_status()
            pedido_data = response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"El pedido con id '{payment.id_pedido}' no existe.",
                )
            raise HTTPException(
                status_code=e.response.status_code,
                detail="Error al verificar el pedido.",
            )
        except httpx.RequestError:
            raise HTTPException(
                status_code=503,
                detail="No se pudo comunicar con el servicio de pedidos.",
            )

    # 2. Validar que el usuario del pago es el mismo que el del pedido
    if pedido_data.get("id_usuario") != payment.id_usuario:
        raise HTTPException(
            status_code=403,
            detail=f"El usuario (id: {payment.id_usuario}) no tiene permiso para pagar este pedido, que pertenece al usuario (id: {pedido_data.get('id_usuario')}).",
        )

    # --- FIN: Validación ---

    new_payment = Payment(**payment.dict())
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return new_payment


@router.put("/{id}", response_model=PaymentRead)
def update_pago(id: int, pago: PaymentUpdate, db: Session = Depends(get_db)):
    db_pago = db.query(Payment).filter(Payment.id == id).first()
    if not db_pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    for key, value in pago.dict(exclude_unset=True).items():
        setattr(db_pago, key, value)
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
