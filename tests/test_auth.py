"""
Тести аутентифікації (логін, реєстрація, вихід)
"""

def test_login_page(client):
    """Тест: Сторінка логіну доступна"""
    response = client.get("/")
    assert response.status_code == 200

def test_register_valid_user(client, test_user_data):
    """Тест: Реєстрація з правильними даними"""
    response = client.post("/register", data=test_user_data, follow_redirects=False)
    assert response.status_code == 303  # ✅ Редірект, без слідування
    assert response.headers["location"] == "/home"

def test_register_password_mismatch(client):
    """Тест: Реєстрація з різними паролями"""
    response = client.post("/register", data={
        "email": "test@example.com",
        "password": "password123",
        "password2": "wrongpassword"
    }, follow_redirects=False)
    assert response.status_code == 200
    assert "Паролі не співпадають" in response.text

def test_register_short_password(client):
    """Тест: Реєстрація з коротким паролем"""
    response = client.post("/register", data={
        "email": "test@example.com",
        "password": "123",
        "password2": "123"
    }, follow_redirects=False)
    assert response.status_code == 200
    assert "мінімум 6 символів" in response.text

def test_register_duplicate_email(client, test_user_data):
    """Тест: Реєстрація з існуючим email"""
    client.post("/register", data=test_user_data, follow_redirects=False)
    
    response = client.post("/register", data=test_user_data, follow_redirects=False)
    assert response.status_code == 200
    assert "вже існує" in response.text

def test_login_valid(client, registered_user):
    """Тест: Логін з правильними даними"""
    response = client.post("/login", data=registered_user, follow_redirects=False)
    assert response.status_code == 303  # ✅ Редірект
    assert response.headers["location"] == "/home"

def test_login_invalid_email(client):
    """Тест: Логін з неправильним email"""
    response = client.post("/login", data={
        "email": "nonexistent@example.com",
        "password": "password123"
    }, follow_redirects=False)
    assert response.status_code == 200
    assert "Невірний email або пароль" in response.text

def test_login_invalid_password(client, registered_user):
    """Тест: Логін з неправильним паролем"""
    response = client.post("/login", data={
        "email": registered_user["email"],
        "password": "wrongpassword"
    }, follow_redirects=False)
    assert response.status_code == 200
    assert "Невірний email або пароль" in response.text

def test_logout(client, logged_in_client):
    """Тест: Вихід з акаунту"""
    response = logged_in_client.get("/logout", follow_redirects=False)
    assert response.status_code == 303  # ✅ Редірект
    assert response.headers["location"] == "/"