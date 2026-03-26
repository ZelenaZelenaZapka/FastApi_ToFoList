#!/bin/bash

echo "🚀 Початок налаштування проекту..."

# 1. Встановлення залежностей Python
echo "📦 Встановлення Python залежностей..."
pip install -r requirements.txt

# 2. Перевірка та встановлення PostgreSQL
echo "🗄️ Перевірка PostgreSQL..."
if ! command -v psql &> /dev/null; then
    echo "⚠️ PostgreSQL не встановлено. Встановлюємо..."
    sudo apt update
    sudo apt install postgresql postgresql-contrib -y
fi

sudo service postgresql start

# 3. Визначаємо середовище і створюємо .env
echo "⚙️ Налаштування змінних оточення..."

if [ -n "$CODESPACES" ]; then
    # Ми в GitHub Codespaces
    echo "🌐 Виявлено середовище Codespaces"
    DB_PASS="postgres"
    DB_HOST="localhost"
else
    # Локальний комп'ютер
    echo "💻 Виявлено локальне середовище"
    DB_PASS="12345"
    DB_HOST="localhost"
    
    # Створюємо користувача з паролем для локальної розробки
    sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '$DB_PASS';" 2>/dev/null
fi

# Створюємо базу
sudo -u postgres psql -c "CREATE DATABASE todo_db;" 2>/dev/null || echo "✅ База вже існує"

# Створюємо .env файл
cat > .env << EOF
DATABASE_URL=postgresql://postgres:$DB_PASS@$DB_HOST:5432/todo_db
EOF

echo "✅ Файл .env створено"

# 4. Дозвіл на sudo без пароля (для зручності)
echo "codespace" | sudo -S tee /etc/sudoers.d/nopasswd >/dev/null <<< "codespace ALL=(ALL) NOPASSWD:ALL" 2>/dev/null

echo "✅ Готово! Запускайте командою: fastapi dev main.py"