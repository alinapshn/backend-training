products = [
   {"id": 1, "name": "shampoo", "category": "hair", "price": 25, "in_stock": True},
   {"id": 2, "name": "mask", "category": "hair", "price": 40, "in_stock": False},
   {"id": 3, "name": "heat protection", "category": "hair", "price": 30, "in_stock": True},
   {"id": 4, "name": "face cream", "category": "face", "price": 55, "in_stock": True},
   {"id": 5, "name": "serum", "category": "face", "price": 70, "in_stock": True}
]

def filter_catalog(category_name, max_price):
   if max_price <= 0:
      return []
   result = []
   for item in products:
      if category_name == item["category"] and max_price >= item["price"] and item["in_stock"]:
         result.append(item)
   return result

def calculate_cart(cart_ids):
   total = 0
   for item in products:
      if item["id"] in cart_ids and item["in_stock"]:
         total += item["price"]
   if total > 100:
      total *= 0.9
   return total

print(filter_catalog("hair", 35))
print(calculate_cart([1, 3, 5]))

# unexpected input data
print(calculate_cart([1, 2, 999]))
print(filter_catalog("hair", -10))