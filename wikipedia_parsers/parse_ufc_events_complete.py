#!/usr/bin/env python3
"""
Полный парсер событий UFC с Wikipedia
Парсит все исторические события из таблицы Past events
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

class UFCEventsParser:
    """Парсер всех событий UFC с Wikipedia"""
    
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
    
    def parse_all_events(self):
        """Парсит все события UFC с Wikipedia"""
        
        try:
            logger.info("🔍 Загружаем страницу со всеми событиями UFC...")
            response = requests.get(self.events_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            all_events = []
            
            # Парсим секцию Past events
            logger.info("📋 Парсим секцию Past events...")
            past_events = self.parse_past_events(soup)
            all_events.extend(past_events)
            logger.info(f"   ✅ Найдено {len(past_events)} прошедших событий")
            
            # Парсим секцию Scheduled events
            logger.info("📋 Парсим секцию Scheduled events...")
            scheduled_events = self.parse_scheduled_events(soup)
            all_events.extend(scheduled_events)
            logger.info(f"   ✅ Найдено {len(scheduled_events)} запланированных событий")
            
            logger.info(f"📊 Всего найдено событий: {len(all_events)}")
            return all_events
            
        except Exception as e:
            logger.error(f"❌ Ошибка при парсинге событий: {e}")
            return []
    
    def parse_past_events(self, soup):
        """Парсит секцию Past events"""
        
        events = []
        
        try:
            # Находим секцию Past events
            past_section = soup.find('h2', {'id': 'Past_events'})
            if not past_section:
                logger.warning("⚠️ Секция Past events не найдена")
                return events
            
            # Находим таблицу после заголовка
            table = past_section.find_next('table')
            if not table:
                logger.warning("⚠️ Таблица Past events не найдена")
                return events
            
            # Парсим строки таблицы
            rows = table.find_all('tr')
            logger.info(f"📊 Найдено {len(rows)} строк в таблице Past events")
            
            for i, row in enumerate(rows[1:], 1):  # Пропускаем заголовок
                try:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) < 3:
                        continue
                    
                    # Извлекаем данные из ячеек
                    event_data = self.extract_event_data(cells, "Past_events")
                    if event_data:
                        events.append(event_data)
                        
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка при парсинге строки {i} в Past events: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"❌ Ошибка при парсинге Past events: {e}")
        
        return events
    
    def parse_scheduled_events(self, soup):
        """Парсит секцию Scheduled events"""
        
        events = []
        
        try:
            # Находим секцию Scheduled events
            scheduled_section = soup.find('h2', {'id': 'Scheduled_events'})
            if not scheduled_section:
                logger.warning("⚠️ Секция Scheduled events не найдена")
                return events
            
            # Находим таблицу после заголовка
            table = scheduled_section.find_next('table')
            if not table:
                logger.warning("⚠️ Таблица Scheduled events не найдена")
                return events
            
            # Парсим строки таблицы
            rows = table.find_all('tr')
            logger.info(f"📊 Найдено {len(rows)} строк в таблице Scheduled events")
            
            for i, row in enumerate(rows[1:], 1):  # Пропускаем заголовок
                try:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) < 3:
                        continue
                    
                    # Извлекаем данные из ячеек
                    event_data = self.extract_event_data(cells, "Scheduled_events")
                    if event_data:
                        events.append(event_data)
                        
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка при парсинге строки {i} в Scheduled events: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"❌ Ошибка при парсинге Scheduled events: {e}")
        
        return events
    
    def extract_event_data(self, cells, section_type):
        """Извлекает данные о событии из ячеек таблицы"""
        
        try:
            # Название события (обычно в первой ячейке)
            event_name_cell = cells[0]
            event_name = event_name_cell.get_text(strip=True)
            
            # Очищаем название от лишних символов
            event_name = re.sub(r'\[.*?\]', '', event_name)  # Убираем [edit]
            event_name = event_name.strip()
            
            if not event_name or event_name in ['Event', 'Date', 'Venue', 'City', '#']:
                return None
            
            # Дата события (обычно во второй ячейке)
            date_text = cells[1].get_text(strip=True) if len(cells) > 1 else ""
            
            # Место проведения (обычно в третьей ячейке)
            venue_text = cells[2].get_text(strip=True) if len(cells) > 2 else ""
            
            # Город (обычно в четвертой ячейке)
            location_text = cells[3].get_text(strip=True) if len(cells) > 3 else ""
            
            # Парсим дату
            event_date = self.parse_date(date_text)
            
            # Определяем тип события
            event_type = self.determine_event_type(event_name, section_type)
            
            # Извлекаем номер события
            event_number = self.extract_event_number(event_name)
            
            # Определяем статус
            status = "completed" if section_type == "Past_events" else "scheduled"
            
            event_data = {
                'name': event_name,
                'event_number': event_number,
                'event_type': event_type,
                'date': event_date,
                'venue': venue_text,
                'location': location_text,
                'status': status,
                'is_upcoming': section_type != "Past_events"
            }
            
            return event_data
            
        except Exception as e:
            logger.warning(f"⚠️ Ошибка при извлечении данных события: {e}")
            return None
    
    def parse_date(self, date_text):
        """Парсит дату из текста"""
        
        if not date_text:
            return None
        
        try:
            # Убираем лишние символы
            date_text = re.sub(r'\[.*?\]', '', date_text)
            date_text = date_text.strip()
            
            # Пробуем разные форматы дат
            date_formats = [
                '%B %d, %Y',      # January 1, 2023
                '%b %d, %Y',      # Jan 1, 2023
                '%d %B %Y',       # 1 January 2023
                '%d %b %Y',       # 1 Jan 2023
                '%Y-%m-%d',       # 2023-01-01
                '%m/%d/%Y',       # 01/01/2023
                '%d/%m/%Y',       # 01/01/2023
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_text, fmt).date()
                except ValueError:
                    continue
            
            # Если не удалось распарсить, возвращаем None
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Не удалось распарсить дату '{date_text}': {e}")
            return None
    
    def determine_event_type(self, event_name, section_type):
        """Определяет тип события"""
        
        event_name_lower = event_name.lower()
        
        if 'ufc' in event_name_lower and any(num in event_name_lower for num in ['1', '2', '3', '4', '5', '6', '7', '8', '9']):
            return 'UFC'
        elif 'fight night' in event_name_lower:
            return 'Fight Night'
        elif 'ultimate fighter' in event_name_lower or 'tuf' in event_name_lower:
            return 'The Ultimate Fighter'
        elif 'fox' in event_name_lower:
            return 'UFC on Fox'
        elif 'espn' in event_name_lower:
            return 'UFC on ESPN'
        elif 'abc' in event_name_lower:
            return 'UFC on ABC'
        elif 'fx' in event_name_lower:
            return 'UFC on FX'
        elif 'versus' in event_name_lower:
            return 'UFC on Versus'
        elif 'spike' in event_name_lower:
            return 'UFC on Spike'
        elif 'fuel' in event_name_lower:
            return 'UFC on Fuel TV'
        elif 'fs1' in event_name_lower:
            return 'UFC on FS1'
        elif 'fs2' in event_name_lower:
            return 'UFC on FS2'
        else:
            return 'Other'
    
    def extract_event_number(self, event_name):
        """Извлекает номер события"""
        
        # Ищем паттерн UFC XXX
        match = re.search(r'UFC\s+(\d+)', event_name)
        if match:
            return match.group(1)
        
        # Ищем паттерн Fight Night XXX
        match = re.search(r'Fight\s+Night\s+(\d+)', event_name)
        if match:
            return f"FN{match.group(1)}"
        
        return None
    
    def save_events(self, events):
        """Сохраняет события в базу данных"""
        
        if not events:
            logger.warning("⚠️ Нет событий для сохранения")
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            new_count = 0
            updated_count = 0
            skipped_count = 0
            
            for event in events:
                try:
                    # Проверяем, существует ли событие
                    cursor.execute("""
                        SELECT id FROM events 
                        WHERE name = ? OR (event_number = ? AND event_number IS NOT NULL)
                    """, (event['name'], event['event_number']))
                    
                    existing = cursor.fetchone()
                    
                    if existing:
                        # Обновляем существующее событие
                        cursor.execute("""
                            UPDATE events SET
                                event_number = ?,
                                event_type = ?,
                                date = ?,
                                venue = ?,
                                location = ?,
                                status = ?,
                                is_upcoming = ?,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE id = ?
                        """, (
                            event['event_number'],
                            event['event_type'],
                            event['date'],
                            event['venue'],
                            event['location'],
                            event['status'],
                            event['is_upcoming'],
                            existing[0]
                        ))
                        updated_count += 1
                        
                    else:
                        # Создаем новое событие
                        cursor.execute("""
                            INSERT INTO events (
                                name, event_number, event_type, date, venue, location,
                                status, is_upcoming, created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        """, (
                            event['name'],
                            event['event_number'],
                            event['event_type'],
                            event['date'],
                            event['venue'],
                            event['location'],
                            event['status'],
                            event['is_upcoming']
                        ))
                        new_count += 1
                        
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка при сохранении события '{event['name']}': {e}")
                    skipped_count += 1
                    continue
            
            conn.commit()
            
            logger.info(f"✅ Сохранение завершено!")
            logger.info(f"📊 Статистика:")
            logger.info(f"   • Новых событий: {new_count}")
            logger.info(f"   • Обновленных событий: {updated_count}")
            logger.info(f"   • Пропущенных событий: {skipped_count}")
            logger.info(f"   • Всего обработано: {len(events)}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при сохранении в БД: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()

def main():
    """Основная функция"""
    
    print("🚀 ПАРСЕР ВСЕХ СОБЫТИЙ UFC С WIKIPEDIA")
    print("=" * 50)
    
    parser = UFCEventsParser()
    
    # Парсим все события
    events = parser.parse_all_events()
    
    if events:
        # Сохраняем в базу данных
        parser.save_events(events)
        
        print(f"\n✅ Парсинг завершен успешно!")
        print(f"📊 Обработано событий: {len(events)}")
    else:
        print("❌ Не удалось получить события")

if __name__ == "__main__":
    main()
