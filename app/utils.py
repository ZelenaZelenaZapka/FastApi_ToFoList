from datetime import datetime

def format_datetime(dt: datetime) -> str:
    """Форматує час: '27.03.2026 09:45'"""
    if dt is None:
        return "—"
    return dt.strftime("%d.%m.%Y %H:%M")

def get_nickname(email: str) -> str:
    return email.split("@")[0] if "@" in email else email


