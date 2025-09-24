#!/usr/bin/env python3
"""
Отладочный скрипт для анализа структуры страницы Wikipedia
"""

import requests
from bs4 import BeautifulSoup

def debug_page_structure():
    """Анализирует структуру страницы Wikipedia"""
    
    print("🔍 АНАЛИЗ СТРУКТУРЫ СТРАНИЦЫ WIKIPEDIA")
    print("=" * 50)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get("https://en.wikipedia.org/wiki/List_of_UFC_events", headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Ищем заголовки h2
        print("🔍 Все заголовки h2:")
        h2_headers = soup.find_all('h2')
        for i, header in enumerate(h2_headers):
            header_id = header.get('id', 'no-id')
            header_text = header.get_text(strip=True)
            print(f"  {i+1}. ID: {header_id} | Текст: {header_text}")
            
            # Ищем следующую таблицу после этого заголовка
            next_table = header.find_next('table')
            if next_table:
                rows = next_table.find_all('tr')
                print(f"     📊 Следующая таблица: {len(rows)} строк")
                
                # Показываем первые 3 строки
                for j, row in enumerate(rows[:3]):
                    cells = row.find_all(['td', 'th'])
                    cell_texts = [cell.get_text(strip=True) for cell in cells]
                    print(f"       Строка {j+1}: {cell_texts}")
            else:
                print(f"     ❌ Таблица не найдена")
        
        # Ищем все таблицы на странице
        print(f"\n🔍 Все таблицы на странице:")
        tables = soup.find_all('table')
        print(f"📊 Найдено {len(tables)} таблиц")
        
        for i, table in enumerate(tables):
            rows = table.find_all('tr')
            print(f"\n📋 Таблица {i+1}: {len(rows)} строк")
            
            # Показываем первые 3 строки
            for j, row in enumerate(rows[:3]):
                cells = row.find_all(['td', 'th'])
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                print(f"  Строка {j+1}: {cell_texts}")
        
        # Специально ищем Past events и Scheduled events
        print(f"\n🔍 Специальный поиск секций:")
        
        # Past events
        past_header = soup.find('h2', {'id': 'Past_events'})
        if past_header:
            print("✅ Заголовок Past events найден")
            print(f"   Текст: {past_header.get_text(strip=True)}")
            
            # Ищем следующую таблицу
            next_table = past_header.find_next('table')
            if next_table:
                rows = next_table.find_all('tr')
                print(f"   📊 Следующая таблица: {len(rows)} строк")
                
                # Показываем первые 5 строк
                for j, row in enumerate(rows[:5]):
                    cells = row.find_all(['td', 'th'])
                    cell_texts = [cell.get_text(strip=True) for cell in cells]
                    print(f"     Строка {j+1}: {cell_texts}")
            else:
                print("   ❌ Таблица не найдена")
        else:
            print("❌ Заголовок Past events не найден")
        
        # Scheduled events
        scheduled_header = soup.find('h2', {'id': 'Scheduled_events'})
        if scheduled_header:
            print("✅ Заголовок Scheduled events найден")
            print(f"   Текст: {scheduled_header.get_text(strip=True)}")
            
            # Ищем следующую таблицу
            next_table = scheduled_header.find_next('table')
            if next_table:
                rows = next_table.find_all('tr')
                print(f"   📊 Следующая таблица: {len(rows)} строк")
                
                # Показываем первые 5 строк
                for j, row in enumerate(rows[:5]):
                    cells = row.find_all(['td', 'th'])
                    cell_texts = [cell.get_text(strip=True) for cell in cells]
                    print(f"     Строка {j+1}: {cell_texts}")
            else:
                print("   ❌ Таблица не найдена")
        else:
            print("❌ Заголовок Scheduled events не найден")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    debug_page_structure()
