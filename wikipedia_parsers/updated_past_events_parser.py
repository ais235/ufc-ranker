#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Обновленный парсер для таблицы Past events с Wikipedia
Поддерживает новую структуру БД с проверкой дублирования
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
import time
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UpdatedPastEventsParser:
    """Обновленный парсер прошедших событий UFC"""
    
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
    
    def parse_past_events(self, limit=None):
        """Парсит таблицу прошедших событий"""
        
        try:
            logger.info("Загружаем страницу с прошедшими событиями...")
            response = requests.get(self.events_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Находим таблицу Past events
            past_section = soup.find('h2', {'id': 'Past_events'})
            if not past_section:
                logger.error("Секция Past events не найдена")
                return []
            
            past_table = past_section.find_next('table')
            if not past_table:
                logger.error("Таблица Past events не найдена")
                return []
            
            logger.info("Таблица Past events найдена")
            
            # Парсим строки таблицы
            events = []
            rows = past_table.find_all('tr')[1:]  # Пропускаем заголовок
            
            if limit:
                rows = rows[:limit]
                logger.info(f"Ограничение: парсим первые {limit} событий")
            
            for i, row in enumerate(rows, 1):
                try:
                    event_data = self.parse_past_event_row(row)
                    if event_data:
                        events.append(event_data)
                        logger.info(f"Событие {i}: {event_data['name']}")
                    else:
                        logger.warning(f"Не удалось распарсить строку {i}")
                except Exception as e:
                    logger.error(f"Ошибка при парсинге строки {i}: {e}")
            
            logger.info(f"Всего прошедших событий: {len(events)}")
            return events
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге прошедших событий: {e}")
            return []
    
    def parse_past_event_row(self, row):
        """Парсит строку прошедшего события из таблицы"""
        
        cells = row.find_all(['td', 'th'])
        if len(cells) < 6:
            return None
        
        # Извлекаем данные из ячеек
        number_cell = cells[0]  # #
        event_cell = cells[1]   # Event
        date_cell = cells[2]    # Date
        venue_cell = cells[3]   # Venue
        location_cell = cells[4] # Location
        attendance_cell = cells[5] # Attendance
        ref_cell = cells[6] if len(cells) > 6 else None # Ref.
        
        # Парсим номер события
        event_number_text = number_cell.get_text(strip=True)
        event_number = None
        if event_number_text.isdigit():
            event_number = int(event_number_text)
        
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
        
        # Парсим посещаемость
        attendance_text = attendance_cell.get_text(strip=True)
        attendance = None
        if attendance_text and attendance_text != '—':
            # Убираем запятые и конвертируем в число
            attendance_clean = attendance_text.replace(',', '')
            if attendance_clean.isdigit():
                attendance = int(attendance_clean)
        
        # Парсим ссылку на источник
        reference_url = None
        if ref_cell:
            ref_link = ref_cell.find('a')
            if ref_link:
                href = ref_link.get('href')
                if href:
                    reference_url = urljoin(self.base_url, href)
        
        # Извлекаем номер события и тип
        extracted_number, event_type = self.extract_event_info(event_name)
        
        # Используем номер из таблицы, если он есть, иначе извлекаем из названия
        final_event_number = event_number if event_number else extracted_number
        
        return {
            'name': event_name,
            'event_number': final_event_number,
            'event_type': event_type,
            'date': parsed_date,
            'venue': venue_name,
            'venue_url': venue_url,
            'location': location_name,
            'location_url': location_url,
            'attendance': attendance,
            'event_url': event_url,
            'reference_url': reference_url,
            'status': 'completed'
        }
    
    def parse_date(self, date_text):
        """Парсит дату из текста"""
        
        try:
            # Различные форматы дат
            date_patterns = [
                r'(\w+)\s+(\d+),\s+(\d{4})',  # Sep 13, 2025
                r'(\w+)\s+(\d{1,2}),\s+(\d{4})',  # Sep 6, 2025
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
            
            logger.warning(f"Не удалось распарсить дату: {date_text}")
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге даты '{date_text}': {e}")
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
                r'UFC\s+(\d+)',  # UFC 319
                r'UFC\s+Fight\s+Night\s+(\d+)',  # UFC Fight Night 266
                r'UFC\s+Fight\s+Night:\s+([^0-9]+)',  # UFC Fight Night: Lopes vs. Silva
                r'UFC\s+on\s+(\w+)',  # UFC on ESPN
            ]
            
            for pattern in patterns:
                match = re.search(pattern, event_name, re.IGNORECASE)
                if match:
                    if 'Fight Night' in event_name:
                        if match.group(1).isdigit():
                            return int(match.group(1)), 'UFC Fight Night'
                        else:
                            return None, 'UFC Fight Night'
                    elif 'UFC on' in event_name:
                        return None, 'UFC on ESPN'  # Или другой канал
                    else:
                        return int(match.group(1)), 'UFC'
            
            # Если не найден номер, возвращаем None
            return None, 'UFC'
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении информации о событии '{event_name}': {e}")
            return None, 'UFC'
    
    def save_events_to_db(self, events):
        """Сохраняет события в базу данных с проверкой дублирования"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            logger.info(f"Сохраняем {len(events)} событий в базу данных...")
            
            saved_count = 0
            updated_count = 0
            skipped_count = 0
            
            for event in events:
                try:
                    # Проверяем, существует ли событие (более строгая проверка)
                    cursor.execute("""
                        SELECT id FROM events 
                        WHERE name = ? AND event_number = ? AND event_type = ? AND date = ?
                    """, (event['name'], event['event_number'], event['event_type'], event['date']))
                    
                    existing = cursor.fetchone()
                    
                    if existing:
                        # Проверяем, нужно ли обновление
                        cursor.execute("""
                            SELECT venue, location, attendance, event_url, reference_url 
                            FROM events WHERE id = ?
                        """, (existing[0],))
                        
                        current_data = cursor.fetchone()
                        
                        # Обновляем только если есть изменения
                        if (current_data[0] != event['venue'] or 
                            current_data[1] != event['location'] or 
                            current_data[2] != event['attendance'] or
                            current_data[3] != event['event_url'] or
                            current_data[4] != event['reference_url']):
                            
                            cursor.execute("""
                                UPDATE events SET
                                    venue = ?, venue_url = ?, location = ?, location_url = ?, 
                                    event_url = ?, reference_url = ?, attendance = ?, 
                                    updated_at = CURRENT_TIMESTAMP
                                WHERE id = ?
                            """, (
                                event['venue'], event['venue_url'], event['location'], 
                                event['location_url'], event['event_url'], event['reference_url'], 
                                event['attendance'], existing[0]
                            ))
                            updated_count += 1
                            logger.info(f"Обновлено: {event['name']}")
                        else:
                            skipped_count += 1
                            logger.debug(f"Пропущено (без изменений): {event['name']}")
                    else:
                        # Создаем новое событие
                        cursor.execute("""
                            INSERT INTO events (
                                name, event_number, event_type, date, venue, venue_url,
                                location, location_url, event_url, reference_url, status, attendance,
                                created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        """, (
                            event['name'], event['event_number'], event['event_type'],
                            event['date'], event['venue'], event['venue_url'],
                            event['location'], event['location_url'], event['event_url'],
                            event['reference_url'], event['status'], event['attendance']
                        ))
                        saved_count += 1
                        logger.info(f"Сохранено: {event['name']}")
                        
                except Exception as e:
                    logger.error(f"Ошибка при сохранении события '{event['name']}': {e}")
            
            conn.commit()
            conn.close()
            
            logger.info(f"Результаты сохранения:")
            logger.info(f"  Новых событий: {saved_count}")
            logger.info(f"  Обновленных событий: {updated_count}")
            logger.info(f"  Пропущенных событий: {skipped_count}")
            logger.info(f"  Всего обработано: {saved_count + updated_count + skipped_count}")
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении в базу данных: {e}")

def main():
    """Основная функция"""
    
    print("ОБНОВЛЕННЫЙ ПАРСЕР ПРОШЕДШИХ СОБЫТИЙ UFC")
    print("=" * 60)
    
    parser = UpdatedPastEventsParser()
    
    # Парсим прошедшие события (ограничиваем первыми 20 для тестирования)
    events = parser.parse_past_events(limit=20)
    
    if events:
        # Сохраняем в базу данных
        parser.save_events_to_db(events)
        
        print(f"\nПарсинг завершен успешно!")
        print(f"Обработано событий: {len(events)}")
    else:
        print("\nНе удалось получить данные о событиях")

if __name__ == "__main__":
    main()







