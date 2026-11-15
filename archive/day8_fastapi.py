from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/")
def root():
   return {"message": "Welcome to Ecobazar API", "docs": "/docs"}

products = [
    {"id": 1, "name": "Keratin Shampoo", "category": "hair", "price": 25, "stock": 5},
    {"id": 2, "name": "Hydrating Mask", "category": "hair", "price": 40, "stock": 0},
    {"id": 3, "name": "Heat Protection Spray", "category": "hair", "price": 30, "stock": 3},
    {"id": 4, "name": "Vitamin C Face Cream", "category": "face", "price": 55, "stock": 2},
    {"id": 5, "name": "Hyaluronic Serum", "category": "face", "price": 70, "stock": 4},
]

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