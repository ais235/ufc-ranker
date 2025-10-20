#!/usr/bin/env python3
"""
Скрипт для запуска FastAPI в продакшене
"""

import uvicorn
import os
import sys

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Получаем порт из переменной окружения (для Heroku и других платформ)
    port = int(os.environ.get("PORT", 8000))
    
    print(f"🚀 Запуск UFC Ranker в продакшене...")
    print(f"🌐 API будет доступно по адресу: http://0.0.0.0:{port}")
    print(f"📚 Документация API: http://0.0.0.0:{port}/docs")
    print("-" * 50)
    
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=port,
        workers=1,  # Для начала один воркер
        log_level="info",
        access_log=True
    )
