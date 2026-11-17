from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
   name: str = Field(min_length=1, max_length=100)
   category: str = Field(min_length=1, max_length=50)
   price: float = Field(gt=0)
   stock: int = Field(ge=0)

class ProductUpdate(BaseModel):
   name: str | None = Field(default=None, min_length=1, max_length=100)
   category: str | None = Field(default=None, min_length=1, max_length=50)
   price: float | None = Field(default=None, gt=0)
   stock: int | None = Field(default=None, ge=0)

class ProductOut(BaseModel):
   id: int
   name: str
   category: str
   price: float
   model_config = ConfigDict(from_attributes=True)

class OrderItemCreate(BaseModel):
   product_id: int
   quantity: int = Field(gt=0)

class OrderCreate(BaseModel):
   items: list[OrderItemCreate] = Field(min_length=1)

class OrderItemOut(BaseModel):
   id: int
   quantity: int = Field(gt=0)
   price_at_purchase: float
   product: ProductOut
   model_config = ConfigDict(from_attributes=True)

class OrderOut(BaseModel):
   id: int
   user_id: int
   total_price: float
   items: list[OrderItemOut]
   model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
   email: str = Field(min_length=5, max_length=100)
   password: str = Field(min_length=6, max_length=100)

class UserOut(BaseModel):
   id: int
   email: str
   model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
   email: str
   password: str

class TokenOut(BaseModel):
   access_token: str
   token_type: str = "bearer"