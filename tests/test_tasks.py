"""
Тести завдань (додавання, видалення, позначення)
"""
from main import Task

def test_add_task(logged_in_client):
    """Тест: Додавання завдання"""
    response = logged_in_client.post(
        "/add-task", 
        data={"title": "Купити молоко"}, 
        follow_redirects=False  # ✅ Добавити
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/home"

def test_add_task_without_login(client):
    """Тест: Додавання завдання без логіну"""
    response = client.post(
        "/add-task", 
        data={"title": "Купити молоко"}, 
        follow_redirects=False  # ✅ Добавити
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/"

def test_toggle_task(logged_in_client, db_session):
    """Тест: Позначення завдання як виконане"""
    # Додаємо завдання
    logged_in_client.post(
        "/add-task", 
        data={"title": "Тест"}, 
        follow_redirects=False  # ✅ Добавити
    )
    
    # Отримуємо ID з БД
    task = db_session.query(Task).filter(Task.title == "Тест").first()
    assert task is not None
    
    # Позначаємо як виконане
    response = logged_in_client.post(
        f"/toggle-task/{task.id}", 
        follow_redirects=False  # ✅ Добавити
    )
    assert response.status_code == 303
    
    # Перевіряємо в БД
    db_session.refresh(task)
    assert task.completed == True

def test_delete_task(logged_in_client, db_session):
    """Тест: Видалення завдання"""
    # Додаємо завдання
    logged_in_client.post(
        "/add-task", 
        data={"title": "Видалити це"}, 
        follow_redirects=False  # ✅ Добавити
    )
    
    # Отримуємо ID
    task = db_session.query(Task).filter(Task.title == "Видалити це").first()
    task_id = task.id
    
    # Видаляємо
    response = logged_in_client.post(
        f"/delete-task/{task_id}", 
        follow_redirects=False  # ✅ Добавити
    )
    assert response.status_code == 303
    
    # Перевіряємо, що видалено
    db_session.refresh(task)
    assert task.deleted == True
    assert task.deleted_at is not None

def test_cannot_delete_other_user_task(client, registered_user, test_user2_data, db_session):
    """Тест: Користувач не може видалити чужу задачу"""
    # Користувач 1 логінеться й додає завдання
    client.post("/login", data=registered_user, follow_redirects=False)
    client.post("/add-task", data={"title": "Задача користувача 1"}, follow_redirects=False)
    
    task = db_session.query(Task).filter(Task.title == "Задача користувача 1").first()
    task_id = task.id
    
    # Виходимо
    client.get("/logout", follow_redirects=False)
    
    # Реєструємо користувача 2 і логінимось
    client.post("/register", data=test_user2_data, follow_redirects=False)
    client.post("/login", data=test_user2_data, follow_redirects=False)
    
    # Спробуємо видалити чужу задачу
    response = client.post(
        f"/delete-task/{task_id}", 
        follow_redirects=False  # ✅ Добавити
    )
    
    # Перевіряємо, що завдання НЕ видалено
    db_session.refresh(task)
    assert task.deleted == False

def test_home_shows_only_own_tasks(client, registered_user, test_user2_data, db_session):
    """Тест: Користувач бачить тільки свої завдання"""
    # Користувач 1 додає завдання
    client.post("/login", data=registered_user, follow_redirects=False)
    client.post("/add-task", data={"title": "Завдання 1"}, follow_redirects=False)
    client.get("/logout", follow_redirects=False)
    
    # Користувач 2 додає завдання
    client.post("/register", data=test_user2_data, follow_redirects=False)
    client.post("/login", data=test_user2_data, follow_redirects=False)
    client.post("/add-task", data={"title": "Завдання 2"}, follow_redirects=False)
    
    # Отримуємо сторінку (слідуємо редіректу)
    response = client.get("/home", follow_redirects=True)
    
    # Повинна бути тільки "Завдання 2"
    assert "Завдання 2" in response.text
    assert "Завдання 1" not in response.text