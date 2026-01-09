from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import uuid4

app = FastAPI(title="Stock API", version="1.0.0")



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Modèles ---
class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0)
    quantity: int = Field(ge=0)

class Product(ProductCreate):
    id: str

# --- "Base de données" en mémoire (simple pour commencer) ---
db: List[Product] = []

# --- Endpoints CRUD ---
@app.get("/products", response_model=List[Product])
def list_products(
    q: Optional[str] = None,          # texte dans le nom
    min_qty: Optional[int] = None,    # quantité min
    max_qty: Optional[int] = None     # quantité max
):
    results = db

    if q is not None:
        q_lower = q.lower()
        results = [p for p in results if q_lower in p.name.lower()]

    if min_qty is not None:
        results = [p for p in results if p.quantity >= min_qty]

    if max_qty is not None:
        results = [p for p in results if p.quantity <= max_qty]

    return results

@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: str):
    for p in db:
        if p.id == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")

@app.post("/products", response_model=Product, status_code=201)
def create_product(payload: ProductCreate):
    new_product = Product(id=str(uuid4())[:8], **payload.model_dump())
    db.append(new_product)
    return new_product

@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: str, payload: ProductCreate):
    for i, p in enumerate(db):
        if p.id == product_id:
            updated = Product(id=product_id, **payload.model_dump())
            db[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Product not found")

@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: str):
    for i, p in enumerate(db):
        if p.id == product_id:
            db.pop(i)
            return
    raise HTTPException(status_code=404, detail="Product not found")
