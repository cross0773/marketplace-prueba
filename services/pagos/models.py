from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

from pydantic import BaseModel


# Define la base declarativa
Base = declarative_base()


class Payment(Base):
    """
    Plantilla de modelo de datos para un recurso.
    Ajusta esta clase según los requisitos de tu tema.
    """

    __tablename__ = "payments"

    # Columnas de la tabla
    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, index=True)  # ID del usuario (cliente o vendedor)
    id_pedido = Column(Integer, index=True)  # ID del pedido relacionado
    monto = Column(Integer)  # Monto en centavos para precisión
    moneda = Column(String, default="COP")
    estado = Column(String, default="pending")  # Ej. pending, completed, failed
    metodo_pago = Column(String)  # Ej. credit_card, paypal
    fecha_pago = Column(DateTime, nullable=True)  # Fecha en que se completa el pago
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    # agrego columna adicional de pagos
    activo = Column(Boolean, default=True)
    fecha_actualizacion = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.monto})>"


class PaymentBase(BaseModel):
    id_usuario: int
    id_pedido: int
    monto: int
    moneda: str = "COP"
    estado: str = "pending"
    metodo_pago: Optional[str] = None
    activo: bool = True
    fecha_actualizacion: Optional[datetime] = None


class PaymentCreate(PaymentBase):
    pass


class PaymentRead(PaymentBase):
    id: int
    fecha_creacion: datetime
    fecha_pago: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None


class PaymentUpdate(PaymentBase):
    id_usuario: Optional[int] = None
    id_pedido: Optional[int] = None
    monto: Optional[int] = None
    moneda: Optional[str] = None
    estado: Optional[str] = None
    metodo_pago: Optional[str] = None
    activo: Optional[bool] = None

    class Config:
        from_attributes = True  # Compatibilidad con Pydantic V2
