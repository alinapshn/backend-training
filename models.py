from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class ProductDB(Base):
   __tablename__ = "products"
   id = Column(Integer, primary_key=True, index=True)
   name = Column(String, unique=True, nullable=False)
   category = Column(String, nullable=False)
   price = Column(Float, nullable=False)
   stock = Column(Integer, nullable=False, default=0)

class OrderItemDB(Base):
   __tablename__ = "order_items"
   id = Column(Integer, primary_key=True, index=True)
   order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
   product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
   quantity = Column(Integer, nullable=False)
   price_at_purchase = Column(Float, nullable=False)

   product = relationship("ProductDB")

class OrderDB(Base):
   __tablename__ = "orders"
   id = Column(Integer, primary_key=True, index=True)
   total_price = Column(Float, nullable=False)

   items = relationship("OrderItemDB")