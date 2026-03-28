from fastapi import APIRouter, Request, Form, Cookie, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime

from app.dependencies import get_db, get_current_user
from app.models import Task

router = APIRouter()

@router.post("/add-task")
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

@router.post("/toggle-task/{task_id}")
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

@router.post("/delete-task/{task_id}")
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