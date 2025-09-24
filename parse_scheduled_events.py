#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Парсер для таблицы Scheduled events с Wikipedia
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
import time

class ScheduledEventsParser:
    """Парсер запланированных событий UFC"""
    
    def __init__(self, db_path="ufc_ranker_v2.db"):
        self.db_path = db_path
        self.base_url = "https://en.wikipedia.org"
        self.events_url = "https://en.wikipedia.org/wiki/List_of_UFC_events"
        
        # Заголовки для запросов
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    def parse_scheduled_events(self):
        """Парсит таблицу запланированных событий"""
        
        try:
            print("🔍 Загружаем страницу с запланированными событиями...")
            response = requests.get(self.events_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Находим таблицу Scheduled events
            scheduled_section = soup.find('h2', {'id': 'Scheduled_events'})
            if not scheduled_section:
                print("❌ Секция Scheduled events не найдена")
                return []
            
            scheduled_table = scheduled_section.find_next('table')
            if not scheduled_table:
                print("❌ Таблица Scheduled events не найдена")
                return []
            
            print("✅ Таблица Scheduled events найдена")
            
            # Парсим строки таблицы
            events = []
            rows = scheduled_table.find_all('tr')[1:]  # Пропускаем заголовок
            
            for i, row in enumerate(rows, 1):
                try:
                    event_data = self.parse_event_row(row)
                    if event_data:
                        events.append(event_data)
                        print(f"✅ Событие {i}: {event_data['name']}")
                    else:
                        print(f"❌ Не удалось распарсить строку {i}")
                except Exception as e:
                    print(f"❌ Ошибка при парсинге строки {i}: {e}")
            
            print(f"\n📊 Всего запланированных событий: {len(events)}")
            return events
            
        except Exception as e:
            print(f"❌ Ошибка при парсинге запланированных событий: {e}")
            return []
    
    def parse_event_row(self, row):
        """Парсит строку события из таблицы"""
        
        cells = row.find_all(['td', 'th'])
        if len(cells) < 4:
            return None
        
        # Извлекаем данные из ячеек
        event_cell = cells[0]
        date_cell = cells[1]
        venue_cell = cells[2]
        location_cell = cells[3]
        ref_cell = cells[4] if len(cells) > 4 else None
        
        # Парсим название события и ссылку
        event_link = event_cell.find('a')
        event_name = event_cell.get_text(strip=True)
        event_url = None
        
        if event_link:
            href = event_link.get('href')
            if href:
                event_url = urljoin(self.base_url, href)
        
        # Парсим дату
        date_text = date_cell.get_text(strip=True)
        parsed_date = self.parse_date(date_text)
        
        # Парсим арену и ссылку
        venue_link = venue_cell.find('a')
        venue_name = venue_cell.get_text(strip=True)
        venue_url = None
        
        if venue_link:
            href = venue_link.get('href')
            if href:
                venue_url = urljoin(self.base_url, href)
        
        # Парсим местоположение и ссылку
        location_link = location_cell.find('a')
        location_name = location_cell.get_text(strip=True)
        location_url = None
        
        if location_link:
            href = location_link.get('href')
            if href:
                location_url = urljoin(self.base_url, href)
        
        # Парсим ссылку на источник
        reference_url = None
        if ref_cell:
            ref_link = ref_cell.find('a')
            if ref_link:
                href = ref_link.get('href')
                if href:
                    reference_url = urljoin(self.base_url, href)
        
        # Извлекаем номер события и тип
        event_number, event_type = self.extract_event_info(event_name)
        
        return {
            'name': event_name,
            'event_number': event_number,
            'event_type': event_type,
            'date': parsed_date,
            'venue': venue_name,
            'venue_url': venue_url,
            'location': location_name,
            'location_url': location_url,
            'event_url': event_url,
            'reference_url': reference_url,
            'status': 'scheduled'
        }
    
    def parse_date(self, date_text):
        """Парсит дату из текста"""
        
        try:
            # Различные форматы дат
            date_patterns = [
                r'(\w+)\s+(\d+),\s+(\d{4})',  # Dec 13, 2025
                r'(\w+)\s+(\d{4})',           # June 2026
                r'(\d{1,2})/(\d{1,2})/(\d{4})',  # 12/25/2025
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, date_text)
                if match:
                    if len(match.groups()) == 3:
                        month_str, day_str, year_str = match.groups()
                        month = self.month_to_number(month_str)
                        if month:
                            return f"{year_str}-{month:02d}-{int(day_str):02d}"
                    elif len(match.groups()) == 2:
                        month_str, year_str = match.groups()
                        month = self.month_to_number(month_str)
                        if month:
                            return f"{year_str}-{month:02d}-01"  # Первое число месяца
            
            print(f"⚠️ Не удалось распарсить дату: {date_text}")
            return None
            
        except Exception as e:
            print(f"❌ Ошибка при парсинге даты '{date_text}': {e}")
            return None
    
    def month_to_number(self, month_str):
        """Конвертирует название месяца в число"""
        
        months = {
            'january': 1, 'jan': 1,
            'february': 2, 'feb': 2,
            'march': 3, 'mar': 3,
            'april': 4, 'apr': 4,
            'may': 5,
            'june': 6, 'jun': 6,
            'july': 7, 'jul': 7,
            'august': 8, 'aug': 8,
            'september': 9, 'sep': 9, 'sept': 9,
            'october': 10, 'oct': 10,
            'november': 11, 'nov': 11,
            'december': 12, 'dec': 12
        }
        
        return months.get(month_str.lower())
    
    def extract_event_info(self, event_name):
        """Извлекает номер события и тип из названия"""
        
        try:
            # Паттерны для различных типов событий
            patterns = [
                r'UFC\s+(\d+)',  # UFC 323
                r'UFC\s+Fight\s+Night\s+(\d+)',  # UFC Fight Night 266
                r'UFC\s+on\s+(\w+)',  # UFC on ESPN
                r'UFC\s+White\s+House',  # UFC White House
            ]
            
            for pattern in patterns:
                match = re.search(pattern, event_name, re.IGNORECASE)
                if match:
                    if 'Fight Night' in event_name:
                        return int(match.group(1)), 'UFC Fight Night'
                    elif 'UFC on' in event_name:
                        return None, 'UFC on ESPN'  # Или другой канал
                    elif 'White House' in event_name:
                        return None, 'UFC White House'
                    else:
                        return int(match.group(1)), 'UFC'
            
            # Если не найден номер, возвращаем None
            return None, 'UFC'
            
        except Exception as e:
            print(f"❌ Ошибка при извлечении информации о событии '{event_name}': {e}")
            return None, 'UFC'
    
    def save_events_to_db(self, events):
        """Сохраняет события в базу данных"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            print(f"\n💾 Сохраняем {len(events)} событий в базу данных...")
            
            saved_count = 0
            updated_count = 0
            
            for event in events:
                try:
                    # Проверяем, существует ли событие
                    cursor.execute("""
                        SELECT id FROM events 
                        WHERE name = ? AND event_number = ? AND event_type = ?
                    """, (event['name'], event['event_number'], event['event_type']))
                    
                    existing = cursor.fetchone()
                    
                    if existing:
                        # Обновляем существующее событие
                        cursor.execute("""
                            UPDATE events SET
                                date = ?, venue = ?, venue_url = ?,
                                location = ?, location_url = ?, event_url = ?,
                                reference_url = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                            WHERE id = ?
                        """, (
                            event['date'], event['venue'], event['venue_url'],
                            event['location'], event['location_url'], event['event_url'],
                            event['reference_url'], event['status'], existing[0]
                        ))
                        updated_count += 1
                        print(f"🔄 Обновлено: {event['name']}")
                    else:
                        # Создаем новое событие
                        cursor.execute("""
                            INSERT INTO events (
                                name, event_number, event_type, date, venue, venue_url,
                                location, location_url, event_url, reference_url, status
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            event['name'], event['event_number'], event['event_type'],
                            event['date'], event['venue'], event['venue_url'],
                            event['location'], event['location_url'], event['event_url'],
                            event['reference_url'], event['status']
                        ))
                        saved_count += 1
                        print(f"✅ Сохранено: {event['name']}")
                        
                except Exception as e:
                    print(f"❌ Ошибка при сохранении события '{event['name']}': {e}")
            
            conn.commit()
            conn.close()
            
            print(f"\n📊 Результаты сохранения:")
            print(f"  ✅ Новых событий: {saved_count}")
            print(f"  🔄 Обновленных событий: {updated_count}")
            print(f"  📈 Всего обработано: {saved_count + updated_count}")
            
        except Exception as e:
            print(f"❌ Ошибка при сохранении в базу данных: {e}")

def main():
    """Основная функция"""
    
    print("🚀 ПАРСЕР ЗАПЛАНИРОВАННЫХ СОБЫТИЙ UFC")
    print("=" * 50)
    
    parser = ScheduledEventsParser()
    
    # Парсим запланированные события
    events = parser.parse_scheduled_events()
    
    if events:
        # Сохраняем в базу данных
        parser.save_events_to_db(events)
        
        print(f"\n✅ Парсинг завершен успешно!")
        print(f"📊 Обработано событий: {len(events)}")
    else:
        print("\n❌ Не удалось получить данные о событиях")

if __name__ == "__main__":
    main()



