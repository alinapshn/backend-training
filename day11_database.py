from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Column, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, relationship, sessionmaker

DATABASE_URL = "sqlite:///./ecobazar.db"

app = FastAPI()

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
   db = SessionLocal()
   try:
      yield db
   finally:
      db.close()

SessionDep = Annotated[Session, Depends(get_db)]

class ProductDB(Base):
   __tablename__ = "products"
   id = Column(Integer, primary_key=True, index=True)
   name = Column(String, unique=True, nullable=False)
   category = Column(String, nullable=False)
   price = Column(Float, nullable=False)
   stock = Column(Integer, nullable=False, default=0)

class OrderDB(Base):
   __tablename__ = "orders"
   id = Column(Integer, primary_key=True, index=True)
   product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
   quantity = Column(Integer, nullable=False)
   total_price = Column(Float, nullable=False)

   product = relationship("ProductDB")

Base.metadata.create_all(bind=engine)

class ProductCreate(BaseModel):
   name: str = Field(min_length=1, max_length=100)
   category: str = Field(min_length=1, max_length=50)
   price: float = Field(gt=0)
   stock: int = Field(ge=0)

class ProductUpdate(BaseModel):
   name: str | None = Field(default=None, min_length=1, max_length=100)
   category: str | None = Field(default=None, min_length=1, max_length=50)
   price: float | None = Field(default=None, gt=0)
   stock: int | None = Field(default=None, ge=0)

class ProductOut(BaseModel):
   id: int
   name: str
   category: str
   price: float
   model_config = ConfigDict(from_attributes=True)

class OrderCreate(BaseModel):
   product_id: int
   quantity: int = Field(gt=0)

class OrderOut(BaseModel):
   id: int
   quantity: int
   total_price: float
   product: ProductOut
   model_config = ConfigDict(from_attributes=True)

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
   product = get_product_by_id(payload.product_id, db)
   if product.stock < payload.quantity:
      raise HTTPException(status_code=400, detail="Not enough products available")
   product.stock -= payload.quantity
   total_price = payload.quantity * product.price
   new_order = OrderDB(
      product_id=payload.product_id,
      quantity=payload.quantity,
      total_price=total_price
   )
   db.add(new_order)
   db.commit()
   db.refresh(new_order)
   return new_order

@app.get("/orders", response_model=list[OrderOut])
def get_orders(db: SessionDep):
   orders = db.query(OrderDB).all()
   return orders 