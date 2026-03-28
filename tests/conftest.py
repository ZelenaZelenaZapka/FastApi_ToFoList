"""
Конфіг для всіх тестів (фікстури, налаштування БД)
"""
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from dotenv import load_dotenv

load_dotenv()

# Імпортуємо з main.py
from main import app, get_db
from app.database import Base
from app.models import User, Task

# ==================== 🗄️ ТЕСТОВА БД ====================

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# ==================== 📝 КЛІЄНТ ====================

@pytest.fixture
def client():
    """Тестовий клієнт FastAPI"""
    return TestClient(app)

@pytest.fixture(autouse=True)
def clear_db():
    """Очищує БД перед кожним тестом"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# ==================== 👤 ФІКСТУРИ КОРИСТУВАЧІВ ====================

@pytest.fixture
def test_user_data():
    """Тестові дані користувача"""
    return {
        "email": "test@example.com",
        "password": "password123",
        "password2": "password123"
    }

@pytest.fixture
def test_user2_data():
    """Другий тестовий користувач"""
    return {
        "email": "user2@example.com",
        "password": "password123",
        "password2": "password123"
    }

@pytest.fixture
def registered_user(client, test_user_data):
    """Реєструє користувача й повертає дані"""
    client.post("/register", data=test_user_data)
    return test_user_data

@pytest.fixture
def logged_in_client(client, registered_user):
    """Повертає клієнт залогіненого користувача"""
    client.post("/login", data=registered_user)
    return client

# ==================== 🛠️ HELPERS ====================

@pytest.fixture
def db_session():
    """Сеанс БД для прямого доступу"""
    db = TestingSessionLocal()
    yield db
    db.close()