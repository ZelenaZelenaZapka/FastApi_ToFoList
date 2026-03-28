from typing import Optional
from app.database import SessionLocal
from app.models import User

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(db, email: Optional[str]):
    if not email:
        return None
    return db.query(User).filter(User.email == email).first()

