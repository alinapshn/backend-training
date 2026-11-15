products = [
    {"id": 1, "name": "Keratin Shampoo", "category": "hair", "price": 25, "stock": 5},
    {"id": 2, "name": "Hydrating Mask", "category": "hair", "price": 40, "stock": 0},
    {"id": 3, "name": "Heat Protection Spray", "category": "hair", "price": 30, "stock": 3},
    {"id": 4, "name": "Vitamin C Face Cream", "category": "face", "price": 55, "stock": 2},
    {"id": 5, "name": "Hyaluronic Serum", "category": "face", "price": 70, "stock": 4},
    {"id": 6, "name": "Gentle Cleansing Gel", "category": "face", "price": 35, "stock": 6},
]

def update_product(product_id, name=None, category=None, price=None, stock=None):
   for item in products:
      if item["id"] == product_id:
         if name is not None:
            clean_name = name.strip()
            if name == "":
               return None
            item["name"] = clean_name

         if category is not None:
            clean_category = category.strip().lower()
            if category == "":
               return None
            item["category"] = clean_category

         if price is not None:
            if price <= 0:
               return None
            item["price"] = price

         if stock is not None:
            if stock < 0:
               return None
            item["stock"] = stock

         return item
      
   return None

def delete_product(product_id):
   for item in products:
      if item["id"] == product_id:
         products.remove(item)
         return item
      
   return None

print(update_product(1, price=35))
print(update_product(3, price=-5))
print(delete_product(2))
print(delete_product(999))
print(products)