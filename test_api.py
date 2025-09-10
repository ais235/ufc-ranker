#!/usr/bin/env python3
"""
Тестовый скрипт для проверки API
"""

import requests
import json
import time

def test_api():
    """Тестирует API эндпоинты"""
    base_url = "http://localhost:8000"
    
    # Ждем запуска сервера
    print("⏳ Ожидание запуска сервера...")
    time.sleep(3)
    
    endpoints = [
        "/",
        "/api/stats",
        "/api/fighters?limit=5",
        "/api/weight-classes",
        "/api/events?limit=5",
        "/api/fights?limit=5"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\n🔍 Тестируем {endpoint}...")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint} - OK")
                if isinstance(data, dict):
                    print(f"   Ключи: {list(data.keys())}")
                elif isinstance(data, list):
                    print(f"   Количество записей: {len(data)}")
            else:
                print(f"❌ {endpoint} - {response.status_code}")
                print(f"   Ответ: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} - Ошибка: {e}")
        except Exception as e:
            print(f"❌ {endpoint} - Неожиданная ошибка: {e}")

if __name__ == "__main__":
    test_api()
