from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

from pydantic import BaseModel

# Define la base declarativa
Base = declarative_base()


class Order(Base):
    """
    Plantilla de modelo de datos para un recurso.
    Ajusta esta clase según los requisitos de tu tema.
    """

    __tablename__ = "orders"

    # Columnas de la tabla
    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, index=True)
    id_producto = Column(Integer, index=True)
    cantidad = Column(Integer)
    monto_total = Column(Integer)
    estado = Column(String, default="pending")
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    activo = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Order(id_usuario={self.id_usuario}, id_producto={self.id_producto})>"


class OrderBase(BaseModel):
    id_usuario: int
    id_producto: int
    cantidad: int
    monto_total: int
    estado: str = "pending"
    activo: bool = True


class OrderCreate(OrderBase):
    pass


class OrderRead(OrderBase):
    id: int
    fecha_creacion: datetime
    activo: bool

    class Config:
        from_attributes = True


class OrderUpdate(OrderBase):
    id_usuario: Optional[int] = None
    id_producto: Optional[int] = None
    cantidad: Optional[int] = None
    monto_total: Optional[int] = None
    estado: Optional[str] = None
    activo: Optional[bool] = None

    class Config:
        from_attributes = True
