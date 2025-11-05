from fastapi import FastAPI, APIRouter, HTTPException
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Payment, PaymentCreate, PaymentRead, PaymentUpdate, Base  # Modelos personalizados y base de SQLAlchemy
from sqlalchemy.orm import Session
from fastapi import Depends

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/pagos_db")
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

router = APIRouter()


@app.get("/health")
def health_check():
    """Endpoint de salud para verificar el estado del servicio."""
    return {"status": "ok"}

@router.get("/", response_model=list[PaymentRead])
async def get_pagos(db: Session = Depends(get_db)):
    pagos = db.query(Payment).all()
    return pagos

@router.post("/", response_model=PaymentRead)
async def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
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
    for key, value in pago.dict(exclude_unset=True).items():
        setattr(db_pago, key, value)
    db.commit()
    db.refresh(db_pago)
    return db_pago
    
@router.delete("/{id}")
async def delete_pago(id: int, db: Session = Depends(get_db)):
    db_pago = db.query(Payment).filter(Payment.id == id).first()
    if not db_pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    db.delete(db_pago)
    db.commit()
    return {"message": "Pago eliminado"}
    


app.include_router(router)
