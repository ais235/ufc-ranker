#!/usr/bin/env python3
"""
Точка входа для Railway
"""

import uvicorn
import os
import sys

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Получаем порт из переменной окружения Railway
    port = int(os.environ.get("PORT", 8000))
    
    print(f"🚀 Запуск UFC Ranker на Railway...")
    print(f"🌐 API будет доступно на порту: {port}")
    print("-" * 50)
    
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
