products = [
    {"id": 1, "name": "Keratin Shampoo", "category": "hair", "price": 25, "stock": 5},
    {"id": 2, "name": "Hydrating Mask", "category": "hair", "price": 40, "stock": 0},
    {"id": 3, "name": "Heat Protection Spray", "category": "hair", "price": 30, "stock": 3},
    {"id": 4, "name": "Vitamin C Face Cream", "category": "face", "price": 55, "stock": 2},
    {"id": 5, "name": "Hyaluronic Serum", "category": "face", "price": 70, "stock": 4},
    {"id": 6, "name": "Gentle Cleansing Gel", "category": "face", "price": 35, "stock": 6},
]

def create_product(name, category, price, stock):
   clean_name = name.strip()
   clean_category = category.strip().lower()
   if clean_name == "" or clean_category == "" or price <= 0 or stock < 0:
      return None
   for item in products:
      if clean_name == item["name"].lower():
         return None
   if len(products) > 0:
      new_id = max(item["id"] for item in products) + 1
   else:
      new_id = 1
   new_product = {"id": new_id, "name": clean_name, "category": clean_category, "price": price, "stock": stock}
   products.append(new_product)
   return new_product

def get_category_stats():
   stats = {}
   for item in products:
      category = item["category"]
      quantity = item["stock"]
      if category in stats:
         stats[category] += quantity
      else:
         stats[category] = quantity
   return stats

print(create_product("  Argan Oil  ", "HAIR", 45, 10))
print(get_category_stats())

# unexpected input data
print(create_product("   ", "face", 30, 5))
print(create_product("New Cream", "face", -10, 5))
print(create_product("  keratin shampoo ", "hair", 25, 3))
print(len(products))