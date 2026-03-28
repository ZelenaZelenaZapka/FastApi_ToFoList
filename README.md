# FastAPI To-Do List

[![Tests](https://github.com/ZelenaZelenaZapka/FastApi_ToFoList/actions/workflows/test.yml/badge.svg)](https://github.com/ZelenaZelenaZapka/FastApi_ToFoList/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.104%2B-green)](https://fastapi.tiangolo.com/)

**Посилання на живий проект:** [https://todo-app-l42x.onrender.com/home](https://todo-app-l42x.onrender.com/home)

---

## Про проект

FastAPI To-Do List — це повнофункціональний веб-додаток для управління персональними завданнями. Проект демонструє розуміння сучасних практик веб-розробки: аутентифікація користувачів, робота з базами даних, тестування та автоматизована розгортка.

Кожен користувач отримує:
- Особистий список завдань з можливістю керування статусом
- Безпечну систему аутентифікації з хешуванням паролів
- Історію видалених завдань
- Ізольований простір від інших користувачів

---

## Функціонал

| Функція | Опис |
|---------|------|
| Реєстрація та вхід | Аутентифікація з хешуванням паролів через bcrypt |
| Керування завданнями | Створення, видалення, позначення як виконане |
| Історія завдань | Переглядання видалених завдань з можливістю їх відновлення |
| Персональні дані | Кожен користувач бачить тільки свої завдання |
| Форматування часу | Збереження в UTC, відображенн�� в локальному форматі |

---

## Архітектура проекту

```
.
└── SimpleTestSite
   ├── __pycache__
   │  └── main.cpython-312.pyc
   ├── app
   │  ├── __pycache__
   │  │  ├── database.cpython-312.pyc
   │  │  ├── dependencies.cpython-312.pyc
   │  │  ├── models.cpython-312.pyc
   │  │  ├── security.cpython-312.pyc
   │  │  └── utils.cpython-312.pyc
   │  ├── database.py
   │  ├── dependencies.py
   │  ├── models.py
   │  ├── routes
   │  │  ├── __init__.py
   │  │  ├── __pycache__
   │  │  ├── auth.py
   │  │  ├── pages.py
   │  │  └── tasks.py
   │  ├── security.py
   │  └── utils.py
   ├── env.example
   ├── main.py
   ├── myenv
   ├── README.md
   ├── requirements.txt
   ├── run_tests.sh
   ├── setup.sh
   ├── static
   │  ├── css
   │  │  ├── dashboard.css
   │  │  └── login.css
   │  ├── img
   │  └── js
   │     ├── dashboard.js
   │     └── login.js
   ├── template
   │  ├── dashboard.html
   │  └── login.html
   ├── test.db
   └── tests
      ├── __init__.py
      ├── __pycache__
      ├── conftest.py
      ├── test_auth.py
      ├── test_tasks.py
      └── test_utils.py
```


### Обґрунтування архітектури

- **Модульна структура**: відділення логіки на окремі файли забезпечує масштабованість та підтримку коду
- **FastAPI**: сучасний фреймворк з автоматичною валідацією та документацією
- **SQLAlchemy ORM**: захист від SQL-ін'єкцій та зручність роботи з базою
- **Маршрути в окремих файлах**: спрощує навігацію в проекті при його розростанні

---

## Стек технологій

**Backend:**
- FastAPI 0.104+
- SQLAlchemy 2.0+
- Passlib + bcrypt (криптографія)

**Фронтенд:**
- Jinja2 (серверне рендерування)
- HTML5 + CSS3 + Vanilla JavaScript

**Дані:**
- SQLite (розробка)
- PostgreSQL (продакшен)

**Тестування:**
- Pytest
- TestClient (FastAPI)

**Розгортка:**
- GitHub Actions (CI/CD)
- Render.com (hosting)

---

## Функції безпеки

- Паролі хешуються через bcrypt з автоматичним генеруванням salt
- HTTP-only cookies для захисту від XSS атак
- Валідація вхідних даних через Pydantic
- Захист від SQL-ін'єкцій через ORM
- Тести перевіряють ізоляцію користувачів (user isolation)

---

## Встановлення та запуск

### Вимоги

- Python 3.11 або новіше
- Git
- Virtualenv або venv

### Інструкції

**1. Клонування репозиторію**
```bash
git clone https://github.com/ZelenaZelenaZapka/FastApi_ToFoList.git
cd FastApi_ToFoList
```
**2. Створення віртуального середовища**
```bash

python -m venv myenv
source myenv/bin/activate  # Linux/Mac
myenv\Scripts\activate     # Windows
```
**3. Встановлення залежностей**
```bash

pip install -r requirements.txt
```
**4. Налаштування конфігурації**
```bash

cp env.example .env
```
**5. Запуск сервера**
```bash

uvicorn main:app --reload
```

Додаток буде доступний за адресою: http://127.0.0.1:8000

Тестування

Проект включає набір автоматичних тестів, які перевіряють:

- Функціональність реєстрації та входу
- Керування завданнями
- Контроль доступу (користувач не може видалити завдання іншого користувача)
- Валідацію даних
- Форматування часу

Запуск тестів локально:
```bash

pytest tests/ -v
```

Статус тестів: Тести запускаються автоматично при кожному push на GitHub (див. бейдж вище)
Розгортка на Render.com

- Підключіть GitHub репозиторій до сервісу Render
- Налаштуйте змінну середовища DATABASE_URL з PostgreSQL строкою підключення
- При кожному git push:
     GitHub Actions запускає тести
     При успіху код розгортається на Render
     Сайт автоматично оновлюється

## Структура даних

**Users**

| Поле | Тип | Опис |
|------|-----|------|
| id | Integer | Первинний ключ |
| email | String | Електронна пошта (унікальна) |
| hashed_password | String | Хешований пароль |
| created_at | DateTime | Час реєстрації |

**Tasks**

| Поле | Тип | Опис |
|------|-----|------|
| id | Integer | Первинний ключ |
| title | String | Назва завдання |
| completed | Boolean | Статус виконання |
| deleted | Boolean | Чи видалено завдання |
| deleted_at | DateTime | Час видалення |
| created_at | DateTime | Час створення |
| user_id | Integer | ID користувача (зовнішній ключ) |

## Розробник

👨‍💻 **Розробник:** [@ZelenaZelenaZapka](https://github.com/ZelenaZelenaZapka)

## Корисні посилання

- [FastAPI документація](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Render.com документація](https://render.com/docs)
