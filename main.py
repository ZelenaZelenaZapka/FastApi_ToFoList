from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="template")

# 🗃️ Простий список для задач (в пам'яті)
tasks = []

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/home", response_class=Jinja2Templates)
async def home_page(request: Request):
    # Передаємо список задач у шаблон
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "tasks": tasks
    })

@app.post("/add-task")
async def add_task(
    request: Request, 
    title: str = Form(...)
):
    tasks.append({
        "id": len(tasks) + 1,
        "title": title,
        "created_at": datetime.now().strftime("%H:%M"),
        "completed": False  # ← ДОДАЙ ЦЕЙ РЯДОК!
    })
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/home", status_code=303)

# Додай це в main.py, якщо ще немає

@app.post("/toggle-task/{task_id}")
async def toggle_task(task_id: int, request: Request):
    """Позначити задачу як виконану/активну"""
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = not task["completed"]
            break
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/home", status_code=303)

@app.post("/delete-task/{task_id}")
async def delete_task(task_id: int, request: Request):
    """Видалити задачу"""
    global tasks
    tasks = [t for t in tasks if t["id"] != task_id]
    # Перенумеруємо ID
    for i, task in enumerate(tasks, 1):
        task["id"] = i
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/home", status_code=303)
