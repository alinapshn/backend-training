from typing import Annotated

import bcrypt
from fastapi import Depends, FastAPI, HTTPException

from database import Base, SessionDep, engine
from models import OrderDB, OrderItemDB, ProductDB, UserDB
from schemas import (
   OrderCreate,
   OrderOut,
   ProductCreate,
   ProductUpdate,
   UserCreate,
   UserOut,
)

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.post("/products", status_code=201)
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

@app.get("/products")
def get_products(db: SessionDep): 
   products = db.query(ProductDB).filter(ProductDB.stock > 0).all()
   return products

def get_product_by_id(product_id: int, db: SessionDep) -> ProductDB:
   product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
   if not product:
      raise HTTPException(status_code=404, detail="Product not found")
   return product 

ProductDep = Annotated[ProductDB, Depends(get_product_by_id)]

@app.get("/products/{product_id}")
def get_product(product: ProductDep):
   return product

@app.patch("/products/{product_id}")
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

@app.delete("/products/{product_id}")
def delete_product(product: ProductDep, db: SessionDep):
   db.delete(product)
   db.commit()
   return {"message": f"Product {product.name} deleted"}

@app.post('/orders', status_code=201, response_model=OrderOut)
def create_order(payload: OrderCreate, db: SessionDep):
   total_price = 0
   order_items = []
   for item in payload.items:
      product = get_product_by_id(item.product_id, db)
      if product.stock < item.quantity:
         raise HTTPException(status_code=400, detail="Not enough products available")
      product.stock -= item.quantity
      total_price += item.quantity * product.price
      new_item = OrderItemDB(
         product_id=item.product_id,
         quantity=item.quantity,
         price_at_purchase=product.price
      )
      order_items.append(new_item)
   new_order = OrderDB(total_price=total_price, items=order_items)
   db.add(new_order)
   db.commit()
   db.refresh(new_order)
   return new_order

@app.get("/orders", response_model=list[OrderOut])
def get_orders(db: SessionDep):
   orders = db.query(OrderDB).all()
   return orders 

def hash_password(password: str) -> str:
   pwd_bytes = password.encode("utf-8")
   salt = bcrypt.gensalt()
   hashed = bcrypt.hashpw(pwd_bytes, salt)
   return hashed.decode("utf-8")

@app.post("/register", status_code=201, response_model=UserOut)
def create_user(payload: UserCreate, db: SessionDep):
   clean_mail = payload.email.strip().lower()
   is_exist = db.query(UserDB).filter(UserDB.email == clean_mail).first()
   if is_exist:
      raise HTTPException(status_code=400, detail="Email already registered")
   new_user = UserDB(email=clean_mail, hashed_password=hash_password(payload.password))
   db.add(new_user)
   db.commit()
   db.refresh(new_user)
   return new_user