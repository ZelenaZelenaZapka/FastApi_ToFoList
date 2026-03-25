from fastapi import FastAPI, Request, Form, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from datetime import datetime
from passlib.context import CryptContext
import json
import os

app = FastAPI()

# 📁 Статика та шаблони
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="template")

# 🔐 Хешування
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 📁 Абсолютні шляхи до файлів (щоб точно знайти)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_FILE = os.path.join(BASE_DIR, "tasks.json")
USERS_FILE = os.path.join(BASE_DIR, "users.json")

print(f"📁 BASE_DIR: {BASE_DIR}")
print(f"📁 TASKS_FILE: {TASKS_FILE}")
print(f"📁 USERS_FILE: {USERS_FILE}")

# 🔐 Функції паролів
def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(password):
    return pwd_context.hash(password)

# 👥 Користувачі
def load_users():
    if not os.path.exists(USERS_FILE):
        print("📭 users.json не знайдено, створюємо пустий список")
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"✅ Завантажено користувачів: {list(data.keys())}")
            return data
    except Exception as e:
        print(f"❌ Помилка завантаження users.json: {e}")
        return {}

def save_users(users_dict):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users_dict, f, indent=2, ensure_ascii=False)
        print(f"💾 Збережено користувачів: {list(users_dict.keys())}")
        return True
    except Exception as e:
        print(f"❌ Помилка збереження users.json: {e}")
        return False

# 📋 Задачі
def load_tasks(user_email=None):
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            all_tasks = json.load(f)
        if user_email:
            filtered = [t for t in all_tasks if t.get("user") == user_email]
            print(f"🔍 Задачі для {user_email}: {len(filtered)} шт.")
            return filtered
        return all_tasks
    except Exception as e:
        print(f"❌ Помилка завантаження tasks.json: {e}")
        return []

def save_tasks(tasks_list):
    try:
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks_list, f, indent=2, ensure_ascii=False)
        print(f"💾 Збережено задач: {len(tasks_list)} шт.")
        return True
    except Exception as e:
        print(f"❌ Помилка збереження tasks.json: {e}")
        return False

# 🌍 Глобальні дані
users = load_users()
print(f"🚀 Сервер запущено. Користувачів у пам'яті: {len(users)}")

# ==================== 🌐 МАРШРУТИ ====================

@app.get("/")
async def login_page(request: Request, user: str = Cookie(None)):
    print(f"🔍 GET / — user cookie: {user}")
    if user:
        return RedirectResponse(url="/home", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/home")
async def home_page(request: Request, user: str = Cookie(None), view: str = "active"):
    """Показує задачі: active = всі не видалені, history = тільки видалені"""
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    all_tasks = load_tasks()
    
    if view == "history":
        # Історія = тільки видалені задачі цього користувача
        user_tasks = [t for t in all_tasks if t.get("user") == user and t.get("deleted") == True]
        # Сортуємо по даті видалення (новіші зверху)
        user_tasks.sort(key=lambda x: x.get("deleted_at", ""), reverse=True)
    else:
        # Активні = всі НЕ видалені (і завершені, і ні — показуємо разом)
        user_tasks = [t for t in all_tasks if t.get("user") == user and t.get("deleted") != True]
        # Сортуємо: спочатку незавершені, потім завершені
        user_tasks.sort(key=lambda x: x.get("completed", False))
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "tasks": user_tasks,
        "user_email": user,
        "user_nickname": get_nickname(user),
        "current_view": view
    })

@app.get("/logout")
async def logout():
    print("🚪 Вихід користувача")
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="user")
    return response

@app.post("/register")
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    password2: str = Form(None)
):
    print(f"📝 POST /register — email: {email}, passwords match: {password == password2}")
    
    if password != password2:
        print("❌ Паролі не співпадають")
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Паролі не співпадають"
        })
    
    if len(password) < 6:
        print("❌ Пароль занадто короткий")
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Пароль має містити мінімум 6 символів"
        })
    
    if email in users:
        print(f"❌ Користувач {email} вже існує")
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Користувач з таким email вже існує"
        })
    
    # Створюємо користувача
    users[email] = {
        "password": get_password_hash(password),
        "created_at": datetime.now().strftime("%Y-%m-%d")
    }
    print(f"✅ Створено користувача в пам'яті: {email}")
    
    # Зберігаємо на диск
    if not save_users(users):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Помилка збереження"
        })
    
    # ✅ Редірект з кукі
    print(f"🎯 Реєстрація успішна, ставимо кукі user={email}")
    response = RedirectResponse(url="/home", status_code=303)
    response.set_cookie(
        key="user", 
        value=email, 
        max_age=7*24*60*60, 
        httponly=True,
        samesite="lax"
    )
    return response

@app.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    print(f"🔑 POST /login — email: {email}")
    
    user_data = users.get(email)
    print(f"🔍 Знайдено користувача в пам'яті: {user_data is not None}")
    
    if not user_data:
        print(f"❌ Користувач {email} не знайдено в users dict")
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Невірний email або пароль"
        })
    
    if not verify_password(password, user_data["password"]):
        print("❌ Невірний пароль")
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Невірний email або пароль"
        })
    
    print(f"✅ Вхід успішний для {email}")
    response = RedirectResponse(url="/home", status_code=303)
    response.set_cookie(
        key="user", 
        value=email, 
        max_age=7*24*60*60, 
        httponly=True,
        samesite="lax"
    )
    return response

@app.get("/logout")
async def logout():
    print("🚪 Вихід користувача")
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="user")
    return response

@app.post("/add-task")
async def add_task(request: Request, title: str = Form(...), user: str = Cookie(None)):
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    all_tasks = load_tasks()
    new_id = len(all_tasks) + 1
    
    all_tasks.append({
        "id": new_id,
        "title": title,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "completed": False,
        "deleted": False,  # ← нове поле
        "user": user
    })
    save_tasks(all_tasks)
    return RedirectResponse(url="/home", status_code=303)

@app.post("/toggle-task/{task_id}")
async def toggle_task(task_id: int, request: Request, user: str = Cookie(None)):
    """Просто позначити/зняти галочку — задача НЕ переміщується"""
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    all_tasks = load_tasks()
    for task in all_tasks:
        if task["id"] == task_id and task.get("user") == user:
            task["completed"] = not task["completed"]  # просто перемикаємо
            break
    save_tasks(all_tasks)
    return RedirectResponse(url="/home", status_code=303)  # залишаємось на активних

@app.post("/delete-task/{task_id}")
async def delete_task(task_id: int, request: Request, user: str = Cookie(None)):
    """Видалити = позначити deleted=True → задача з'явиться в Історії"""
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    all_tasks = load_tasks()
    for task in all_tasks:
        if task["id"] == task_id and task.get("user") == user:
            task["deleted"] = True
            task["deleted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            break
    save_tasks(all_tasks)
    return RedirectResponse(url="/home", status_code=303)

    # 📧 Отримати нікнейм з email (частина до @)
def get_nickname(email: str) -> str:
    return email.split("@")[0] if "@" in email else email
