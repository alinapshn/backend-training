from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

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

class ProductDB(Base):
   __tablename__ = "products"
   id = Column(Integer, primary_key=True, index=True)
   name = Column(String, unique=True, nullable=False)
   category = Column(String, nullable=False)
   price = Column(Float, nullable=False)
   stock = Column(Integer, nullable=False, default=0)

Base.metadata.create_all(bind=engine)

class ProductCreate(BaseModel):
   name: str = Field(min_length=1, max_length=100)
   category: str = Field(min_length=1, max_length=50)
   price: float = Field(gt=0)
   stock: int = Field(ge=0)

@app.post("/products", status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):  # noqa: B008
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
def get_products(db: Session = Depends(get_db)):  # noqa: B008
   products = db.query(ProductDB).filter(ProductDB.stock > 0).all()
   return products