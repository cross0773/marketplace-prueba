from fastapi import FastAPI, APIRouter, HTTPException, Depends
import os
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from models import Order, OrderItem, OrderCreate, OrderRead, OrderUpdate, Base
from typing import List
from common.config import settings  # Importar la configuración centralizada

# Configuración de la base de datos
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@localhost:5432/pedidos_db"
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()
router = APIRouter(prefix="/api/v1/pedidos", tags=["pedidos"])


# Endpoint de salud
@router.get("/health")
def health_check():
    return {"status": "ok"}


# Endpoints de pedidos
@router.get("/", response_model=List[OrderRead])
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()


@router.get("/{id}", response_model=OrderRead)
def get_order(id: int, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return db_order


@router.post("/", response_model=OrderRead)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    monto_total_calculado = 0
    order_items_data = []

    # 1. Iterar sobre los ítems del pedido para validar y calcular el total
    async with httpx.AsyncClient() as client:
        for item in order.items:
            try:
                # Verificar si el producto existe y obtener su precio
                url = f"{settings.PRODUCTOS_SERVICE_URL}/api/v1/productos/{item.id_producto}"
                response = await client.get(url)
                response.raise_for_status()
                producto_data = response.json()
                precio_producto = producto_data.get("precio", 0)

                # Calcular subtotal y añadir al total
                subtotal = precio_producto * item.cantidad
                monto_total_calculado += subtotal

                # Guardar datos para crear OrderItem más tarde
                order_items_data.append(
                    {
                        "id_producto": item.id_producto,
                        "cantidad": item.cantidad,
                        "precio_unitario": precio_producto,
                    }
                )

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise HTTPException(
                        status_code=404,
                        detail=f"El producto con id '{item.id_producto}' no existe.",
                    )
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Error al verificar el producto {item.id_producto}.",
                )
            except httpx.RequestError:
                raise HTTPException(
                    status_code=503,
                    detail="No se pudo comunicar con el servicio de productos.",
                )

    # 2. Crear el registro principal del Pedido (Order)
    db_order = Order(
        id_usuario=order.id_usuario, monto_total=monto_total_calculado, estado="pending"
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # 3. Crear los registros de los Ítems del Pedido (OrderItem)
    for item_data in order_items_data:
        db_item = OrderItem(**item_data, id_pedido=db_order.id)
        db.add(db_item)
    db.commit()
    db.refresh(db_order)  # Refrescar para cargar la relación 'items'

    # --- INICIO: Notificar al servicio de pagos para crear un registro pendiente ---
    try:
        async with httpx.AsyncClient() as client:
            pago_payload = {
                "id_pedido": db_order.id,
                "id_usuario": db_order.id_usuario,
                "monto": db_order.monto_total,
                "estado": "pending",  # El pago se crea como pendiente
                "metodo_pago": "N/A",
            }
            url = f"{settings.PAGOS_SERVICE_URL}/api/v1/pagos/"
            await client.post(url, json=pago_payload)
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        # Si la creación del pago pendiente falla, el pedido se creó pero queda inconsistente.
        # En un sistema real, esto requeriría una transacción distribuida o un mecanismo de compensación.
        # Por ahora, solo lo advertimos.
        print(
            f"ADVERTENCIA: El pedido {db_order.id} se creó, pero no se pudo registrar el pago pendiente. Error: {e}"
        )
    # --- FIN: Notificación ---

    return db_order


@router.put("/{id}", response_model=OrderRead)
async def update_order(id: int, order: OrderUpdate, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    # Simplificado: este endpoint ahora solo actualiza campos simples como el estado.
    # La lógica para editar ítems de un pedido es más compleja y se omite por ahora.
    for key, value in order.dict(exclude_unset=True).items():
        setattr(db_order, key, value)

    db.commit()
    db.refresh(db_order)
    return db_order


@router.delete("/{id}")
def delete_order(id: int, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    db.delete(db_order)
    db.commit()
    return {"message": "Pedido eliminado correctamente"}


# Incluir el enrutador
app.include_router(router)
