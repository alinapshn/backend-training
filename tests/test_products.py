from models import UserDB


def test_customer_cannot_create_product(client):
   client.post(
      "/register",
      json={"email": "user@test.ch", "password": "secret123"}
   )
   login_res = client.post(
      "/login",
      json={"email": "user@test.ch", "password": "secret123"}
   )
   token = login_res.json()["access_token"]

   response = client.post(
      "/products",
      json={"name": "shampoo", "category": "hair", "price": 30.0, "stock": 7},
      headers={"Authorization": f"Bearer {token}"}
   )

   assert response.status_code == 403

def test_admin_can_create_and_filter_products(client, db):
   client.post(
      "/register",
      json={"email": "admin@test.ch", "password": "secret123"}
   )
   user = db.query(UserDB).filter(UserDB.email == "admin@test.ch").first()
   user.role = "admin"
   db.commit()

   login_res = client.post(
      "/login",
      json={"email": "admin@test.ch", "password": "secret123"}
   )
   token = login_res.json()["access_token"]
   headers = {"Authorization": f"Bearer {token}"}

   response_create_first = client.post(
      "/products",
      json={"name": "shampoo", "category": "hair", "price": 30.0, "stock": 7},
      headers=headers
   )
   response_create_second = client.post(
      "/products",
      json={"name": "lotion", "category": "body", "price": 15.0, "stock": 4},
      headers=headers
   )
   assert response_create_first.status_code == 201
   assert response_create_second.status_code == 201

   response_filter = client.get(
      "/products?search=shampoo"
   )
   items = response_filter.json()

   assert response_filter.status_code == 200
   assert len(items) == 1
   assert items[0]["name"] == "shampoo"

