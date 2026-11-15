products = [
    {"id": 1, "name": "Keratin Shampoo", "category": "hair", "price": 25, "stock": 5},
    {"id": 2, "name": "Hydrating Mask", "category": "hair", "price": 40, "stock": 0},
    {"id": 3, "name": "Heat Protection Spray", "category": "hair", "price": 30, "stock": 3},
    {"id": 4, "name": "Vitamin C Face Cream", "category": "face", "price": 55, "stock": 2},
    {"id": 5, "name": "Hyaluronic Serum", "category": "face", "price": 70, "stock": 4},
]

def calculate_discount(raw_price, raw_discount):
   try:
      price = float(raw_price)
      discount = int(raw_discount)
   except (ValueError, TypeError):
      return {"status": "error", "message": "Invalid number format"}
   if price <= 0 or discount < 0 or discount > 90:
      return {"status": "error", "message": "Values out of range"}
   final_price = round(price * (1 - discount / 100), 2)
   return {"status": "ok", "final_price": final_price}

def process_dirty_cart(cart_items):
   skipped_errors = 0
   total_cost = 0
   for cart_item in cart_items:
      try:
         item_id = int(cart_item["id"])
         item_qty = int(cart_item["qty"])
      except (KeyError, ValueError, TypeError):
         skipped_errors += 1
         continue
      if item_qty <= 0:
         skipped_errors += 1
         continue
      for item in products:
         if item["id"] == item_id and item["stock"] >= item_qty:
            item["stock"] -= item_qty
            total_cost += item["price"] * item_qty
            break
   return {"total_cost": total_cost, "skipped_errors": skipped_errors}

# Тесты для Задачи 1 (calculate_discount)
print(calculate_discount("100.50", "15"))       # Ожидаем ok и 85.42
print(calculate_discount("free", 10))           # Ожидаем Invalid number format
print(calculate_discount(100, 95))              # Ожидаем Values out of range
print(calculate_discount(None, "10"))           # Ожидаем Invalid number format

# Тесты для Задачи 2 (process_dirty_cart)
dirty_cart = [
    {"id": 1, "qty": "2"},       # Валидный (строка преобразуется в число): Shampoo 25 * 2 = 50
    {"id": 3},                   # Ошибка: нет ключа qty
    {"id": 4, "qty": "two"},     # Ошибка: qty не число
    {"id": 5, "qty": -1},        # Ошибка: qty <= 0
    {"id": 5, "qty": 1},         # Валидный: Hyaluronic Serum 70 * 1 = 70
]

print(process_dirty_cart(dirty_cart))
# Ожидаем: total_cost = 120 (50 + 70), skipped_errors = 3