products = [
   {"id": 1, "name": "Keratin Shampoo", "category": "hair", "price": 25, "stock": 5},
   {"id": 2, "name": "Hydrating Mask", "category": "hair", "price": 40, "stock": 0},
   {"id": 3, "name": "Heat Protection Spray", "category": "hair", "price": 30, "stock": 3},
   {"id": 4, "name": "Vitamin C Face Cream", "category": "face", "price": 55, "stock": 2},
   {"id": 5, "name": "Hyaluronic Serum", "category": "face", "price": 70, "stock": 4},
   {"id": 6, "name": "Gentle Cleansing Gel", "category": "face", "price": 35, "stock": 6},
]

def get_catalog(category=None, search_query=None, max_price=None, sort_field="id", is_desc=False, page=1, page_size=2):
   if page <= 0 or page_size <= 0:
      return {"page": page, "total_matched": 0, "items": []}
   if max_price is not None and max_price <= 0:
      return {"page": page, "total_matched": 0, "items": []}
   allowed_fields = ["price", "stock", "name", "id"]
   if sort_field not in allowed_fields:
      sort_field = "id"  
   filtered = []
   if search_query is not None:
      search_query = search_query.strip().lower()
   for item in products:
      if item["stock"] <= 0:
         continue 
      if category is not None and category != item["category"]:
         continue
      if max_price is not None and max_price < item["price"]:
         continue
      if search_query is not None and search_query not in item["name"].lower():
         continue
      filtered.append(item)

   total_matched = len(filtered)
   sorted_items = sorted(filtered, key=lambda item: item[sort_field], reverse=is_desc)
   
   start = (page - 1) * page_size
   end = start + page_size
   page_items = sorted_items[start:end]

   return {"page": page, "total_matched": total_matched, "items": page_items}

print(get_catalog(category="face", max_price=60, sort_field="price", is_desc=True))
print(get_catalog())

# unexpected input data
print(get_catalog(page=0))
print(get_catalog(max_price=-20))
print(get_catalog(sort_field="hacked_field", page_size=3))