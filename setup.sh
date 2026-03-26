
---

### ⚡ Крок 4: Автоматизація (Скрипт `setup.sh`)

Щоб користувач не вводив команди вручну, створи скрипт автоматичного налаштування.
Створи файл `setup.sh` у корені проекту:

```bash
#!/bin/bash

echo "🚀 Початок налаштування проекту..."

# 1. Встановлення залежностей Python
echo "📦 Встановлення Python залежностей..."
pip install -r requirements.txt

# 2. Перевірка PostgreSQL
echo "🗄️ Перевірка PostgreSQL..."
if ! sudo service postgresql status > /dev/null; then
    echo "⚠️ PostgreSQL не встановлено. Встановлюємо..."
    sudo apt update
    sudo apt install postgresql postgresql-contrib -y
fi

sudo service postgresql start

# 3. Створення БД
echo "🏗️ Створення бази даних..."
sudo -u postgres psql -c "CREATE DATABASE todo_db;" 2>/dev/null || echo "✅ База вже існує"
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '12345';" 2>/dev/null

# 4. Створення .env
if [ ! -f .env ]; then
    echo "⚙️ Створення файлу .env..."
    cp .env.example .env
    echo "⚠️ ВІДРЕДАГУЙТЕ ФАЙЛ .env І ВПИШІТЬ Свій ПАРОЛЬ ВІД БАЗИ!"
else
    echo "✅ Файл .env вже існує"
fi

echo "✅ Готово! Запускайте командою: fastapi dev main.py"
