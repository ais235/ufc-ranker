#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Обновленный парсер UFC с Wikipedia для новой структуры БД с внешними ключами
"""

import sqlite3
import requests
from lxml import html
import time
import re
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UpdatedUFCWikipediaParser:
    """Обновленный парсер UFC с Wikipedia для новой структуры БД"""
    
    def __init__(self, db_path='ufc_ranker_v2.db'):
        self.db_path = db_path
        self.base_url = "https://en.wikipedia.org"
        self.fighters_url = "https://en.wikipedia.org/wiki/List_of_current_UFC_fighters"
        self.rankings_url = "https://en.wikipedia.org/wiki/UFC_rankings"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Весовые категории с правильными данными
        self.weight_classes = {
            'Heavyweights': {
                'id': 'Heavyweights_.28265lb.2C_120_kg.29',
                'name_ru': 'Тяжелый вес',
                'name_en': 'Heavyweights',
                'weight_min': 120,
                'weight_max': 120,
                'gender': 'male'
            },
            'Light Heavyweights': {
                'id': 'Light_heavyweights_.28205_lb.2C_93_kg.29',
                'name_ru': 'Полутяжелый вес',
                'name_en': 'Light Heavyweights',
                'weight_min': 93,
                'weight_max': 93,
                'gender': 'male'
            },
            'Middleweights': {
                'id': 'Middleweights_.28185_lb.2C_84_kg.29',
                'name_ru': 'Средний вес',
                'name_en': 'Middleweights',
                'weight_min': 84,
                'weight_max': 84,
                'gender': 'male'
            },
            'Welterweights': {
                'id': 'Welterweights_.28170_lb.2C_77_kg.29',
                'name_ru': 'Полусредний вес',
                'name_en': 'Welterweights',
                'weight_min': 77,
                'weight_max': 77,
                'gender': 'male'
            },
            'Lightweights': {
                'id': 'Lightweights_.28155_lb.2C_70_kg.29',
                'name_ru': 'Легкий вес',
                'name_en': 'Lightweights',
                'weight_min': 70,
                'weight_max': 70,
                'gender': 'male'
            },
            'Featherweights': {
                'id': 'Featherweights_.28145_lb.2C_65_kg.29',
                'name_ru': 'Полулегкий вес',
                'name_en': 'Featherweights',
                'weight_min': 65,
                'weight_max': 65,
                'gender': 'male'
            },
            'Bantamweights': {
                'id': 'Bantamweights_.28135_lb.2C_61_kg.29',
                'name_ru': 'Легчайший вес',
                'name_en': 'Bantamweights',
                'weight_min': 61,
                'weight_max': 61,
                'gender': 'male'
            },
            'Flyweights': {
                'id': 'Flyweights_.28125_lb.2C_56_kg.29',
                'name_ru': 'Наилегчайший вес',
                'name_en': 'Flyweights',
                'weight_min': 56,
                'weight_max': 56,
                'gender': 'male'
            },
            'Women\'s Bantamweights': {
                'id': 'Women.27s_bantamweights_.28135_lb.2C_61_kg.29',
                'name_ru': 'Женский легчайший вес',
                'name_en': 'Women\'s Bantamweights',
                'weight_min': 61,
                'weight_max': 61,
                'gender': 'female'
            },
            'Women\'s Flyweights': {
                'id': 'Women.27s_flyweights_.28125_lb.2C_56_kg.29',
                'name_ru': 'Женский наилегчайший вес',
                'name_en': 'Women\'s Flyweights',
                'weight_min': 56,
                'weight_max': 56,
                'gender': 'female'
            },
            'Women\'s Strawweights': {
                'id': 'Women.27s_strawweights_.28115_lb.2C_52_kg.29',
                'name_ru': 'Женский минимальный вес',
                'name_en': 'Women\'s Strawweights',
                'weight_min': 52,
                'weight_max': 52,
                'gender': 'female'
            }
        }
    
    def get_page(self, url: str) -> Optional[html.HtmlElement]:
        """Получает страницу и возвращает HTML элемент"""
        try:
            logger.info(f"Загружаем страницу: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            tree = html.fromstring(response.content)
            return tree
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке страницы {url}: {e}")
            return None
    
    def init_database(self):
        """Инициализирует базу данных - создает весовые категории"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            logger.info("Инициализация весовых категорий...")
            
            for weight_class_name, weight_class_data in self.weight_classes.items():
                # Проверяем, существует ли уже категория
                cursor.execute("""
                    SELECT id FROM weight_classes 
                    WHERE name_en = ?
                """, (weight_class_data['name_en'],))
                
                if not cursor.fetchone():
                    # Создаем новую категорию
                    cursor.execute("""
                        INSERT INTO weight_classes (
                            name_ru, name_en, weight_min, weight_max, 
                            gender, is_p4p, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        weight_class_data['name_ru'],
                        weight_class_data['name_en'],
                        weight_class_data['weight_min'],
                        weight_class_data['weight_max'],
                        weight_class_data['gender'],
                        False,
                        datetime.now(),
                        datetime.now()
                    ))
                    logger.info(f"Создана весовая категория: {weight_class_data['name_en']}")
                else:
                    logger.info(f"Весовая категория уже существует: {weight_class_data['name_en']}")
            
            conn.commit()
            conn.close()
            logger.info("Инициализация базы данных завершена")
            
        except Exception as e:
            logger.error(f"Ошибка при инициализации БД: {e}")
    
    def check_duplicate_fighter(self, cursor, fighter_data: Dict) -> Optional[int]:
        """Проверяет, существует ли уже боец в БД"""
        try:
            # Ищем по имени (английскому и русскому)
            cursor.execute("""
                SELECT id FROM fighters 
                WHERE name_en = ? OR name_ru = ? OR name = ?
                LIMIT 1
            """, (fighter_data['name_en'], fighter_data['name_en'], fighter_data.get('name', '')))
            
            result = cursor.fetchone()
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Ошибка при проверке дубликата: {e}")
            return None
    
    def get_fighter_additional_data(self, profile_url: str) -> Dict[str, Optional[str]]:
        """Получает дополнительные данные бойца с его личной страницы Wikipedia"""
        try:
            if not profile_url:
                return {}
            
            profile_tree = self.get_page(profile_url)
            if not profile_tree:
                return {}
            
            additional_data = {}
            
            # Полное имя из заголовка страницы
            try:
                full_name_elements = profile_tree.xpath('//h1[@id="firstHeading"]//text()')
                if full_name_elements:
                    full_name = ''.join(full_name_elements).strip()
                    full_name = ' '.join(full_name.split())
                    additional_data['full_name'] = full_name
            except:
                pass
            
            # Дата рождения
            birth_date_xpaths = [
                '//table[contains(@class, "infobox")]//th[contains(text(), "Born")]/following-sibling::td[1]//text()',
                '//table[contains(@class, "infobox")]//th[contains(text(), "Date of birth")]/following-sibling::td[1]//text()',
                '//table[contains(@class, "infobox")]//th[contains(text(), "Birth")]/following-sibling::td[1]//text()'
            ]
            
            birth_date_text = None
            for xpath in birth_date_xpaths:
                try:
                    elements = profile_tree.xpath(xpath)
                    if elements:
                        birth_date_text = ' '.join(elements).strip()
                        break
                except:
                    continue
            
            if birth_date_text:
                birth_date = self.parse_birth_date_text(birth_date_text)
                if birth_date:
                    try:
                        birth_date_obj = datetime.strptime(birth_date, '%Y-%m-%d').date()
                        additional_data['birth_date'] = birth_date_obj
                    except ValueError:
                        additional_data['birth_date'] = None
                    additional_data['birth_place'] = self.extract_birth_place(birth_date_text)
            
            # Дополнительные поля
            fields = {
                'nickname': 'Other names',
                'stance': 'Stance',
                'team': 'Team',
                'trainer': 'Trainer',
                'belt_rank': 'Rank',
                'years_active': 'Years active',
                'current_division': 'Division'
            }
            
            for field, label in fields.items():
                try:
                    elements = profile_tree.xpath(f'//table[contains(@class, "infobox")]//th[contains(text(), "{label}")]/following-sibling::td[1]//text()')
                    if elements:
                        additional_data[field] = elements[0].strip()
                except:
                    pass
            
            return additional_data
            
        except Exception as e:
            logger.debug(f"Ошибка при получении дополнительных данных с {profile_url}: {e}")
            return {}
    
    def parse_birth_date_text(self, date_text: str) -> Optional[str]:
        """Парсит текст с датой рождения и возвращает дату в формате YYYY-MM-DD"""
        try:
            date_text = date_text.strip()
            
            patterns = [
                r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})',
                r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})',
                r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})',
                r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})',
                r'(\d{4})-(\d{1,2})-(\d{1,2})',
                r'(\d{1,2})/(\d{1,2})/(\d{4})'
            ]
            
            month_names = {
                'january': '01', 'february': '02', 'march': '03', 'april': '04',
                'may': '05', 'june': '06', 'july': '07', 'august': '08',
                'september': '09', 'october': '10', 'november': '11', 'december': '12',
                'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
                'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
            }
            
            for pattern in patterns:
                match = re.search(pattern, date_text, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    
                    if len(groups) == 3:
                        if groups[0].isdigit() and groups[1].isdigit() and groups[2].isdigit():
                            year, month, day = groups
                            if len(year) == 4:
                                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                            else:
                                return f"{groups[2]}-{groups[0].zfill(2)}-{groups[1].zfill(2)}"
                        elif groups[0].isdigit() and groups[2].isdigit():
                            day, month_name, year = groups
                            month = month_names.get(month_name.lower())
                            if month:
                                return f"{year}-{month}-{day.zfill(2)}"
                        elif groups[1].isdigit() and groups[2].isdigit():
                            month_name, day, year = groups
                            month = month_names.get(month_name.lower())
                            if month:
                                return f"{year}-{month}-{day.zfill(2)}"
            
            return None
            
        except Exception as e:
            logger.debug(f"Ошибка при парсинге даты рождения '{date_text}': {e}")
            return None
    
    def extract_birth_place(self, born_text: str) -> Optional[str]:
        """Извлекает место рождения из текста поля Born"""
        try:
            text_without_date = re.sub(r'\(\d{4}-\d{2}-\d{2}\)', '', born_text)
            text_without_age = re.sub(r'\(age\s+\d+\)', '', text_without_date)
            text_without_date_text = re.sub(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}', '', text_without_age)
            
            parts = text_without_date_text.strip().split()
            
            if len(parts) > 2:
                birth_place = ' '.join(parts[-3:]).strip()
                birth_place = re.sub(r'^[,\s]+|[,\s]+$', '', birth_place)
                return birth_place if birth_place else None
            
            return None
            
        except Exception as e:
            logger.debug(f"Ошибка при извлечении места рождения из '{born_text}': {e}")
            return None
    
    def parse_record(self, record_str: str) -> tuple:
        """Парсит рекорд в формате 28–12 (1 NC)"""
        if not record_str:
            return 0, 0, 0, 0
        
        record_str = record_str.strip()
        
        # Ищем паттерн W–L (NC)
        match = re.search(r'(\d+)–(\d+)(?:\s*\((\d+)\s*NC\))?', record_str)
        if match:
            wins = int(match.group(1))
            losses = int(match.group(2))
            no_contests = int(match.group(3)) if match.group(3) else 0
            return wins, losses, no_contests, 0
        
        # Если не нашли с длинным тире, пробуем с обычным дефисом
        match = re.search(r'(\d+)-(\d+)(?:\s*\((\d+)\s*NC\))?', record_str)
        if match:
            wins = int(match.group(1))
            losses = int(match.group(2))
            no_contests = int(match.group(3)) if match.group(3) else 0
            return wins, losses, no_contests, 0
        
        return 0, 0, 0, 0
    
    def extract_fighter_data(self, tree: html.HtmlElement, weight_class: str, row_num: int) -> Optional[Dict]:
        """Извлекает данные бойца из указанной строки таблицы"""
        try:
            weight_class_data = self.weight_classes[weight_class]
            base_xpath = f'//span[@id="{weight_class_data["id"]}"]/ancestor::div[1]/following-sibling::table[1]/tbody/tr[{row_num}]'
            
            # Имя и ссылка на профиль
            name_elements = tree.xpath(f'{base_xpath}/td[2]//a')
            if not name_elements:
                logger.warning(f"Не найдено имя бойца в строке {row_num}")
                return None
            
            name_element = name_elements[0]
            name_en = name_element.text_content().strip()
            profile_url = name_element.get('href', '')
            
            if profile_url.startswith('/wiki/'):
                profile_url = f"{self.base_url}{profile_url}"
            elif not profile_url.startswith('http'):
                profile_url = f"{self.base_url}/wiki/{profile_url}"
            
            # Получаем дополнительные данные с личной страницы бойца
            additional_data = self.get_fighter_additional_data(profile_url)
            
            # Возраст
            age_text = tree.xpath(f'{base_xpath}/td[3]/text()')
            age = None
            if age_text:
                age_match = re.search(r'\d+', age_text[0])
                if age_match:
                    age = int(age_match.group())
            
            # Рост
            height_text = tree.xpath(f'{base_xpath}/td[4]/text()')
            height = None
            if height_text:
                height_match = re.search(r'(\d+)\s*ft\s*(\d+)\s*in', height_text[0])
                if height_match:
                    feet = int(height_match.group(1))
                    inches = int(height_match.group(2))
                    height = feet * 30.48 + inches * 2.54
                else:
                    height_match = re.search(r'(\d+)\s*ft', height_text[0])
                    if height_match:
                        feet = int(height_match.group(1))
                        height = feet * 30.48
            
            # Никнейм
            nickname_elements = tree.xpath(f'{base_xpath}/td[5]/i')
            nickname = None
            if nickname_elements:
                nickname = nickname_elements[0].text_content().strip()
            
            # Вес
            weight_text = tree.xpath(f'{base_xpath}/td[6]/text()')
            weight = None
            if weight_text:
                weight_match = re.search(r'(\d+)\s*lb', weight_text[0])
                if weight_match:
                    weight_lb = int(weight_match.group(1))
                    weight = weight_lb * 0.453592
            
            # Размах рук
            reach_text = tree.xpath(f'{base_xpath}/td[7]/text()')
            reach = None
            if reach_text:
                reach_match = re.search(r'(\d+)\s*in', reach_text[0])
                if reach_match:
                    reach_inches = int(reach_match.group(1))
                    reach = reach_inches * 2.54
            
            # Рекорд в UFC (колонка 8)
            ufc_record_text = tree.xpath(f'{base_xpath}/td[8]//text()')
            ufc_record = None
            if ufc_record_text:
                ufc_record = ' '.join(ufc_record_text).strip()
            
            # Рекорд в ММА (колонка 9)
            mma_record_text = tree.xpath(f'{base_xpath}/td[9]//text()')
            mma_record = None
            if mma_record_text:
                mma_record = ' '.join(mma_record_text).strip()
            
            # Страна
            country_elements = tree.xpath(f'{base_xpath}/td[1]//a[@title]/@title')
            country = None
            if country_elements:
                country = country_elements[0].strip()
            
            # Парсим рекорды
            wins, losses, draws, no_contests = self.parse_record(mma_record or ufc_record or "0-0-0")
            
            fighter_data = {
                'name_en': name_en,
                'name_ru': name_en,
                'nickname': additional_data.get('nickname') or nickname,
                'country': country,
                'profile_url': profile_url,
                'height': int(height) if height else None,
                'weight': int(weight) if weight else None,
                'reach': int(reach) if reach else None,
                'age': age,
                'birth_date': additional_data.get('birth_date'),
                'weight_class': weight_class_data['name_ru'],
                'win': wins,
                'draw': draws,
                'lose': losses,
                'career': 'UFC',
                'ufc_record': ufc_record,
                'mma_record': mma_record,
                'row_number': row_num,
                'full_name': additional_data.get('full_name'),
                'birth_place': additional_data.get('birth_place'),
                'stance': additional_data.get('stance'),
                'team': additional_data.get('team'),
                'trainer': additional_data.get('trainer'),
                'belt_rank': additional_data.get('belt_rank'),
                'years_active': additional_data.get('years_active'),
                'current_division': additional_data.get('current_division')
            }
            
            logger.info(f"Извлечен боец: {name_en} ({country}) - {mma_record}")
            return fighter_data
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении данных бойца в строке {row_num}: {e}")
            return None
    
    def get_fighters_count(self, tree: html.HtmlElement, weight_class: str) -> int:
        """Получает количество бойцов в весовой категории"""
        try:
            weight_class_data = self.weight_classes[weight_class]
            rows_xpath = f'//span[@id="{weight_class_data["id"]}"]/ancestor::div[1]/following-sibling::table[1]/tbody/tr'
            rows = tree.xpath(rows_xpath)
            return len(rows)
        except Exception as e:
            logger.error(f"Ошибка при подсчете бойцов в категории {weight_class}: {e}")
            return 0
    
    def parse_weight_class(self, tree: html.HtmlElement, weight_class: str) -> List[Dict]:
        """Парсит бойцов указанной весовой категории"""
        logger.info(f"Начинаем парсинг {weight_class}...")
        
        fighters = []
        fighters_count = self.get_fighters_count(tree, weight_class)
        logger.info(f"Найдено {fighters_count} бойцов в категории {weight_class}")
        
        for row_num in range(1, fighters_count + 1):
            try:
                fighter_data = self.extract_fighter_data(tree, weight_class, row_num)
                if fighter_data:
                    fighters.append(fighter_data)
                
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Ошибка при парсинге бойца в строке {row_num}: {e}")
                continue
        
        logger.info(f"Успешно извлечено {len(fighters)} бойцов {weight_class}")
        return fighters
    
    def save_fighters_to_database(self, fighters_data: Dict[str, List[Dict]]):
        """Сохраняет бойцов в базу данных с проверкой дубликатов"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            logger.info("Начинаем сохранение бойцов в базу данных...")
            
            # Получаем маппинг весовых категорий
            cursor.execute("SELECT id, name_en FROM weight_classes")
            weight_classes = {name_en: id for id, name_en in cursor.fetchall()}
            
            total_saved = 0
            total_skipped = 0
            
            for weight_class_name, fighters in fighters_data.items():
                if weight_class_name not in weight_classes:
                    logger.warning(f"Весовая категория {weight_class_name} не найдена в БД")
                    continue
                
                weight_class_id = weight_classes[weight_class_name]
                
                for fighter_data in fighters:
                    try:
                        # Проверяем дубликат
                        existing_id = self.check_duplicate_fighter(cursor, fighter_data)
                        if existing_id:
                            logger.info(f"Боец уже существует: {fighter_data['name_en']} (ID: {existing_id})")
                            total_skipped += 1
                            continue
                        
                        # Создаем бойца
                        cursor.execute("""
                            INSERT INTO fighters (
                                name, name_ru, name_en, nickname, country, profile_url,
                                height, weight, reach, age, birth_date, weight_class,
                                wins, draws, losses, career, birth_place,
                                stance, team, trainer, belt_rank, years_active,
                                current_division, fighting_out_of, created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            fighter_data.get('name', fighter_data['name_en']),  # name
                            fighter_data['name_ru'],
                            fighter_data['name_en'],
                            fighter_data['nickname'],
                            fighter_data['country'],
                            fighter_data['profile_url'],
                            fighter_data['height'],
                            fighter_data['weight'],
                            fighter_data['reach'],
                            fighter_data['age'],
                            fighter_data['birth_date'],
                            fighter_data['weight_class'],
                            fighter_data['win'],  # wins
                            fighter_data['draw'],  # draws
                            fighter_data['lose'],  # losses
                            fighter_data['career'],
                            fighter_data['birth_place'],
                            fighter_data['stance'],
                            fighter_data['team'],
                            fighter_data['trainer'],
                            fighter_data['belt_rank'],
                            fighter_data['years_active'],
                            fighter_data['current_division'],
                            None,  # fighting_out_of
                            datetime.now(),
                            datetime.now()
                        ))
                        
                        fighter_id = cursor.lastrowid
                        
                        # Создаем боевой рекорд
                        cursor.execute("""
                            INSERT INTO fight_records (
                                fighter_id, wins, losses, draws, no_contests, weight_class,
                                created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            fighter_id,
                            fighter_data['win'],
                            fighter_data['lose'],
                            fighter_data['draw'],
                            0,
                            fighter_data['weight_class'],
                            datetime.now(),
                            datetime.now()
                        ))
                        
                        total_saved += 1
                        logger.info(f"Сохранен боец: {fighter_data['name_en']} ({weight_class_name})")
                        
                    except Exception as e:
                        logger.error(f"Ошибка при сохранении бойца {fighter_data.get('name_en', 'Unknown')}: {e}")
                        continue
            
            conn.commit()
            conn.close()
            
            logger.info(f"Сохранение завершено: {total_saved} новых бойцов, {total_skipped} пропущено")
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении в базу данных: {e}")
    
    def parse_all_fighters(self) -> Dict[str, List[Dict]]:
        """Парсит всех бойцов со страницы"""
        logger.info("Начинаем парсинг всех бойцов UFC...")
        
        tree = self.get_page(self.fighters_url)
        if not tree:
            logger.error("Не удалось загрузить страницу")
            return {}
        
        all_fighters = {}
        
        for weight_class in self.weight_classes.keys():
            try:
                fighters = self.parse_weight_class(tree, weight_class)
                if fighters:
                    all_fighters[weight_class] = fighters
                else:
                    logger.warning(f"Не найдено бойцов в категории {weight_class}")
            except Exception as e:
                logger.error(f"Ошибка при парсинге категории {weight_class}: {e}")
                continue
        
        return all_fighters
    
    def run(self):
        """Запускает парсинг"""
        logger.info("Запуск обновленного парсера UFC Wikipedia...")
        
        try:
            # Инициализируем базу данных
            self.init_database()
            
            # Парсим всех бойцов
            fighters_data = self.parse_all_fighters()
            
            # Выводим статистику
            total_fighters = sum(len(fighters) for fighters in fighters_data.values())
            logger.info(f"Всего извлечено бойцов: {total_fighters}")
            
            for weight_class, fighters in fighters_data.items():
                logger.info(f"{weight_class}: {len(fighters)} бойцов")
            
            # Сохраняем в базу данных
            self.save_fighters_to_database(fighters_data)
            
            logger.info("Парсинг завершен успешно!")
            
        except Exception as e:
            logger.error(f"Ошибка при выполнении парсинга: {e}")

def main():
    """Главная функция"""
    parser = UpdatedUFCWikipediaParser()
    parser.run()

if __name__ == "__main__":
    main()
