import os
from datetime import UTC, datetime, timedelta
from typing import Annotated

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from database import SessionDep
from models import UserDB

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
   raise ValueError("SECRET_KEY is not set in .env file")

ALGORITHM = "HS256"

security = HTTPBearer()

def hash_password(password: str) -> str:
   pwd_bytes = password.encode("utf-8")
   salt = bcrypt.gensalt()
   hashed = bcrypt.hashpw(pwd_bytes, salt)
   return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
   return bcrypt.checkpw(
      plain_password.encode("utf-8"),
      hashed_password.encode("utf-8")
   )

def create_access_token(user_id: int) -> str:
   expire = datetime.now(UTC) + timedelta(minutes=60)
   payload = {"sub": str(user_id), "exp": expire}
   return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
      credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
      db: SessionDep,
) -> UserDB:
   token = credentials.credentials
   try: 
      payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
      user_id = int(payload["sub"])
   except (jwt.PyJWTError, KeyError, ValueError):
      raise HTTPException(status_code=401, detail="Invalid or expired token")
   user = db.query(UserDB).filter(UserDB.id == user_id).first()
   if not user:
      raise HTTPException(status_code=401, detail="User not found")
   return user

CurrentUserDep = Annotated[UserDB, Depends(get_current_user)]

def get_current_admin(current_user: CurrentUserDep) -> UserDB:
   if current_user.role != "admin":
      raise HTTPException(status_code=403, detail="Admin privileges required")
   return current_user

AdminUserDep = Annotated[UserDB, Depends(get_current_admin)]