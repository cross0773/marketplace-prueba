from fastapi import FastAPI, APIRouter, HTTPException, Depends
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from models import Order, OrderCreate, OrderRead, OrderUpdate, Base
from typing import List

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
router = APIRouter()


# Endpoint de salud
@router.get("/health")
def health_check():
    return {"status": "ok"}


# Endpoints de pedidos
@router.get("/", response_model=List[OrderRead])
async def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()


@router.post("/", response_model=OrderRead)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    db_order = Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@router.put("/{id}", response_model=OrderRead)
async def update_order(id: int, order: OrderUpdate, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    for key, value in order.dict(exclude_unset=True).items():
        setattr(db_order, key, value)
    db.commit()
    db.refresh(db_order)
    return db_order


@router.delete("/{id}")
async def delete_order(id: int, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    db.delete(db_order)
    db.commit()
    return {"message": "Pedido eliminado correctamente"}


# Incluir el enrutador
app.include_router(router)
