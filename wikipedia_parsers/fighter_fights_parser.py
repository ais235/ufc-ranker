#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Парсер боёв каждого бойца с их страниц Wikipedia
Извлекает информацию о боях и сохраняет в таблицу fights с проверкой уникальности
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

class FighterFightsParser:
    """Парсер боёв бойцов UFC с их страниц Wikipedia"""
    
    def __init__(self, db_path="ufc_ranker_v2.db"):
        self.db_path = db_path
        self.base_url = "https://en.wikipedia.org"
        
        # Заголовки для запросов
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    def parse_fighter_fights(self, fighter_id, fighter_name, fighter_url):
        """Парсит бои конкретного бойца с его страницы Wikipedia"""
        
        try:
            logger.info(f"Парсим бои бойца: {fighter_name}")
            
            response = requests.get(fighter_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Ищем таблицу с боями
            fights_table = self.find_fights_table(soup)
            if not fights_table:
                logger.warning(f"Таблица с боями не найдена для {fighter_name}")
                return []
            
            # Парсим таблицу боев
            fights = self.parse_fights_table(fights_table, fighter_id, fighter_name)
            
            logger.info(f"Найдено боев для {fighter_name}: {len(fights)}")
            return fights
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге боев {fighter_name}: {e}")
            return []
    
    def find_fights_table(self, soup):
        """Находит таблицу с боями на странице бойца"""
        
        try:
            # Ищем таблицу по различным критериям
            tables = soup.find_all('table', {'class': 'wikitable'})
            
            for table in tables:
                # Проверяем заголовки таблицы
                headers = table.find_all('th')
                header_texts = [th.get_text(strip=True).lower() for th in headers]
                
                # Ищем таблицу с боями по ключевым словам в заголовках
                fight_keywords = ['opponent', 'result', 'method', 'round', 'time', 'date', 'event']
                if any(keyword in ' '.join(header_texts) for keyword in fight_keywords):
                    return table
            
            # Если не найдена таблица с боями, ищем любую таблицу с результатами
            for table in tables:
                rows = table.find_all('tr')
                if len(rows) > 1:  # Есть данные, не только заголовки
                    first_row = rows[1]  # Первая строка с данными
                    cells = first_row.find_all(['td', 'th'])
                    if len(cells) >= 3:  # Минимум 3 колонки
                        return table
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при поиске таблицы с боями: {e}")
            return None
    
    def parse_fights_table(self, table, fighter_id, fighter_name):
        """Парсит таблицу с боями"""
        
        try:
            fights = []
            rows = table.find_all('tr')
            
            # Пропускаем заголовок
            data_rows = rows[1:] if len(rows) > 1 else []
            
            for row in data_rows:
                try:
                    fight_data = self.parse_fight_row(row, fighter_id, fighter_name)
                    if fight_data:
                        fights.append(fight_data)
                except Exception as e:
                    logger.error(f"Ошибка при парсинге строки боя: {e}")
            
            return fights
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге таблицы боев: {e}")
            return []
    
    def parse_fight_row(self, row, fighter_id, fighter_name):
        """Парсит строку боя из таблицы"""
        
        try:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 3:
                return None
            
            # Извлекаем данные из ячеек
            opponent_cell = cells[0] if len(cells) > 0 else None
            result_cell = cells[1] if len(cells) > 1 else None
            method_cell = cells[2] if len(cells) > 2 else None
            round_cell = cells[3] if len(cells) > 3 else None
            time_cell = cells[4] if len(cells) > 4 else None
            date_cell = cells[5] if len(cells) > 5 else None
            event_cell = cells[6] if len(cells) > 6 else None
            
            # Парсим соперника
            opponent_name = None
            if opponent_cell:
                opponent_name = opponent_cell.get_text(strip=True)
                # Убираем лишние символы
                opponent_name = re.sub(r'[\[\]]', '', opponent_name)
            
            # Парсим результат
            result = None
            if result_cell:
                result = result_cell.get_text(strip=True)
            
            # Парсим метод
            method = None
            method_details = None
            if method_cell:
                method_text = method_cell.get_text(strip=True)
                method, method_details = self.parse_method(method_text)
            
            # Парсим раунд
            fight_round = None
            if round_cell:
                round_text = round_cell.get_text(strip=True)
                fight_round = self.parse_round(round_text)
            
            # Парсим время
            fight_time = None
            if time_cell:
                fight_time = time_cell.get_text(strip=True)
            
            # Парсим дату
            fight_date = None
            if date_cell:
                date_text = date_cell.get_text(strip=True)
                fight_date = self.parse_date(date_text)
            
            # Парсим событие
            event_name = None
            if event_cell:
                event_name = event_cell.get_text(strip=True)
            
            # Определяем победителя
            winner_id = None
            if result and 'win' in result.lower():
                winner_id = fighter_id
            
            # Определяем рекорд бойца на момент боя
            fighter_record = self.extract_fighter_record(result, fighter_name)
            
            # Определяем рекорд соперника (если есть информация)
            opponent_record = self.extract_opponent_record(result, opponent_name)
            
            return {
                'fighter1_id': fighter_id,
                'fighter2_name': opponent_name,
                'winner_id': winner_id,
                'result': result,
                'method': method,
                'method_details': method_details,
                'round': fight_round,
                'time': fight_time,
                'fight_date': fight_date,
                'event_name': event_name,
                'fighter1_record': fighter_record,
                'fighter2_record': opponent_record
            }
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге строки боя: {e}")
            return None
    
    def parse_method(self, method_text):
        """Парсит метод победы"""
        
        try:
            # Ищем решения судей в скобках
            judge_pattern = r'\(([^)]+)\)'
            judge_matches = re.findall(judge_pattern, method_text)
            
            method_details = None
            if judge_matches:
                method_details = judge_matches[0]
            
            # Убираем детали судей из основного метода
            clean_method = re.sub(r'\([^)]+\)', '', method_text).strip()
            
            return clean_method, method_details
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге метода '{method_text}': {e}")
            return method_text, None
    
    def parse_round(self, round_text):
        """Парсит раунд"""
        
        try:
            if round_text.isdigit():
                return int(round_text)
            return None
            
        except Exception as e:
            return None
    
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
    
    def extract_fighter_record(self, result, fighter_name):
        """Извлекает рекорд бойца на момент боя"""
        
        try:
            if not result:
                return None
            
            # Ищем рекорд в формате "Win (15-2-0)"
            record_pattern = r'Win\s*\((\d+-\d+-\d+)\)'
            match = re.search(record_pattern, result, re.IGNORECASE)
            if match:
                return match.group(1)
            
            # Ищем рекорд в формате "Loss (15-3-0)"
            record_pattern = r'Loss\s*\((\d+-\d+-\d+)\)'
            match = re.search(record_pattern, result, re.IGNORECASE)
            if match:
                return match.group(1)
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении рекорда бойца: {e}")
            return None
    
    def extract_opponent_record(self, result, opponent_name):
        """Извлекает рекорд соперника на момент боя"""
        
        try:
            if not result or not opponent_name:
                return None
            
            # Ищем рекорд соперника в формате "vs. John Doe (15-2-0)"
            record_pattern = rf'{re.escape(opponent_name)}\s*\((\d+-\d+-\d+)\)'
            match = re.search(record_pattern, result, re.IGNORECASE)
            if match:
                return match.group(1)
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении рекорда соперника: {e}")
            return None
    
    def save_fights_to_db(self, fights):
        """Сохраняет бои в базу данных с проверкой уникальности"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            logger.info(f"Сохраняем {len(fights)} боев в базу данных...")
            
            saved_count = 0
            skipped_count = 0
            
            for fight in fights:
                try:
                    # Проверяем уникальность боя
                    # Бой уникален если: fighter1_id + fighter2_name + fight_date уникальны
                    cursor.execute("""
                        SELECT id FROM fights 
                        WHERE fighter1_id = ? AND opponent_name = ? AND fight_date = ?
                    """, (fight['fighter1_id'], fight['fighter2_name'], fight['fight_date']))
                    
                    existing = cursor.fetchone()
                    
                    if existing:
                        skipped_count += 1
                        logger.debug(f"Бой уже существует: {fight['fighter2_name']} vs {fight['fight_date']}")
                    else:
                        # Находим ID события
                        event_id = self.find_event_id(fight['event_name'])
                        
                        # Создаем новый бой
                        cursor.execute("""
                            INSERT INTO fights (
                                event_id, fighter1_id, fighter2_id, winner_id,
                                result, method, method_details, round, time,
                                fight_date, opponent_name, fighter1_record, fighter2_record,
                                created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        """, (
                            event_id, fight['fighter1_id'], None, fight['winner_id'],
                            fight['result'], fight['method'], fight['method_details'], fight['round'], fight['time'],
                            fight['fight_date'], fight['fighter2_name'], fight['fighter1_record'], fight['fighter2_record']
                        ))
                        saved_count += 1
                        logger.info(f"Сохранен бой: {fight['fighter2_name']} vs {fight['fight_date']}")
                        
                except Exception as e:
                    logger.error(f"Ошибка при сохранении боя: {e}")
            
            conn.commit()
            conn.close()
            
            logger.info(f"Результаты сохранения боев:")
            logger.info(f"  Новых боев: {saved_count}")
            logger.info(f"  Пропущенных боев: {skipped_count}")
            logger.info(f"  Всего обработано: {saved_count + skipped_count}")
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении боев в базу данных: {e}")
    
    def find_event_id(self, event_name):
        """Находит ID события по названию"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if not event_name:
                return None
            
            # Ищем событие по названию
            cursor.execute("""
                SELECT id FROM events 
                WHERE name LIKE ? OR name LIKE ?
            """, (f"%{event_name}%", f"%{event_name}%"))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0]
            else:
                logger.warning(f"Событие не найдено: {event_name}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при поиске события '{event_name}': {e}")
            return None
    
    def parse_all_fighters_fights(self, limit=None):
        """Парсит бои всех бойцов из базы данных"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Получаем список бойцов с URL
            cursor.execute("""
                SELECT id, name_en, profile_url FROM fighters 
                WHERE profile_url IS NOT NULL AND profile_url LIKE '%wikipedia%'
                ORDER BY name_en
            """)
            
            fighters = cursor.fetchall()
            conn.close()
            
            if not fighters:
                logger.error("Бойцы с URL Wikipedia не найдены")
                return
            
            if limit:
                fighters = fighters[:limit]
                logger.info(f"Ограничение: парсим бои первых {limit} бойцов")
            
            logger.info(f"Найдено бойцов для парсинга: {len(fighters)}")
            
            total_fights = 0
            
            for fighter_id, fighter_name, fighter_url in fighters:
                logger.info(f"\nПарсим бои бойца: {fighter_name}")
                
                # Парсим бои бойца
                fights = self.parse_fighter_fights(fighter_id, fighter_name, fighter_url)
                
                if fights:
                    # Сохраняем бои в базу данных
                    self.save_fights_to_db(fights)
                    total_fights += len(fights)
                
                # Пауза между запросами
                time.sleep(2)
            
            logger.info(f"\n✅ Парсинг боёв всех бойцов завершен!")
            logger.info(f"📊 Всего обработано боев: {total_fights}")
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге боёв всех бойцов: {e}")

def main():
    """Основная функция"""
    
    print("🚀 ПАРСЕР БОЁВ БОЙЦОВ UFC С WIKIPEDIA")
    print("=" * 60)
    
    parser = FighterFightsParser()
    
    # Парсим бои всех бойцов (ограничиваем первыми 10 для тестирования)
    parser.parse_all_fighters_fights(limit=10)

if __name__ == "__main__":
    main()
