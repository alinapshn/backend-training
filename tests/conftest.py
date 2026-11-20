import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app

engine = create_engine(
   "sqlite:///:memory:", 
   connect_args={"check_same_thread": False},
   poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture()
def db():
   Base.metadata.create_all(bind=engine)
   session = TestingSessionLocal()
   try:
      yield session
   finally:
      session.close()
      Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def client(db):
   def override_get_db():
      yield db

   app.dependency_overrides[get_db] = override_get_db
   with TestClient(app) as test_client:
      yield test_client
   app.dependency_overrides.clear()
