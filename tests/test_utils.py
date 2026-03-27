"""
Тести утиліт (форматування часу, паролі)
"""
from datetime import datetime
from main import format_datetime, verify_password, get_password_hash

def test_time_formatting():
    """Тест: Форматування часу"""
    dt = datetime(2026, 3, 27, 9, 45, 32)
    formatted = format_datetime(dt)
    
    assert formatted == "27.03.2026 09:45"
    assert "32" not in formatted  # Без секунд

def test_time_formatting_none():
    """Тест: Форматування None"""
    formatted = format_datetime(None)
    assert formatted == "—"

def test_password_hash_and_verify():
    """Тест: Хешування й перевірка паролів"""
    password = "mysecurepassword123"
    
    # Хешуємо
    hashed = get_password_hash(password)
    
    # Хешований пароль не дорівнює оригіналу
    assert hashed != password
    
    # Але верифікація проходить
    assert verify_password(password, hashed) == True
    
    # Неправильний пароль не проходить
    assert verify_password("wrongpassword", hashed) == False

def test_password_hash_different_each_time():
    """Тест: Кожен раз інший хеш (через salt)"""
    password = "same_password"
    
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    
    # Хеши різні (через salt)
    assert hash1 != hash2
    
    # Але обидва верифікуються
    assert verify_password(password, hash1) == True
    assert verify_password(password, hash2) == True