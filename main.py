from fastapi import FastAPI

from routers import auth, orders, products

app = FastAPI()

app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(products.router)