from datetime import UTC, datetime, timedelta
from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from database import Base, SessionDep, engine
from models import OrderDB, OrderItemDB, ProductDB, UserDB
from schemas import (
   OrderCreate,
   OrderOut,
   ProductCreate,
   ProductUpdate,
   TokenOut,
   UserCreate,
   UserLogin,
   UserOut,
)

app = FastAPI()
Base.metadata.create_all(bind=engine)

SECRET_KEY = "secret-ecobazar-key-with-at-least-32-chars"
ALGORITHM = "HS256"
security = HTTPBearer()

def hash_password(password: str) -> str:
   pwd_bytes = password.encode("utf-8")
   salt = bcrypt.gensalt()
   hashed = bcrypt.hashpw(pwd_bytes, salt)
   return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
   return bcrypt.checkpw(
      plain_password.encode("utf-8"),
      hashed_password.encode("utf-8")
   )

def create_access_token(user_id: int) -> str:
   expire = datetime.now(UTC) + timedelta(minutes=60)
   payload = {"sub": str(user_id), "exp": expire}
   return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
      credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
      db: SessionDep,
) -> UserDB:
   token = credentials.credentials
   try: 
      payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
      user_id = int(payload["sub"])
   except (jwt.PyJWTError, KeyError, ValueError):
      raise HTTPException(status_code=401, detail="Invalid or expired token")
   user = db.query(UserDB).filter(UserDB.id == user_id).first()
   if not user:
      raise HTTPException(status_code=401, detail="User not found")
   return user

CurrentUserDep = Annotated[UserDB, Depends(get_current_user)]

def get_product_by_id(product_id: int, db: SessionDep) -> ProductDB:
   product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
   if not product:
      raise HTTPException(status_code=404, detail="Product not found")
   return product 

ProductDep = Annotated[ProductDB, Depends(get_product_by_id)]

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

@app.post("/login", response_model=TokenOut)
def login_user(payload: UserLogin, db: SessionDep):
   clean_mail = payload.email.strip().lower()
   user = db.query(UserDB).filter(UserDB.email == clean_mail).first()
   if not user or not verify_password(payload.password, user.hashed_password):
      raise HTTPException(status_code=401, detail="Invalid email or password")
   token = create_access_token(user.id)
   return {"access_token": token, "token_type": "bearer"}

@app.get("/profile", response_model=UserOut)
def get_profile(user: CurrentUserDep):
   return user

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
def create_order(payload: OrderCreate, current_user: CurrentUserDep, db: SessionDep):
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
   new_order = OrderDB(user_id=current_user.id, total_price=total_price, items=order_items)
   db.add(new_order)
   db.commit()
   db.refresh(new_order)
   return new_order

@app.get("/orders", response_model=list[OrderOut])
def get_orders(current_user: CurrentUserDep, db: SessionDep):
   orders = db.query(OrderDB).filter(OrderDB.user_id == current_user.id).all()
   return orders 