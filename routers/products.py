from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from database import SessionDep
from models import ProductDB
from schemas import ProductCreate, ProductUpdate

router = APIRouter(prefix="/products", tags=["Products"])

def get_product_by_id(product_id: int, db: SessionDep) -> ProductDB:
   product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
   if not product:
      raise HTTPException(status_code=404, detail="Product not found")
   return product 

ProductDep = Annotated[ProductDB, Depends(get_product_by_id)]

@router.post("", status_code=201)
def create_product(payload: ProductCreate, db: SessionDep): 
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
      price=payload.price,
      stock=payload.stock
   )
   db.add(new_product)
   db.commit()
   db.refresh(new_product)
   return new_product

@router.get("")
def get_products(db: SessionDep): 
   products = db.query(ProductDB).filter(ProductDB.stock > 0).all()
   return products

@router.get("/{product_id}")
def get_product(product: ProductDep):
   return product

@router.patch("/{product_id}")
def update_product(payload: ProductUpdate, product: ProductDep, db: SessionDep):
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

   if payload.price is not None:
      product.price = payload.price

   if payload.stock is not None:
      product.stock = payload.stock

   db.commit()
   db.refresh(product)
   return product 

@router.delete("/{product_id}")
def delete_product(product: ProductDep, db: SessionDep):
   db.delete(product)
   db.commit()
   return {"message": f"Product {product.name} deleted"}
