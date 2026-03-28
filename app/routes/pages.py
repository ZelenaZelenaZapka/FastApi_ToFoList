from fastapi import APIRouter, Request, Cookie, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.utils import get_nickname, format_datetime
from app.models import Task

router = APIRouter()
templates = Jinja2Templates(directory="template")

@router.get("/")
async def login_page(request: Request, user: str = Cookie(None)):
    if user:
        return RedirectResponse(url="/home", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/home")
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
