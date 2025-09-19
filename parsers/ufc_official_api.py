#!/usr/bin/env python3
"""
Парсер официального UFC API
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
from .base_parser import BaseParser
from database.models import Fighter, WeightClass, Ranking, Event, Fight
from database.config import SessionLocal


class UFCOfficialAPIParser(BaseParser):
    """Парсер официального UFC API"""
    
    def __init__(self, cache_dir: str = ".cache/ufc_official"):
        super().__init__(cache_dir)
        self.base_url = "https://d29m7x9x9j2pb9.cloudfront.net"
        self.api_endpoints = {
            'rankings': '/rankings',
            'fighters': '/fighters',
            'events': '/events',
            'fights': '/fights'
        }
    
    def get_rankings(self) -> Dict[str, List[Dict]]:
        """Получает рейтинги с официального API"""
        print("🥊 Получение рейтингов с официального UFC API...")
        
        try:
            response = requests.get(f"{self.base_url}{self.api_endpoints['rankings']}", timeout=30)
            if response.status_code == 200:
                data = response.json()
                return self._parse_rankings_data(data)
            else:
                print(f"❌ Ошибка API: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ Ошибка при получении рейтингов: {e}")
            return {}
    
    def get_fighters(self) -> List[Dict]:
        """Получает список бойцов с официального API"""
        print("👥 Получение бойцов с официального UFC API...")
        
        try:
            response = requests.get(f"{self.base_url}{self.api_endpoints['fighters']}", timeout=30)
            if response.status_code == 200:
                data = response.json()
                return self._parse_fighters_data(data)
            else:
                print(f"❌ Ошибка API: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Ошибка при получении бойцов: {e}")
            return []
    
    def get_events(self) -> List[Dict]:
        """Получает события с официального API"""
        print("🎪 Получение событий с официального UFC API...")
        
        try:
            response = requests.get(f"{self.base_url}{self.api_endpoints['events']}", timeout=30)
            if response.status_code == 200:
                data = response.json()
                return self._parse_events_data(data)
            else:
                print(f"❌ Ошибка API: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Ошибка при получении событий: {e}")
            return []
    
    def _parse_rankings_data(self, data: Dict) -> Dict[str, List[Dict]]:
        """Парсит данные рейтингов"""
        categories = {}
        
        for division in data.get('divisions', []):
            division_name = division.get('name', '')
            fighters = []
            
            for fighter_data in division.get('fighters', []):
                fighter = {
                    'name': fighter_data.get('name', ''),
                    'rank': fighter_data.get('rank', 0),
                    'is_champion': fighter_data.get('isChampion', False),
                    'weight_class': division_name,
                    'country': fighter_data.get('country', ''),
                    'image_url': fighter_data.get('imageUrl', ''),
                    'profile_url': fighter_data.get('profileUrl', '')
                }
                fighters.append(fighter)
            
            if fighters:
                categories[division_name] = fighters
        
        return categories
    
    def _parse_fighters_data(self, data: Dict) -> List[Dict]:
        """Парсит данные бойцов"""
        fighters = []
        
        for fighter_data in data.get('fighters', []):
            fighter = {
                'name': fighter_data.get('name', ''),
                'nickname': fighter_data.get('nickname', ''),
                'country': fighter_data.get('country', ''),
                'image_url': fighter_data.get('imageUrl', ''),
                'height': fighter_data.get('height', 0),
                'weight': fighter_data.get('weight', 0),
                'reach': fighter_data.get('reach', 0),
                'age': fighter_data.get('age', 0),
                'wins': fighter_data.get('wins', 0),
                'losses': fighter_data.get('losses', 0),
                'draws': fighter_data.get('draws', 0),
                'weight_class': fighter_data.get('weightClass', ''),
                'profile_url': fighter_data.get('profileUrl', '')
            }
            fighters.append(fighter)
        
        return fighters
    
    def _parse_events_data(self, data: Dict) -> List[Dict]:
        """Парсит данные событий"""
        events = []
        
        for event_data in data.get('events', []):
            event = {
                'name': event_data.get('name', ''),
                'date': event_data.get('date', ''),
                'location': event_data.get('location', ''),
                'venue': event_data.get('venue', ''),
                'image_url': event_data.get('imageUrl', ''),
                'is_upcoming': event_data.get('isUpcoming', True),
                'attendance': event_data.get('attendance', 0)
            }
            events.append(event)
        
        return events
    
    def save_to_database(self, data: Dict) -> None:
        """Сохраняет данные в базу данных"""
        db = SessionLocal()
        try:
            # Сохраняем рейтинги
            if 'rankings' in data:
                self._save_rankings(db, data['rankings'])
            
            # Сохраняем бойцов
            if 'fighters' in data:
                self._save_fighters(db, data['fighters'])
            
            # Сохраняем события
            if 'events' in data:
                self._save_events(db, data['events'])
            
            db.commit()
            print("✅ Данные успешно сохранены в БД")
            
        except Exception as e:
            db.rollback()
            print(f"❌ Ошибка при сохранении в БД: {e}")
        finally:
            db.close()
    
    def _save_rankings(self, db, rankings: Dict[str, List[Dict]]) -> None:
        """Сохраняет рейтинги"""
        for category_name, fighters in rankings.items():
            # Создаем или получаем весовую категорию
            weight_class = db.query(WeightClass).filter(
                WeightClass.name_en == category_name
            ).first()
            
            if not weight_class:
                weight_class = WeightClass(
                    name_en=category_name,
                    name_ru=self._translate_category_name(category_name),
                    gender=self._detect_gender(category_name)
                )
                db.add(weight_class)
                db.flush()
            
            # Сохраняем бойцов и их рейтинги
            for fighter_data in fighters:
                fighter = self._get_or_create_fighter(db, fighter_data)
                
                ranking = Ranking(
                    fighter_id=fighter.id,
                    weight_class_id=weight_class.id,
                    rank_position=fighter_data.get('rank'),
                    is_champion=fighter_data.get('is_champion', False)
                )
                db.add(ranking)
    
    def _save_fighters(self, db, fighters: List[Dict]) -> None:
        """Сохраняет бойцов"""
        for fighter_data in fighters:
            self._get_or_create_fighter(db, fighter_data)
    
    def _save_events(self, db, events: List[Dict]) -> None:
        """Сохраняет события"""
        for event_data in events:
            event = Event(
                name=event_data.get('name', ''),
                date=datetime.strptime(event_data.get('date', ''), '%Y-%m-%d').date() if event_data.get('date') else None,
                location=event_data.get('location', ''),
                venue=event_data.get('venue', ''),
                image_url=event_data.get('image_url', ''),
                is_upcoming=event_data.get('is_upcoming', True),
                attendance=event_data.get('attendance', 0)
            )
            db.add(event)
    
    def _get_or_create_fighter(self, db, fighter_data: Dict) -> Fighter:
        """Создает или получает бойца"""
        fighter = db.query(Fighter).filter(
            Fighter.name_en == fighter_data.get('name', '')
        ).first()
        
        if not fighter:
            fighter = Fighter(
                name_en=fighter_data.get('name', ''),
                name_ru=fighter_data.get('name', ''),  # Пока используем то же имя
                nickname=fighter_data.get('nickname', ''),
                country=fighter_data.get('country', ''),
                image_url=fighter_data.get('image_url', ''),
                height=fighter_data.get('height', 0),
                weight=fighter_data.get('weight', 0),
                reach=fighter_data.get('reach', 0),
                age=fighter_data.get('age', 0),
                win=fighter_data.get('wins', 0),
                lose=fighter_data.get('losses', 0),
                draw=fighter_data.get('draws', 0),
                weight_class=fighter_data.get('weight_class', ''),
                profile_url=fighter_data.get('profile_url', ''),
                career="UFC"
            )
            db.add(fighter)
            db.flush()
        
        return fighter
    
    def _translate_category_name(self, name_en: str) -> str:
        """Переводит название категории на русский"""
        translations = {
            'Flyweight': 'Наилегчайший вес',
            'Bantamweight': 'Легчайший вес',
            'Featherweight': 'Полулегкий вес',
            'Lightweight': 'Легкий вес',
            'Welterweight': 'Полусредний вес',
            'Middleweight': 'Средний вес',
            'Light Heavyweight': 'Полутяжёлый вес',
            'Heavyweight': 'Тяжелый вес',
            "Women's Flyweight": 'Женский наилегчайший вес',
            "Women's Bantamweight": 'Женский легчайший вес',
            "Women's Strawweight": 'Женский минимальный вес',
            'Pound for Pound': 'Pound for Pound'
        }
        return translations.get(name_en, name_en)
    
    def _detect_gender(self, category_name: str) -> str:
        """Определяет пол по названию категории"""
        if "Women's" in category_name:
            return 'female'
        return 'male'
    
    def parse(self, use_cache: bool = True) -> Dict:
        """Основной метод парсинга"""
        print("🥊 Парсинг данных с официального UFC API...")
        
        data = {}
        
        # Получаем рейтинги
        rankings = self.get_rankings()
        if rankings:
            data['rankings'] = rankings
        
        # Получаем бойцов
        fighters = self.get_fighters()
        if fighters:
            data['fighters'] = fighters
        
        # Получаем события
        events = self.get_events()
        if events:
            data['events'] = events
        
        # Сохраняем в БД
        if data:
            self.save_to_database(data)
        
        return data

