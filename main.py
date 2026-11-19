from fastapi import FastAPI

from database import Base, engine
from routers import auth, orders, products

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(products.router)