#!/usr/bin/env python3
"""
WSGI конфигурация для PythonAnywhere
"""
import sys
import os

# Добавляем путь к проекту
path = '/home/yourusername/ufc-ranker'  # Замените yourusername на ваш username
if path not in sys.path:
    sys.path.append(path)

# Импортируем FastAPI приложение
from backend.app import app

# WSGI приложение
application = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
