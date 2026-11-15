products = [
   {"id": 1, "name": "Keratin Shampoo", "category": "hair", "price": 25, "stock": 5},
   {"id": 2, "name": "Hydrating Mask", "category": "hair", "price": 40, "stock": 0},
   {"id": 3, "name": "Heat Protection Spray", "category": "hair", "price": 30, "stock": 3},
   {"id": 4, "name": "Vitamin C Face Cream", "category": "face", "price": 55, "stock": 2},
   {"id": 5, "name": "Hyaluronic Serum", "category": "face", "price": 70, "stock": 4},
]

def search_products(query):
   clean_query = query.strip().lower()
   if clean_query == "":
      return []
   result = []
   for item in products:
      if clean_query in item["name"].lower() and item["stock"] > 0:
         result.append(item)
   return result

def process_order(cart_items):
   total = 0
   failed_ids = []
   for cart_item in cart_items:
      if cart_item["qty"] <= 0:
         failed_ids.append(cart_item["id"])
         continue

      found = False 
      for item in products:
         if cart_item["id"] == item["id"]  :
            found = True
            if item["stock"] >= cart_item["qty"]:
               item["stock"] -= cart_item["qty"]
               total += item["price"] * cart_item["qty"]
            else:
               failed_ids.append(cart_item["id"])
            break
      if not found:
         failed_ids.append(cart_item["id"])
   return {"total": total, "failed_ids": failed_ids}

print(search_products("  SPRAY "))

order = [{"id": 1, "qty": 2}, {"id": 4, "qty": 3}, {"id": 5, "qty": 1}]
print(process_order(order))
print(products)

# unexpected input data
bad_order = [{"id": 1, "qty": -5}, {"id": 999, "qty": 1}, {"id": 3, "qty": 2}]
print(process_order(bad_order))
print(products)