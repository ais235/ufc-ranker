#!/usr/bin/env python3
"""
Парсер рейтингов UFC с fight.ru
"""

import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from .base_parser import BaseParser
from database.models import Fighter, WeightClass, Ranking, FightRecord
from database.config import SessionLocal


class UFCRankingsParser(BaseParser):
    """Парсер рейтингов UFC"""
    
    def __init__(self, cache_dir: str = ".cache/rankings"):
        super().__init__(cache_dir)
        self.base_url = "https://fight.ru/fighter-ratings/ufc/"
    
    def parse_rankings(self, html: str) -> Dict[str, List[Dict]]:
        """Парсит рейтинги из HTML"""
        soup = self.parse_html(html)
        categories = {}
        
        # Ищем все секции весовых категорий
        weight_sections = soup.find_all('div', class_='weight-name')
        
        for section in weight_sections:
            category_name = self.clean_text(section.get_text())
            
            # Пропускаем пустые или служебные категории
            if not category_name or category_name in ['Весовая категория', 'Все']:
                continue
            
            # Находим родительскую секцию с бойцами
            category_section = section.find_parent('div', class_='org-single')
            if not category_section:
                continue
            
            # Извлекаем бойцов
            fighters = self._extract_fighters_from_category(category_section, category_name)
            if fighters:
                categories[category_name] = fighters
        
        return categories
    
    def _extract_fighters_from_category(self, category_section, category_name: str) -> List[Dict]:
        """Извлекает список бойцов из конкретной весовой категории"""
        fighters = []
        
        # Извлекаем чемпиона (first-fighter)
        champion = category_section.find('div', class_='first-fighter')
        if champion:
            fighter_data = self._extract_fighter_data(champion, is_champion=True)
            if fighter_data:
                fighters.append(fighter_data)
        
        # Извлекаем остальных бойцов (next-fighter)
        next_fighters = category_section.find_all('div', class_='next-fighter')
        
        for fighter in next_fighters:
            fighter_data = self._extract_fighter_data(fighter, is_champion=False)
            if fighter_data:
                fighters.append(fighter_data)
        
        return fighters
    
    def _extract_fighter_data(self, fighter_element, is_champion: bool = False) -> Optional[Dict]:
        """Извлекает данные бойца из HTML элемента"""
        # Получаем имя
        name_elem = fighter_element.find('div', class_='fighter-name')
        if not name_elem:
            return None
        
        name = self.clean_text(name_elem.get_text())
        if not name:
            return None
        
        # Получаем ссылку на профиль
        profile_url = None
        link_elem = fighter_element.find('a')
        if link_elem and link_elem.get('href'):
            profile_url = link_elem['href']
            if not profile_url.startswith('http'):
                profile_url = f"https://fight.ru{profile_url}"
        
        # Получаем позицию в рейтинге
        if is_champion:
            rank = 'Ч'
            rank_position = 0
        else:
            number_elem = fighter_element.find('div', class_='fighter-number')
            if not number_elem:
                return None
            
            rank = self.clean_text(number_elem.get_text())
            try:
                rank_position = int(rank)
            except ValueError:
                rank_position = None
        
        # Получаем информацию об изменении позиции
        move_info = ""
        move_elem = fighter_element.find('div', class_='move')
        if move_elem:
            move_text = self.clean_text(move_elem.get_text())
            if 'up' in move_elem.get('class', []):
                move_info = f"↑{move_text}"
            elif 'down' in move_elem.get('class', []):
                move_info = f"↓{move_text}"
        
        return {
            'name': name,
            'rank': rank,
            'rank_position': rank_position,
            'is_champion': is_champion,
            'profile_url': profile_url,
            'move_info': move_info
        }
    
    def save_to_database(self, categories: Dict[str, List[Dict]]) -> None:
        """Сохраняет рейтинги в базу данных"""
        db = SessionLocal()
        try:
            for category_name, fighters in categories.items():
                # Создаем или получаем весовую категорию
                weight_class = db.query(WeightClass).filter(
                    WeightClass.name_ru == category_name
                ).first()
                
                if not weight_class:
                    weight_class = WeightClass(
                        name_ru=category_name,
                        name_en=self._translate_category_name(category_name),
                        gender=self._detect_gender(category_name),
                        is_p4p='p4p' in category_name.lower()
                    )
                    db.add(weight_class)
                    db.flush()
                
                # Обрабатываем каждого бойца
                for fighter_data in fighters:
                    # Создаем или получаем бойца
                    fighter = db.query(Fighter).filter(
                        Fighter.name_ru == fighter_data['name']
                    ).first()
                    
                    if not fighter:
                        fighter = Fighter(
                            name_ru=fighter_data['name'],
                            profile_url=fighter_data.get('profile_url')
                        )
                        db.add(fighter)
                        db.flush()
                    
                    # Создаем или обновляем рейтинг
                    ranking = db.query(Ranking).filter(
                        Ranking.fighter_id == fighter.id,
                        Ranking.weight_class_id == weight_class.id
                    ).first()
                    
                    if not ranking:
                        ranking = Ranking(
                            fighter_id=fighter.id,
                            weight_class_id=weight_class.id,
                            rank_position=fighter_data.get('rank_position'),
                            is_champion=fighter_data['is_champion']
                        )
                        db.add(ranking)
                    else:
                        ranking.rank_position = fighter_data.get('rank_position')
                        ranking.is_champion = fighter_data['is_champion']
            
            db.commit()
            print(f"✅ Сохранено {len(categories)} категорий в БД")
            
        except Exception as e:
            db.rollback()
            print(f"❌ Ошибка при сохранении в БД: {e}")
        finally:
            db.close()
    
    def _translate_category_name(self, name_ru: str) -> str:
        """Переводит название категории на английский"""
        translations = {
            'наилегчайший вес': 'Flyweight',
            'легчайший вес': 'Bantamweight', 
            'полулегкий вес': 'Featherweight',
            'легкий вес': 'Lightweight',
            'полусредний вес': 'Welterweight',
            'средний вес': 'Middleweight',
            'полутяжёлый вес': 'Light Heavyweight',
            'тяжелый вес': 'Heavyweight',
            'женский наилегчайший': 'Women\'s Flyweight',
            'женский легчайший вес': 'Women\'s Bantamweight',
            'женский минимальный': 'Women\'s Strawweight',
            '(p4p)': 'Pound for Pound',
            '(p4p) (жен)': 'Women\'s Pound for Pound'
        }
        return translations.get(name_ru, name_ru)
    
    def _detect_gender(self, category_name: str) -> str:
        """Определяет пол по названию категории"""
        if 'женский' in category_name.lower() or '(жен)' in category_name.lower():
            return 'female'
        return 'male'
    
    def parse(self, use_cache: bool = True) -> Dict[str, List[Dict]]:
        """Основной метод парсинга"""
        print("🥊 Парсинг рейтингов UFC...")
        
        html = self.fetch(self.base_url, use_cache=use_cache)
        if not html:
            print("❌ Не удалось загрузить страницу рейтингов")
            return {}
        
        categories = self.parse_rankings(html)
        print(f"✅ Найдено категорий: {len(categories)}")
        
        # Сохраняем в БД
        self.save_to_database(categories)
        
        return categories




























