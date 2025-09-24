#!/usr/bin/env python3
"""
Скрипт для поиска всех таблиц с событиями UFC на Wikipedia
"""

import requests
from bs4 import BeautifulSoup
import re

def find_all_tables():
    """Находит все таблицы с событиями UFC"""
    
    print("🔍 ПОИСК ВСЕХ ТАБЛИЦ С СОБЫТИЯМИ UFC")
    print("=" * 50)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get("https://en.wikipedia.org/wiki/List_of_UFC_events", headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Ищем все заголовки h2 и h3
        print("🔍 Все заголовки на странице:")
        for header in soup.find_all(['h2', 'h3']):
            if header.get('id'):
                print(f"  {header.name}: {header.get('id')} - {header.get_text(strip=True)}")
        
        # Ищем все таблицы
        print(f"\n🔍 Все таблицы на странице:")
        tables = soup.find_all('table')
        print(f"📊 Найдено {len(tables)} таблиц")
        
        for i, table in enumerate(tables):
            rows = table.find_all('tr')
            print(f"\n📋 Таблица {i+1}: {len(rows)} строк")
            
            # Проверяем первые несколько строк на наличие UFC событий
            ufc_found = False
            for j, row in enumerate(rows[:10]):  # Проверяем первые 10 строк
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    text = cells[0].get_text(strip=True)
                    if 'UFC' in text:
                        print(f"    Строка {j+1}: {text}")
                        if re.search(r'UFC\s+[1-9]', text):
                            print(f"      ⭐ НАЙДЕНО ИСТОРИЧЕСКОЕ СОБЫТИЕ!")
                            ufc_found = True
            
            if ufc_found:
                print(f"    ✅ Таблица {i+1} содержит исторические UFC события!")
        
        # Ищем конкретно UFC 1-10
        print(f"\n🔍 Поиск UFC 1-10 во всех таблицах:")
        for i, table in enumerate(tables):
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    text = cells[0].get_text(strip=True)
                    if re.search(r'UFC\s+[1-9]', text):
                        print(f"  Таблица {i+1}: {text}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    find_all_tables()
