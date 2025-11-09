from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from typing import List

from pydantic import BaseModel

# Define la base declarativa
Base = declarative_base()


class Order(Base):
    __tablename__ = "orders"

    # Columnas de la tabla
    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, index=True)
    monto_total = Column(Integer)
    estado = Column(String, default="pending")
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    activo = Column(Boolean, default=True)

    # Relación con los ítems del pedido
    items = relationship("OrderItem", back_populates="order")

    def __repr__(self):
        return f"<Order(id={self.id}, id_usuario={self.id_usuario})>"


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    id_pedido = Column(Integer, ForeignKey("orders.id"))
    id_producto = Column(Integer, index=True)
    cantidad = Column(Integer)
    precio_unitario = Column(Integer)  # Guardar el precio al momento de la compra

    order = relationship("Order", back_populates="items")


# --- Pydantic Models ---


class OrderItemBase(BaseModel):
    id_producto: int
    cantidad: int


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemRead(OrderItemBase):
    id: int
    id_pedido: int
    precio_unitario: int

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    id_usuario: int
    estado: str = "pending"
    activo: bool = True


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderRead(OrderBase):
    id: int
    monto_total: int
    fecha_creacion: datetime
    activo: bool
    items: List[OrderItemRead] = []

    class Config:
        from_attributes = True


class OrderUpdate(OrderBase):
    id_usuario: Optional[int] = None
    estado: Optional[str] = None
    activo: Optional[bool] = None

    class Config:
        from_attributes = True
