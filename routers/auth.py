from fastapi import APIRouter, HTTPException

from database import SessionDep
from models import UserDB
from schemas import TokenOut, UserCreate, UserLogin, UserOut
from security import CurrentUserDep, create_access_token, hash_password, verify_password

router = APIRouter(tags=["Auth"])

@router.post("/register", status_code=201, response_model=UserOut)
def create_user(payload: UserCreate, db: SessionDep):
   clean_mail = payload.email.strip().lower()
   is_exist = db.query(UserDB).filter(UserDB.email == clean_mail).first()
   if is_exist:
      raise HTTPException(status_code=400, detail="Email already registered")
   new_user = UserDB(email=clean_mail, hashed_password=hash_password(payload.password))
   db.add(new_user)
   db.commit()
   db.refresh(new_user)
   return new_user

@router.post("/login", response_model=TokenOut)
def login_user(payload: UserLogin, db: SessionDep):
   clean_mail = payload.email.strip().lower()
   user = db.query(UserDB).filter(UserDB.email == clean_mail).first()
   if not user or not verify_password(payload.password, user.hashed_password):
      raise HTTPException(status_code=401, detail="Invalid email or password")
   token = create_access_token(user.id)
   return {"access_token": token, "token_type": "bearer"}

@router.get("/profile", response_model=UserOut)
def get_profile(user: CurrentUserDep):
   return user
