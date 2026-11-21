# EcoBazar API (Backend Training Project)

Backend REST API for an e-commerce platform built with FastAPI and SQLAlchemy as a structured backend engineering training project. Supports user authentication, role-based access control (Admin / Customer), product catalog management with search and pagination, order processing, database migrations, and automated testing.

## Tech Stack

- **Framework:** FastAPI
- **Database & ORM:** SQLite (transitioning to PostgreSQL), SQLAlchemy
- **Migrations:** Alembic
- **Auth & Security:** JWT (`PyJWT`), password hashing (`bcrypt`), Role-Based Access Control
- **Validation:** Pydantic v2
- **Testing:** Pytest, FastAPI `TestClient`

## Features

- User registration, login (Bearer JWT), and authenticated profile endpoint
- Role-based authorization (`admin` vs `customer`) protecting catalog mutations
- Product CRUD with case-insensitive search (`ILIKE`), category/price filtering, and offset/limit pagination
- Order creation with stock validation and automatic inventory updates
- Versioned database schema migrations via Alembic
- Isolated in-memory integration test suite (`pytest`)

## Project Structure

```text
.
├── alembic/            # Database migration scripts
├── routers/            # Domain route handlers (auth, products, orders)
├── tests/              # Pytest suite with in-memory SQLite fixtures
├── database.py         # Engine and session configuration
├── main.py             # FastAPI application entrypoint
├── models.py           # SQLAlchemy ORM models
├── schemas.py          # Pydantic request/response schemas
├── security.py         # JWT, bcrypt, and role dependencies
├── alembic.ini
├── requirements.txt
└── .env.example
```

## API Overview

| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/register` | Public | Register a new customer account |
| `POST` | `/login` | Public | Authenticate and receive a JWT access token |
| `GET` | `/profile` | Authenticated | Get current user profile |
| `GET` | `/products` | Public | List products (supports `search`, `category`, `min_price`, `max_price`, `limit`, `offset`) |
| `GET` | `/products/{id}` | Public | Get product details by ID |
| `POST` | `/products` | Admin | Create a new product |
| `PATCH` | `/products/{id}` | Admin | Update product fields |
| `DELETE` | `/products/{id}` | Admin | Delete a product |
| `POST` | `/orders` | Authenticated | Place an order and deduct product stock |
| `GET` | `/orders` | Authenticated | List orders of the current user |

## Local Setup

1. **Clone the repository and create a virtual environment:**

       git clone https://github.com/alinapshn/backend-training.git
       cd backend-training
       python3 -m venv venv
       source venv/bin/activate

2. **Install dependencies:**

       pip install -r requirements.txt

3. **Configure environment variables:**

       cp .env.example .env

   Generate a secure `SECRET_KEY` and paste it into `.env`:

       python3 -c "import secrets; print(secrets.token_hex(32))"

4. **Apply database migrations:**

       alembic upgrade head

5. **Run the development server:**

       uvicorn main:app --reload

   Interactive API docs (Swagger UI) will be available at `http://127.0.0.1:8000/docs`.

## Running Tests

    python -m pytest -v