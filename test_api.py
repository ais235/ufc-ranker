#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_api():
    try:
        print("=== ТЕСТИРОВАНИЕ API ===")
        
        # Тест весовых категорий
        print("\n1. Тест весовых категорий:")
        response = requests.get('http://localhost:8000/api/weight-classes')
        if response.status_code == 200:
            data = response.json()
            print(f"OK Весовые категории загружены: {len(data)} категорий")
            for wc in data[:3]:  # Показываем первые 3
                print(f"   - {wc['name_ru']} ({wc['name_en']})")
        else:
            print(f"ОШИБКА Ошибка: {response.status_code}")
        
        # Тест рейтингов
        print("\n2. Тест рейтингов:")
        response = requests.get('http://localhost:8000/api/rankings')
        if response.status_code == 200:
            data = response.json()
            print(f"OK Рейтинги загружены: {len(data)} записей")
            for ranking in data[:3]:  # Показываем первые 3
                print(f"   - {ranking['fighter']['name_ru']} в {ranking['weight_class']}")
        else:
            print(f"ОШИБКА Ошибка: {response.status_code}")
        
        # Тест конкретной весовой категории
        print("\n3. Тест Heavyweight:")
        response = requests.get('http://localhost:8000/api/rankings')
        if response.status_code == 200:
            data = response.json()
            heavyweight_rankings = [r for r in data if r['weight_class'] == 'Heavyweight']
            print(f"OK Heavyweight рейтинги: {len(heavyweight_rankings)} бойцов")
            for ranking in heavyweight_rankings[:3]:
                print(f"   - {ranking['fighter']['name_ru']} (позиция: {ranking['rank_position']})")
        else:
            print(f"ОШИБКА Ошибка: {response.status_code}")
            
    except Exception as e:
        print(f"ОШИБКА Ошибка подключения: {e}")

if __name__ == '__main__':
    test_api()
