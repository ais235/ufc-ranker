#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Обновленный парсер рейтингов UFC с Wikipedia для новой структуры БД
"""

import sqlite3
import requests
from lxml import html
import re
from datetime import datetime
import logging
from typing import Dict, List, Optional

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UpdatedUFCRankingsParser:
    """Обновленный парсер рейтингов UFC с Wikipedia"""
    
    def __init__(self, db_path="ufc_ranker_v2.db"):
        self.db_path = db_path
        self.rankings_url = "https://en.wikipedia.org/wiki/UFC_rankings"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Маппинг весовых категорий (Wikipedia -> БД)
        self.weight_class_mapping = {
            "Heavyweight": "Heavyweights",
            "Light Heavyweight": "Light Heavyweights", 
            "Middleweight": "Middleweights",
            "Welterweight": "Welterweights",
            "Lightweight": "Lightweights",
            "Featherweight": "Featherweights",
            "Bantamweight": "Bantamweights",
            "Flyweight": "Flyweights",
            "Women's Bantamweight": "Women's Bantamweights",
            "Women's Flyweight": "Women's Flyweights",
            "Women's Strawweight": "Women's Strawweights"
        }
    
    def get_page(self, url: str):
        """Получает HTML страницу"""
        try:
            logger.info(f"Загружаем страницу: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return html.fromstring(response.content)
        except Exception as e:
            logger.error(f"Ошибка при загрузке страницы {url}: {e}")
            return None
    
    def parse_record(self, record_text):
        """Парсит рекорд бойца из строки"""
        try:
            record_text = record_text.strip()
            record_text = re.sub(r'[^\d–\-\(\)\s]', '', record_text)
            
            main_parts = re.split(r'[–\-]', record_text)
            
            wins = int(main_parts[0]) if main_parts[0].strip().isdigit() else 0
            losses = int(main_parts[1]) if len(main_parts) > 1 and main_parts[1].strip().isdigit() else 0
            
            nc_match = re.search(r'\((\d+)\s*NC\)', record_text)
            nc = int(nc_match.group(1)) if nc_match else 0
            
            draws = 0
            if len(main_parts) > 2:
                third_part = main_parts[2].strip()
                if third_part.isdigit():
                    draws = int(third_part)
            
            return wins, losses, draws, nc
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге рекорда '{record_text}': {e}")
            return 0, 0, 0, 0
    
    def parse_ufc_rankings(self):
        """Парсит официальные рейтинги UFC с Wikipedia"""
        
        tree = self.get_page(self.rankings_url)
        if not tree:
            return None
        
        rankings_data = {}
        
        # Ищем все таблицы с рейтингами
        all_tables = tree.xpath('//table')
        
        # Таблицы рейтингов по весовым категориям
        weight_class_tables = {
            "Heavyweight": 4,
            "Light Heavyweight": 5,
            "Middleweight": 6,
            "Welterweight": 7,
            "Lightweight": 8,
            "Featherweight": 9,
            "Bantamweight": 10,
            "Flyweight": 11,
            "Women's Bantamweight": 12,
            "Women's Flyweight": 13,
            "Women's Strawweight": 14
        }
        
        for weight_class, table_index in weight_class_tables.items():
            logger.info(f"Парсинг {weight_class}...")
            
            if table_index >= len(all_tables):
                logger.warning(f"Таблица {table_index} не найдена для {weight_class}")
                continue
                
            table = all_tables[table_index - 1]
            rows = table.xpath('.//tr')
            
            if len(rows) <= 2:
                logger.warning(f"Таблица пуста для {weight_class}")
                continue
            
            data_rows = rows[2:]
            weight_rankings = []
            
            for i, row in enumerate(data_rows):
                try:
                    cells = row.xpath('.//td')
                    if len(cells) < 3:
                        continue
                    
                    rank_cell = cells[0]
                    rank_text = rank_cell.text_content().strip()
                    
                    fighter_cell = cells[1]
                    fighter_name = fighter_cell.text_content().strip()
                    if not fighter_name:
                        continue
                    
                    # Определяем позицию
                    if 'C' in rank_text or 'Champion' in rank_text:
                        rank_position = 0
                        is_champion = True
                    else:
                        rank_match = re.search(r'(\d+)', rank_text)
                        if rank_match:
                            rank_position = int(rank_match.group(1))
                            is_champion = False
                        else:
                            if i == 0:
                                rank_position = 0
                                is_champion = True
                            else:
                                rank_position = i
                                is_champion = False
                    
                    # Имя бойца и ссылка
                    fighter_cell = cells[1]
                    fighter_link = fighter_cell.xpath('.//a')
                    
                    if fighter_link:
                        fighter_name = fighter_link[0].text_content().strip()
                        fighter_url = fighter_link[0].get('href', '')
                        if fighter_url.startswith('/wiki/'):
                            fighter_url = 'https://en.wikipedia.org' + fighter_url
                    else:
                        fighter_name = fighter_cell.text_content().strip()
                        fighter_url = ''
                    
                    # Рекорд
                    record_cell = cells[2]
                    record_text = record_cell.text_content().strip()
                    wins, losses, draws, nc = self.parse_record(record_text)
                    
                    weight_rankings.append({
                        'rank_position': rank_position,
                        'is_champion': is_champion,
                        'fighter_name': fighter_name,
                        'fighter_url': fighter_url,
                        'record': record_text,
                        'wins': wins,
                        'losses': losses,
                        'draws': draws,
                        'nc': nc
                    })
                    
                except Exception as e:
                    logger.error(f"Ошибка при парсинге строки {i+1}: {e}")
                    continue
            
            if weight_rankings:
                rankings_data[weight_class] = weight_rankings
                logger.info(f"Найдено {len(weight_rankings)} бойцов в {weight_class}")
            else:
                logger.warning(f"Нет данных для {weight_class}")
        
        return rankings_data
    
    def clear_rankings_table(self, cursor):
        """Очищает таблицу rankings"""
        logger.info("Очищаем таблицу rankings...")
        cursor.execute("DELETE FROM rankings")
        logger.info("Таблица rankings очищена")
    
    def find_fighter_by_name(self, cursor, fighter_name: str) -> Optional[int]:
        """Находит бойца по имени в БД"""
        try:
            cursor.execute("""
                SELECT id FROM fighters 
                WHERE name_en = ? OR name_ru = ?
                ORDER BY 
                    CASE WHEN name_en = ? THEN 1 
                         ELSE 2 END,
                    id
                LIMIT 1
            """, (fighter_name, fighter_name, fighter_name))
            
            result = cursor.fetchone()
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Ошибка при поиске бойца {fighter_name}: {e}")
            return None
    
    def update_rankings_in_database(self, rankings_data):
        """Обновляет рейтинги в базе данных"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Очищаем таблицу rankings
            self.clear_rankings_table(cursor)
            
            total_updated = 0
            total_not_found = 0
            
            for weight_class, rankings in rankings_data.items():
                logger.info(f"Обновляем {weight_class}...")
                
                # Используем название весовой категории напрямую
                db_weight_class = weight_class
                
                for ranking in rankings:
                    try:
                        # Ищем бойца по имени
                        fighter_name = ranking['fighter_name']
                        fighter_id = self.find_fighter_by_name(cursor, fighter_name)
                        
                        if not fighter_id:
                            logger.warning(f"Боец {fighter_name} не найден в БД")
                            total_not_found += 1
                            continue
                        
                        # Вставляем рейтинг
                        cursor.execute("""
                            INSERT INTO rankings (
                                fighter_id, weight_class, rank_position, 
                                is_champion, created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            fighter_id,
                            weight_class,  # Используем строковое название весовой категории
                            ranking['rank_position'],
                            ranking['is_champion'],
                            datetime.now(),
                            datetime.now()
                        ))
                        
                        total_updated += 1
                        
                        champion_mark = "👑" if ranking['is_champion'] else ""
                        logger.info(f"{champion_mark} #{ranking['rank_position']:2d} {fighter_name}")
                        
                    except Exception as e:
                        logger.error(f"Ошибка при обновлении {ranking['fighter_name']}: {e}")
                        continue
            
            conn.commit()
            conn.close()
            
            logger.info(f"Обновлено {total_updated} рейтингов")
            logger.info(f"Не найдено бойцов: {total_not_found}")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении БД: {e}")
            return False
    
    def show_updated_rankings(self):
        """Показывает обновленные рейтинги"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            logger.info("ОБНОВЛЕННЫЕ РЕЙТИНГИ UFC")
            logger.info("=" * 60)
            
            # Получаем все весовые категории с рейтингами
            cursor.execute("""
                SELECT wc.name_ru, wc.name_en, COUNT(r.id) as count
                FROM weight_classes wc
                LEFT JOIN rankings r ON wc.name_en = r.weight_class
                GROUP BY wc.id, wc.name_ru, wc.name_en
                ORDER BY wc.id
            """)
            
            weight_classes = cursor.fetchall()
            
            for name_ru, name_en, count in weight_classes:
                logger.info(f"{name_ru} ({name_en})")
                logger.info("-" * 40)
                
                if count == 0:
                    logger.info("Нет рейтингов")
                    continue
                
                # Получаем топ-10 для этой категории
                cursor.execute("""
                    SELECT 
                        f.name_en,
                        f.nickname,
                        r.rank_position,
                        r.is_champion,
                        f.wins,
                        f.losses,
                        f.draws,
                        f.no_contests
                    FROM rankings r
                    JOIN fighters f ON r.fighter_id = f.id
                    WHERE r.weight_class = ?
                    ORDER BY r.rank_position ASC
                    LIMIT 10
                """, (name_en,))
                
                fighters = cursor.fetchall()
                
                for fighter in fighters:
                    name_en, nickname, rank_pos, is_champion, wins, losses, draws, nc = fighter
                    
                    champion_mark = "👑" if is_champion else ""
                    nickname_str = f' "{nickname}"' if nickname else ""
                    record_str = f"{wins}-{losses}" if wins is not None and losses is not None else "N/A"
                    if draws and draws > 0:
                        record_str += f"-{draws}"
                    if nc and nc > 0:
                        record_str += f" ({nc} NC)"
                    
                    logger.info(f"{champion_mark} #{rank_pos:2d} {name_en}{nickname_str} ({record_str})")
            
            # Статистика
            cursor.execute("SELECT COUNT(*) FROM rankings")
            total_rankings = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM rankings WHERE is_champion = 1")
            total_champions = cursor.fetchone()[0]
            
            logger.info(f"СТАТИСТИКА:")
            logger.info(f"Всего рейтингов: {total_rankings}")
            logger.info(f"Чемпионов: {total_champions}")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Ошибка при показе рейтингов: {e}")
    
    def run(self):
        """Запускает парсинг рейтингов"""
        logger.info("Запуск парсера рейтингов UFC...")
        
        try:
            # Парсим официальные рейтинги
            rankings_data = self.parse_ufc_rankings()
            
            if not rankings_data:
                logger.error("Не удалось получить данные рейтингов")
                return
            
            logger.info(f"Получены данные для {len(rankings_data)} весовых категорий")
            
            # Обновляем базу данных
            if self.update_rankings_in_database(rankings_data):
                logger.info("Рейтинги успешно обновлены!")
                
                # Показываем результат
                self.show_updated_rankings()
            else:
                logger.error("Ошибка при обновлении рейтингов")
            
        except Exception as e:
            logger.error(f"Ошибка при выполнении парсинга рейтингов: {e}")

def main():
    """Главная функция"""
    parser = UpdatedUFCRankingsParser()
    parser.run()

if __name__ == "__main__":
    main()
