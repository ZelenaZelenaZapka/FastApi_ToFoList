from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# 1. Підключаємо папку static як доступну за адресою /static
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Налаштовуємо шаблони
templates = Jinja2Templates(directory="template")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

