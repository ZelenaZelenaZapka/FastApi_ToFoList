import os
from datetime import datetime
from fastapi import FastAPI, Request, Form, Cookie, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from typing import Optional
from dotenv import load_dotenv

# ==================== 🗄️ БД ====================

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL не знайдено!")

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==================== 🏗️ МОДЕЛІ ====================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    completed = Column(Boolean, default=False)
    deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="tasks")

Base.metadata.create_all(bind=engine)

# ==================== 🚀 APP ====================

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="template")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==================== 🔐 ПАРОЛІ ====================

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(password):
    return pwd_context.hash(password)

# ==================== ⏰ ФОРМАТУВАННЯ ЧАСУ ====================

def format_datetime(dt: datetime) -> str:
    """Форматує час: '27.03.2026 09:45'"""
    if dt is None:
        return "—"
    return dt.strftime("%d.%m.%Y %H:%M")

# ==================== 🛠️ HELPERS ====================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_nickname(email: str) -> str:
    return email.split("@")[0] if "@" in email else email

def get_current_user(db, email: Optional[str]):
    if not email:
        return None
    return db.query(User).filter(User.email == email).first()

# ==================== 🌐 МАРШРУТИ ====================

@app.get("/")
async def login_page(request: Request, user: str = Cookie(None)):
    if user:
        return RedirectResponse(url="/home", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/home")
async def home_page(
    request: Request, 
    user: str = Cookie(None), 
    view: str = "active", 
    db: Session = Depends(get_db)
):
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    current_user = get_current_user(db, user)
    if not current_user:
        response = RedirectResponse(url="/", status_code=303)
        response.delete_cookie(key="user")
        return response
    
    if view == "history":
        tasks = db.query(Task).filter(
            Task.user_id == current_user.id,
            Task.deleted == True
        ).order_by(Task.deleted_at.desc()).all()
    else:
        tasks = db.query(Task).filter(
            Task.user_id == current_user.id,
            Task.deleted == False
        ).order_by(Task.completed.asc()).all()
    
    # ✅ Форматуємо дати
    for task in tasks:
        task.created_at_formatted = format_datetime(task.created_at)
        if task.deleted_at:
            task.deleted_at_formatted = format_datetime(task.deleted_at)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "tasks": tasks,
        "user_email": user,
        "user_nickname": get_nickname(user),
        "current_view": view
    })

@app.post("/register")
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    password2: str = Form(None),
    db: Session = Depends(get_db)
):
    if password != password2:
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": "Паролі не співпадають"
        })
    
    if len(password) < 6:
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": "Пароль має містити мінімум 6 символів"
        })
    
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": "Користувач з таким email вже існує"
        })
    
    new_user = User(
        email=email,
        hashed_password=get_password_hash(password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    response = RedirectResponse(url="/home", status_code=303)
    response.set_cookie(key="user", value=email, max_age=7*24*60*60, httponly=True, samesite="lax")
    return response

@app.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": "Невірний email або пароль"
        })
    
    response = RedirectResponse(url="/home", status_code=303)
    response.set_cookie(key="user", value=email, max_age=7*24*60*60, httponly=True, samesite="lax")
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="user")
    return response

@app.post("/add-task")
async def add_task(
    request: Request, 
    title: str = Form(...), 
    user: str = Cookie(None), 
    db: Session = Depends(get_db)
):
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    current_user = get_current_user(db, user)
    if not current_user:
        return RedirectResponse(url="/", status_code=303)
    
    new_task = Task(
        title=title,
        user_id=current_user.id,
        created_at=datetime.now()
    )
    db.add(new_task)
    db.commit()
    
    return RedirectResponse(url="/home", status_code=303)

@app.post("/toggle-task/{task_id}")
async def toggle_task(
    task_id: int, 
    request: Request, 
    user: str = Cookie(None), 
    db: Session = Depends(get_db)
):
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    current_user = get_current_user(db, user)
    if not current_user:
        return RedirectResponse(url="/", status_code=303)
        
    task = db.query(Task).filter(
        Task.id == task_id, 
        Task.user_id == current_user.id
    ).first()
    
    if task:
        task.completed = not task.completed
        db.commit()
        
    return RedirectResponse(url="/home", status_code=303)

@app.post("/delete-task/{task_id}")
async def delete_task(
    task_id: int, 
    request: Request, 
    user: str = Cookie(None), 
    db: Session = Depends(get_db)
):
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    current_user = get_current_user(db, user)
    if not current_user:
        return RedirectResponse(url="/", status_code=303)

    task = db.query(Task).filter(
        Task.id == task_id, 
        Task.user_id == current_user.id
    ).first()
    
    if task:
        task.deleted = True
        task.deleted_at = datetime.now()
        db.commit()
        
    return RedirectResponse(url="/home", status_code=303)