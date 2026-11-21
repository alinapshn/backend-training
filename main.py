from fastapi import FastAPI

from routers import auth, orders, products

app = FastAPI(
   title="EcoBazar API",
   description="Backend REST API for an e-commerce store with JWT auth, RBAC, and Alembic migrations.",
   version="1.0.0"
)

app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(products.router)