from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

products = [
    {"id": 1, "name": "Keratin Shampoo", "category": "hair", "price": 25, "stock": 5},
    {"id": 2, "name": "Hydrating Mask", "category": "hair", "price": 40, "stock": 0},
    {"id": 3, "name": "Heat Protection Spray", "category": "hair", "price": 30, "stock": 3},
    {"id": 4, "name": "Vitamin C Face Cream", "category": "face", "price": 55, "stock": 2},
    {"id": 5, "name": "Hyaluronic Serum", "category": "face", "price": 70, "stock": 4},
]

class ProductCreate(BaseModel):
   name: str = Field(min_length=1, max_length=100)
   category: str = Field(min_length=1, max_length=50)
   price: float = Field(gt=0)
   stock: int = Field(ge=0)

@app.post("/products", status_code=201)
def create_product(payload: ProductCreate):
   clean_name = payload.name.strip()
   clean_category = payload.category.strip().lower()
   if clean_name == "" or clean_category == "":
      raise HTTPException(status_code=400, detail="Name and category cannot be blank")
   for item in products:
      if item["name"].lower() == clean_name.lower():
         raise HTTPException(status_code=400, detail="Product with this name already exists")
   new_id = max([item["id"] for item in products], default=0) + 1
   new_product = {
      "id": new_id,
      "name": clean_name,
      "category": clean_category,
      "price": payload.price,
      "stock": payload.stock
   }
   products.append(new_product)
   return new_product