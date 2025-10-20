#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Обновленный парсер детальной страницы события UFC
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

class UpdatedEventDetailsParser:
    """Обновленный парсер детальной информации о событии UFC"""
    
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
    
    def parse_event_details(self, event_url):
        """Парсит детальную информацию о событии"""
        
        try:
            logger.info(f"Парсим детальную страницу: {event_url}")
            
            response = requests.get(event_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Извлекаем информацию о выручке
            gate_revenue = self.extract_gate_revenue(soup)
            
            # Извлекаем информацию о боях
            fights = self.extract_fights(soup)
            
            return {
                'gate_revenue': gate_revenue,
                'fights': fights
            }
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге детальной страницы: {e}")
            return None
    
    def extract_gate_revenue(self, soup):
        """Извлекает информацию о выручке"""
        
        try:
            # Ищем информацию о выручке по различным ключевым словам
            revenue_keywords = ['gate', 'revenue', 'attendance', 'выручка', 'доход']
            
            for keyword in revenue_keywords:
                # Ищем элементы с текстом, содержащим ключевое слово
                elements = soup.find_all(string=lambda text: text and keyword.lower() in text.lower())
                
                for elem in elements:
                    parent = elem.parent
                    if parent:
                        text = parent.get_text(strip=True)
                        
                        # Ищем числа в тексте (выручка обычно в долларах)
                        money_patterns = [
                            r'\$[\d,]+(?:\.\d{2})?',  # $1,234,567.89
                            r'[\d,]+(?:\.\d{2})?\s*(?:million|млн)',  # 1.5 million
                            r'[\d,]+(?:\.\d{2})?\s*(?:billion|млрд)',  # 1.2 billion
                        ]
                        
                        for pattern in money_patterns:
                            matches = re.findall(pattern, text, re.IGNORECASE)
                            if matches:
                                logger.info(f"Найдена информация о выручке: {text[:100]}...")
                                return self.parse_money_amount(matches[0])
            
            logger.warning("Информация о выручке не найдена")
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении выручки: {e}")
            return None
    
    def parse_money_amount(self, amount_str):
        """Парсит денежную сумму"""
        
        try:
            # Убираем символы валюты и пробелы
            clean_amount = re.sub(r'[^\d,.]', '', amount_str)
            
            # Убираем запятые
            clean_amount = clean_amount.replace(',', '')
            
            # Конвертируем в число
            if '.' in clean_amount:
                return float(clean_amount)
            else:
                return int(clean_amount)
                
        except Exception as e:
            logger.error(f"Ошибка при парсинге суммы '{amount_str}': {e}")
            return None
    
    def extract_fights(self, soup):
        """Извлекает информацию о боях"""
        
        try:
            fights = []
            
            # Ищем таблицу Results
            results_section = soup.find('h2', {'id': 'Results'})
            if not results_section:
                logger.error("Секция Results не найдена")
                return fights
            
            # Ищем таблицу после заголовка Results
            results_table = results_section.find_next('table')
            if not results_table:
                logger.error("Таблица Results не найдена")
                return fights
            
            logger.info("Таблица Results найдена")
            
            # Парсим таблицу боев
            fights = self.parse_fights_table(results_table)
            
            return fights
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении боев: {e}")
            return []
    
    def parse_fights_table(self, table):
        """Парсит таблицу с боями"""
        
        try:
            fights = []
            rows = table.find_all('tr')
            
            current_card_type = None
            
            for row in rows:
                # Проверяем, является ли строка заголовком карты
                card_type = self.detect_card_type(row)
                if card_type:
                    current_card_type = card_type
                    continue
                
                # Парсим строку боя
                fight_data = self.parse_fight_row(row, current_card_type)
                if fight_data:
                    fights.append(fight_data)
            
            logger.info(f"Найдено боев: {len(fights)}")
            return fights
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге таблицы боев: {e}")
            return []
    
    def detect_card_type(self, row):
        """Определяет тип карты боя"""
        
        try:
            text = row.get_text(strip=True).lower()
            
            if 'main card' in text:
                return 'main_card'
            elif 'preliminary card' in text:
                return 'preliminary_card'
            elif 'early preliminary card' in text:
                return 'early_preliminary_card'
            
            return None
            
        except Exception as e:
            return None
    
    def parse_fight_row(self, row, card_type):
        """Парсит строку боя"""
        
        try:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 6:
                return None
            
            # Извлекаем данные из ячеек
            weight_class_cell = cells[0]
            fighter1_cell = cells[1]
            result_cell = cells[2]
            fighter2_cell = cells[3]
            method_cell = cells[4]
            round_cell = cells[5]
            time_cell = cells[6] if len(cells) > 6 else None
            notes_cell = cells[7] if len(cells) > 7 else None
            
            # Парсим весовую категорию
            weight_class = weight_class_cell.get_text(strip=True)
            
            # Парсим имена бойцов
            fighter1_name = fighter1_cell.get_text(strip=True)
            fighter2_name = fighter2_cell.get_text(strip=True)
            
            # Парсим результат
            result_text = result_cell.get_text(strip=True)
            
            # Парсим метод победы
            method_text = method_cell.get_text(strip=True)
            method, method_details = self.parse_method(method_text)
            
            # Парсим раунд
            round_text = round_cell.get_text(strip=True)
            fight_round = self.parse_round(round_text)
            
            # Парсим время
            fight_time = None
            if time_cell:
                fight_time = time_cell.get_text(strip=True)
            
            # Парсим заметки
            notes = None
            if notes_cell:
                notes = notes_cell.get_text(strip=True)
            
            # Определяем победителя
            winner = self.determine_winner(fighter1_name, fighter2_name, result_text)
            
            return {
                'weight_class': weight_class,
                'fighter1_name': fighter1_name,
                'fighter2_name': fighter2_name,
                'winner': winner,
                'method': method,
                'method_details': method_details,
                'round': fight_round,
                'time': fight_time,
                'card_type': card_type,
                'notes': notes
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
    
    def determine_winner(self, fighter1, fighter2, result_text):
        """Определяет победителя"""
        
        try:
            # Если в результате есть "def.", то первый боец победил
            if 'def.' in result_text.lower():
                return fighter1
            
            # Если в результате есть имя бойца, то он победил
            if fighter1.lower() in result_text.lower():
                return fighter1
            elif fighter2.lower() in result_text.lower():
                return fighter2
            
            return None
            
        except Exception as e:
            return None
    
    def save_event_details_to_db(self, event_id, event_details):
        """Сохраняет детальную информацию о событии в базу данных с проверкой дублирования"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Обновляем информацию о событии
            if event_details['gate_revenue']:
                cursor.execute("""
                    UPDATE events SET gate_revenue = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (event_details['gate_revenue'], event_id))
                logger.info(f"Обновлена выручка: ${event_details['gate_revenue']:,.2f}")
            
            # Сохраняем информацию о боях
            fights_saved = 0
            fights_skipped = 0
            
            for fight in event_details['fights']:
                try:
                    # Находим ID бойцов
                    fighter1_id = self.find_fighter_id(fight['fighter1_name'])
                    fighter2_id = self.find_fighter_id(fight['fighter2_name'])
                    winner_id = None
                    
                    if fight['winner']:
                        if fight['winner'] == fight['fighter1_name']:
                            winner_id = fighter1_id
                        elif fight['winner'] == fight['fighter2_name']:
                            winner_id = fighter2_id
                    
                    # Проверяем уникальность боя
                    cursor.execute("""
                        SELECT id FROM fights 
                        WHERE event_id = ? AND fighter1_id = ? AND fighter2_id = ?
                    """, (event_id, fighter1_id, fighter2_id))
                    
                    existing = cursor.fetchone()
                    
                    if existing:
                        fights_skipped += 1
                        logger.debug(f"Бой уже существует: {fight['fighter1_name']} vs {fight['fighter2_name']}")
                    else:
                        # Сохраняем бой
                        cursor.execute("""
                            INSERT INTO fights (
                                event_id, fighter1_id, fighter2_id, winner_id,
                                result, method, method_details, round, time,
                                card_type, notes, created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        """, (
                            event_id, fighter1_id, fighter2_id, winner_id,
                            fight['method'], fight['method'], fight['method_details'],
                            fight['round'], fight['time'], fight['card_type'], fight['notes']
                        ))
                        
                        fights_saved += 1
                        logger.info(f"Сохранен бой: {fight['fighter1_name']} vs {fight['fighter2_name']}")
                    
                except Exception as e:
                    logger.error(f"Ошибка при сохранении боя: {e}")
            
            conn.commit()
            conn.close()
            
            logger.info(f"Результаты сохранения боев:")
            logger.info(f"  Новых боев: {fights_saved}")
            logger.info(f"  Пропущенных боев: {fights_skipped}")
            logger.info(f"  Всего обработано: {fights_saved + fights_skipped}")
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении детальной информации: {e}")
    
    def find_fighter_id(self, fighter_name):
        """Находит ID бойца по имени"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Ищем бойца по имени (проверяем и русское, и английское имя)
            cursor.execute("""
                SELECT id FROM fighters 
                WHERE name_ru LIKE ? OR name_en LIKE ? OR full_name LIKE ?
            """, (f"%{fighter_name}%", f"%{fighter_name}%", f"%{fighter_name}%"))
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                return result[0]
            else:
                logger.warning(f"Боец не найден: {fighter_name}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при поиске бойца '{fighter_name}': {e}")
            return None
    
    def parse_all_events_details(self, limit=None):
        """Парсит детальную информацию всех событий из базы данных"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Получаем список событий с URL
            cursor.execute("""
                SELECT id, name, event_url FROM events 
                WHERE event_url IS NOT NULL AND status = 'completed'
                ORDER BY date DESC
            """)
            
            events = cursor.fetchall()
            conn.close()
            
            if not events:
                logger.error("События с URL не найдены")
                return
            
            if limit:
                events = events[:limit]
                logger.info(f"Ограничение: парсим детали первых {limit} событий")
            
            logger.info(f"Найдено событий для парсинга: {len(events)}")
            
            for event_id, event_name, event_url in events:
                logger.info(f"\nПарсим событие: {event_name}")
                
                # Парсим детальную информацию
                event_details = self.parse_event_details(event_url)
                
                if event_details:
                    # Сохраняем в базу данных
                    self.save_event_details_to_db(event_id, event_details)
                    
                    logger.info(f"Событие '{event_name}' обработано")
                else:
                    logger.error(f"Не удалось обработать событие '{event_name}'")
                
                # Пауза между запросами
                time.sleep(2)
            
            logger.info(f"\n✅ Парсинг детальной информации завершен!")
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге детальной информации всех событий: {e}")

def main():
    """Основная функция"""
    
    print("🚀 ОБНОВЛЕННЫЙ ПАРСЕР ДЕТАЛЬНОЙ ИНФОРМАЦИИ О СОБЫТИЯХ UFC")
    print("=" * 70)
    
    parser = UpdatedEventDetailsParser()
    
    # Парсим детальную информацию всех событий (ограничиваем первыми 5 для тестирования)
    parser.parse_all_events_details(limit=5)

if __name__ == "__main__":
    main()







