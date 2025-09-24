#!/usr/bin/env python3
"""
Отладочный скрипт для анализа содержимого таблицы Past events
"""

import requests
from bs4 import BeautifulSoup
import re

def debug_past_events():
    """Анализирует содержимое таблицы Past events"""
    
    print("🔍 АНАЛИЗ ТАБЛИЦЫ PAST EVENTS")
    print("=" * 50)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get("https://en.wikipedia.org/wiki/List_of_UFC_events", headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Находим заголовок Past events
        past_header = soup.find('h2', {'id': 'Past_events'})
        if not past_header:
            print("❌ Заголовок Past events не найден")
            return
        
        # Ищем таблицу после заголовка
        table = past_header.find_next('table')
        if not table:
            print("❌ Таблица Past events не найдена")
            return
        
        print("✅ Таблица Past events найдена")
        
        # Парсим строки таблицы
        rows = table.find_all('tr')
        print(f"📊 Найдено {len(rows)} строк в таблице")
        
        # Ищем номерные UFC события
        numbered_events = []
        fight_night_events = []
        other_events = []
        
        for i, row in enumerate(rows[1:], 1):  # Пропускаем заголовок
            cells = row.find_all(['td', 'th'])
            if len(cells) < 3:
                continue
            
            # Название события (обычно во второй ячейке)
            event_name = cells[1].get_text(strip=True)
            
            # Очищаем название
            event_name = re.sub(r'\[.*?\]', '', event_name)
            event_name = event_name.strip()
            
            if not event_name or event_name in ['Event', 'Date', 'Venue', 'City', '#']:
                continue
            
            # Классифицируем события
            if re.search(r'UFC\s+\d+', event_name):
                numbered_events.append(event_name)
            elif 'Fight Night' in event_name:
                fight_night_events.append(event_name)
            else:
                other_events.append(event_name)
        
        print(f"\n📊 Классификация событий:")
        print(f"   • Номерные UFC события: {len(numbered_events)}")
        print(f"   • Fight Night события: {len(fight_night_events)}")
        print(f"   • Другие события: {len(other_events)}")
        
        # Показываем первые 20 номерных событий
        print(f"\n🔍 Первые 20 номерных UFC событий:")
        for i, event in enumerate(numbered_events[:20]):
            print(f"   {i+1}. {event}")
        
        # Показываем последние 20 номерных событий
        if len(numbered_events) > 20:
            print(f"\n🔍 Последние 20 номерных UFC событий:")
            for i, event in enumerate(numbered_events[-20:], len(numbered_events)-19):
                print(f"   {i}. {event}")
        
        # Ищем UFC 1-10
        print(f"\n🔍 Поиск UFC 1-10:")
        for i in range(1, 11):
            ufc_pattern = f"UFC {i}"
            found = [event for event in numbered_events if ufc_pattern in event]
            if found:
                print(f"   ✅ {ufc_pattern}: {found[0]}")
            else:
                print(f"   ❌ {ufc_pattern}: не найдено")
        
        # Ищем UFC 100-110
        print(f"\n🔍 Поиск UFC 100-110:")
        for i in range(100, 111):
            ufc_pattern = f"UFC {i}"
            found = [event for event in numbered_events if ufc_pattern in event]
            if found:
                print(f"   ✅ {ufc_pattern}: {found[0]}")
            else:
                print(f"   ❌ {ufc_pattern}: не найдено")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    debug_past_events()
