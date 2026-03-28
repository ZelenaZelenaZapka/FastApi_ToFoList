from fastapi import APIRouter, Request, Form, Cookie, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.security import verify_password, get_password_hash
from app.models import User

router = APIRouter()
templates = Jinja2Templates(directory="template")

@router.post("/register")
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

@router.post("/login")
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

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="user")
    return response