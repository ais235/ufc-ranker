#!/usr/bin/env python3
"""
Отладочный скрипт для проверки парсинга событий UFC с Wikipedia
"""

import requests
from bs4 import BeautifulSoup
import re

def debug_wikipedia_events():
    """Отлаживает парсинг событий UFC с Wikipedia"""
    
    print("🔍 ОТЛАДКА ПАРСИНГА СОБЫТИЙ UFC С WIKIPEDIA")
    print("=" * 50)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get("https://en.wikipedia.org/wiki/List_of_UFC_events", headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Ищем секцию Past events
        past_section = soup.find('h2', {'id': 'Past_events'})
        if not past_section:
            print("❌ Секция Past events не найдена")
            return
        
        print("✅ Секция Past events найдена")
        
        # Ищем таблицу после заголовка
        table = past_section.find_next('table')
        if not table:
            print("❌ Таблица Past events не найдена")
            return
        
        print("✅ Таблица Past events найдена")
        
        # Парсим первые 20 строк
        rows = table.find_all('tr')
        print(f"📊 Найдено {len(rows)} строк в таблице")
        
        print("\n🔍 Первые 20 строк таблицы:")
        for i, row in enumerate(rows[:21], 1):  # Первые 20 строк + заголовок
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 3:
                event_name = cells[0].get_text(strip=True)
                date_text = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                venue_text = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                
                print(f"{i:2d}. {event_name} | {date_text} | {venue_text}")
                
                # Ищем UFC 1-10
                if re.search(r'UFC\s+[1-9]', event_name):
                    print(f"    ⭐ НАЙДЕНО ИСТОРИЧЕСКОЕ СОБЫТИЕ: {event_name}")
        
        # Ищем все UFC события с номерами 1-100
        print(f"\n🔍 Поиск UFC событий с номерами 1-100:")
        ufc_events = []
        for row in rows[1:]:  # Пропускаем заголовок
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 3:
                event_name = cells[0].get_text(strip=True)
                if re.search(r'UFC\s+([1-9]|[1-9][0-9])', event_name):
                    ufc_events.append(event_name)
        
        print(f"📊 Найдено {len(ufc_events)} UFC событий с номерами 1-100")
        for event in ufc_events[:20]:  # Показываем первые 20
            print(f"   • {event}")
        
        if len(ufc_events) > 20:
            print(f"   ... и еще {len(ufc_events) - 20} событий")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    debug_wikipedia_events()
