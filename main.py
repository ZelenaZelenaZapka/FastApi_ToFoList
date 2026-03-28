from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from app.utils import format_datetime, get_nickname
from app.security import verify_password, get_password_hash
from app.database import SessionLocal
from app.models import User, Task
from app.dependencies import get_db, get_current_user
from app.routes.auth import router as auth_router
from app.routes.pages import router as pages_router
from app.routes.tasks import router as tasks_router

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="template")

# Реєстрація маршрутів
app.include_router(pages_router)
app.include_router(auth_router)
app.include_router(tasks_router)


