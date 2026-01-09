from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Product

app = FastAPI()

# CORS (OK pour projet)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crée les tables automatiquement (mini-projet)
Base.metadata.create_all(bind=engine)

class ProductCreate(BaseModel):
    name: str
    price: float
    quantity: int

class ProductOut(ProductCreate):
    id: int

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/products", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).order_by(Product.id.desc()).all()

@app.post("/products", response_model=ProductOut)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    item = Product(
        name=payload.name,
        price=payload.price,
        quantity=payload.quantity
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@app.put("/products/{id}", response_model=ProductOut)
def update_product(id: int, payload: ProductCreate, db: Session = Depends(get_db)):
    item = db.query(Product).filter(Product.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Product not found")

    item.name = payload.name
    item.price = payload.price
    item.quantity = payload.quantity
    db.commit()
    db.refresh(item)
    return item

@app.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    item = db.query(Product).filter(Product.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(item)
    db.commit()
    return {"deleted": True}
