from fastapi import APIRouter, HTTPException

from database import SessionDep
from models import OrderDB, OrderItemDB
from routers.products import get_product_by_id
from schemas import OrderCreate, OrderOut
from security import CurrentUserDep

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post('', status_code=201, response_model=OrderOut)
def create_order(payload: OrderCreate, current_user: CurrentUserDep, db: SessionDep):
   total_price = 0
   order_items = []
   for item in payload.items:
      product = get_product_by_id(item.product_id, db)
      if product.stock < item.quantity:
         raise HTTPException(status_code=400, detail="Not enough products available")
      product.stock -= item.quantity
      total_price += item.quantity * product.price
      new_item = OrderItemDB(
         product_id=item.product_id,
         quantity=item.quantity,
         price_at_purchase=product.price
      )
      order_items.append(new_item)
   new_order = OrderDB(user_id=current_user.id, total_price=total_price, items=order_items)
   db.add(new_order)
   db.commit()
   db.refresh(new_order)
   return new_order

@router.get("", response_model=list[OrderOut])
def get_orders(current_user: CurrentUserDep, db: SessionDep):
   orders = db.query(OrderDB).filter(OrderDB.user_id == current_user.id).all()
   return orders 