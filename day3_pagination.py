products = [
   {"id": 1, "name": "Keratin Shampoo", "category": "hair", "price": 25, "stock": 5},
   {"id": 2, "name": "Hydrating Mask", "category": "hair", "price": 40, "stock": 0},
   {"id": 3, "name": "Heat Protection Spray", "category": "hair", "price": 30, "stock": 3},
   {"id": 4, "name": "Vitamin C Face Cream", "category": "face", "price": 55, "stock": 2},
   {"id": 5, "name": "Hyaluronic Serum", "category": "face", "price": 70, "stock": 4},
]

def get_catalog_page(page, page_size):
   if page <= 0 or page_size <= 0:
      return {"page": page, "total_items": len(products), "items": []}
   start = (page - 1) * page_size
   end = start + page_size
   page_items = products[start:end]
   return {"page": page, "total_items": len(products), "items": page_items}

def sort_catalog(sort_field, is_desc):
   allowed_fields = ["price", "stock", "name", "id"]
   if sort_field not in allowed_fields:
      return []
   return sorted(products, key=lambda item: item[sort_field], reverse=is_desc)

print(get_catalog_page(2, 2))
print(sort_catalog("price", True))

# unexpected input data
print(get_catalog_page(0, 2))
print(get_catalog_page(1, -5))
print(sort_catalog("color", False))