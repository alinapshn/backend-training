from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from database import SessionDep
from models import ProductDB
from schemas import ProductCreate, ProductUpdate
from security import AdminUserDep

router = APIRouter(prefix="/products", tags=["Products"])

def get_product_by_id(product_id: int, db: SessionDep) -> ProductDB:
   product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
   if not product:
      raise HTTPException(status_code=404, detail="Product not found")
   return product 

ProductDep = Annotated[ProductDB, Depends(get_product_by_id)]

@router.post("", status_code=201)
def create_product(payload: ProductCreate, admin: AdminUserDep, db: SessionDep): 
   clean_name = payload.name.strip()
   clean_category = payload.category.strip().lower()
   if clean_name == "" or clean_category == "":
      raise HTTPException(status_code=400, detail="Name and category cannot be blank")
   is_exist = db.query(ProductDB).filter(ProductDB.name == clean_name).first()
   if is_exist:
      raise HTTPException(status_code=400, detail="Product with this name already exists")
   new_product = ProductDB(
      name=clean_name,
      category=clean_category,
      description=payload.description,
      price=payload.price,
      stock=payload.stock
   )
   db.add(new_product)
   db.commit()
   db.refresh(new_product)
   return new_product

@router.get("")
def get_products(
   db: SessionDep, 
   search: str | None = None,
   category: str | None = None,
   min_price: float | None = Query(default=None, ge=0),
   max_price: float | None = Query(default=None, ge=0),
   limit: int = Query(default=10, ge=1, le=100),
   offset: int = Query(default=0, ge=0)
): 
   if min_price is not None and max_price is not None and min_price > max_price:
      raise HTTPException(status_code=400, detail="min_price cannot be greater than max_price")

   query = db.query(ProductDB).filter(ProductDB.stock > 0)

   if category is not None:
      clean_category = category.strip().lower()
      if clean_category:
         query = query.filter(ProductDB.category == clean_category)

   if search is not None:
      clean_search = search.strip().lower()
      if clean_search:
         query = query.filter(ProductDB.name.ilike(f"%{clean_search}%"))

   if min_price is not None: 
      query = query.filter(ProductDB.price >= min_price)

   if max_price is not None:
      query = query.filter(ProductDB.price <= max_price)

   products = query.order_by(ProductDB.id).offset(offset).limit(limit).all()
   return products

@router.get("/{product_id}")
def get_product(product: ProductDep):
   return product

@router.patch("/{product_id}")
def update_product(payload: ProductUpdate, product: ProductDep, admin: AdminUserDep, db: SessionDep):
   if payload.name is not None:
      clean_name = payload.name.strip()
      if clean_name == "":
         raise HTTPException(status_code=400, detail="Name cannot be blank")

      is_exist = db.query(ProductDB).filter(
         ProductDB.name == clean_name, ProductDB.id != product.id
         ).first()
      if is_exist:
         raise HTTPException(status_code=400, detail="Product with this name already exists")
      product.name = clean_name

   if payload.category is not None:
      clean_category = payload.category.strip().lower()
      if clean_category == "":
         raise HTTPException(status_code=400, detail="Category cannot be blank")
      product.category = clean_category

   if payload.description is not None:
      product.description = payload.description

   if payload.price is not None:
      product.price = payload.price

   if payload.stock is not None:
      product.stock = payload.stock

   db.commit()
   db.refresh(product)
   return product 

@router.delete("/{product_id}")
def delete_product(product: ProductDep, admin: AdminUserDep, db: SessionDep):
   db.delete(product)
   db.commit()
   return {"message": f"Product {product.name} deleted"}
