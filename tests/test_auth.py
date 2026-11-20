def test_register_and_login(client):
   reg_response = client.post(
      "/register",
      json={"email": "user@test.ch", "password": "secret123"}
   )
   assert reg_response.status_code == 201
   data = reg_response.json()
   assert data["email"] == "user@test.ch"
   assert data["role"] == "customer"
   assert "hashed_password" not in data

   login_response = client.post(
      "/login",
      json={"email": "user@test.ch", "password": "secret123"}
   )
   assert login_response.status_code == 200
   token = login_response.json()["access_token"]

   profile_response = client.get(
      "/profile",
      headers={"Authorization": f"Bearer {token}"}
   )
   assert profile_response.status_code == 200
   assert profile_response.json()["email"] == "user@test.ch"

def test_register_duplicate_email(client):
   payload = {"email": "dup@test.ch", "password": "secret123"}
   first = client.post("/register", json=payload)
   second = client.post("/register", json=payload)

   assert first.status_code == 201
   assert second.status_code == 400

def test_profile_without_token(client):
   profile_response = client.get("/profile")
   assert profile_response.status_code == 401
   