#!/usr/bin/env python3
"""
Скрипт для запуска FastAPI бэкенда
"""

import uvicorn
import sys
import os

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Запуск FastAPI бэкенда...")
    print("📡 API будет доступно по адресу: http://localhost:8000")
    print("📚 Документация API: http://localhost:8000/docs")
    print("🔄 Для остановки нажмите Ctrl+C")
    print("-" * 50)
    
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )













