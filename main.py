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

class ProductUpdate(BaseModel):
   name: str | None = Field(default=None, min_length=1, max_length=100)
   category: str | None = Field(default=None, min_length=1, max_length=50)
   price: float | None = Field(default=None, gt=0)
   stock: int | None = Field(default=None, ge=0)

@app.get("/products")
def get_products(category: str = None, max_price: float = None):  # noqa: RUF013
   if max_price is not None and max_price <= 0:
      raise HTTPException(status_code=400, detail="Max price must be greater than 0")
   if category is not None:
      category = category.strip().lower()
   found_products = []
   for item in products:
      if category is not None and item["category"] != category:
         continue
      if max_price is not None and item["price"] > max_price:
         continue
      if item["stock"] > 0:
         found_products.append(item)
   return {"count": len(found_products), "items": found_products}

@app.get("/products/{product_id}")
def get_product_by_id(product_id: int):
   for item in products:
      if item["id"] == product_id:
         return item
   raise HTTPException(status_code=404, detail="Product not found")

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

@app.patch("/products/{product_id}")
def update_product(product_id: int, payload: ProductUpdate):
   for item in products:
      if item["id"] == product_id:
         if payload.name is not None:
            clean_name = payload.name.strip()
            if clean_name == "":
               raise HTTPException(status_code=400, detail="Name cannot be blank")
            item["name"] = clean_name

         if payload.category is not None:
            clean_category = payload.category.strip().lower()
            if clean_category == "":
               raise HTTPException(status_code=400, detail="Category cannot be blank")
            item["category"] = clean_category

         if payload.price is not None:
            item["price"] = payload.price

         if payload.stock is not None:
            item["stock"] = payload.stock
         return item
      
   raise HTTPException(status_code=404, detail="Not Found")

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
   for item in products:
      if item["id"] == product_id:
         products.remove(item)
         return {"message": "Product deleted successfully", "id": product_id}
   raise HTTPException(status_code=404, detail="Not found")