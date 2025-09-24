#!/usr/bin/env python3
"""
Адаптер для интеграции UFC API от FritzCapuyan с нашей БД
"""

import sys
import os
from typing import Dict, List, Optional
from datetime import datetime, date
import re

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ufc import get_fighter, get_event
    UFC_API_AVAILABLE = True
except ImportError:
    UFC_API_AVAILABLE = False
    print("⚠️ UFC API не установлен. Установите: pip install ufc_api")

from database.models import Fighter, WeightClass, Event, Fight, FightRecord, Ranking
from database.config import SessionLocal


class UFCAPIAdapter:
    """Адаптер для интеграции UFC API с нашей БД"""
    
    def __init__(self):
        if not UFC_API_AVAILABLE:
            raise ImportError("UFC API не доступен. Установите: pip install ufc_api")
        
        self.db = SessionLocal()
        self.weight_class_mapping = {
            'Heavyweight': 'Тяжелый вес',
            'Light Heavyweight': 'Полутяжелый вес', 
            'Middleweight': 'Средний вес',
            'Welterweight': 'Полусредний вес',
            'Lightweight': 'Легкий вес',
            'Featherweight': 'Полулегкий вес',
            'Bantamweight': 'Легчайший вес',
            'Flyweight': 'Наилегчайший вес',
            'Women\'s Strawweight': 'Женский минимальный вес',
            'Women\'s Flyweight': 'Женский наилегчайший вес',
            'Women\'s Bantamweight': 'Женский легчайший вес',
            'Women\'s Featherweight': 'Женский полулегкий вес'
        }
    
    def convert_height_to_cm(self, height_str: str) -> Optional[int]:
        """Конвертирует рост из футов в сантиметры"""
        if not height_str or height_str == '--':
            return None
        
        # Парсим формат "6'4""
        match = re.match(r"(\d+)'(\d+)\"", height_str)
        if match:
            feet = int(match.group(1))
            inches = int(match.group(2))
            total_inches = feet * 12 + inches
            return int(total_inches * 2.54)  # Конвертируем в см
        
        return None
    
    def convert_weight_to_kg(self, weight_str: str) -> Optional[int]:
        """Конвертирует вес из фунтов в килограммы"""
        if not weight_str or weight_str == '--':
            return None
        
        # Парсим формат "248 lbs"
        match = re.match(r"(\d+)\s*lbs?", weight_str)
        if match:
            pounds = int(match.group(1))
            return int(pounds * 0.453592)  # Конвертируем в кг
        
        return None
    
    def parse_birth_date(self, birthdate_str: str) -> Optional[date]:
        """Парсит дату рождения"""
        if not birthdate_str or birthdate_str == '--':
            return None
        
        try:
            # Парсим формат "Jul 19, 1987"
            return datetime.strptime(birthdate_str, "%b %d, %Y").date()
        except:
            return None
    
    def get_or_create_weight_class(self, weight_class_en: str) -> WeightClass:
        """Получает или создает весовую категорию"""
        weight_class_ru = self.weight_class_mapping.get(weight_class_en, weight_class_en)
        
        # Ищем существующую категорию
        existing = self.db.query(WeightClass).filter(
            WeightClass.name_en == weight_class_en
        ).first()
        
        if existing:
            return existing
        
        # Создаем новую категорию
        weight_class = WeightClass(
            name_en=weight_class_en,
            name_ru=weight_class_ru,
            gender='male'  # По умолчанию, можно улучшить
        )
        self.db.add(weight_class)
        self.db.flush()
        return weight_class
    
    def import_fighter(self, fighter_name: str) -> Optional[Fighter]:
        """Импортирует бойца из UFC API"""
        print(f"🥊 Импорт бойца: {fighter_name}")
        
        try:
            # Получаем данные из UFC API
            fighter_data = get_fighter(fighter_name)
            
            if not fighter_data:
                print(f"❌ Не удалось получить данные для {fighter_name}")
                return None
            
            # Проверяем, существует ли уже боец
            existing = self.db.query(Fighter).filter(
                Fighter.name_en == fighter_data['name']
            ).first()
            
            if existing:
                print(f"✅ Боец {fighter_name} уже существует")
                return existing
            
            # Создаем нового бойца
            fighter = Fighter(
                name_en=fighter_data['name'],
                name_ru=fighter_data['name'],  # Пока используем английское имя
                nickname=fighter_data.get('nickname', ''),
                country=fighter_data.get('nationality', ''),
                height=self.convert_height_to_cm(fighter_data.get('height', '')),
                weight=self.convert_weight_to_kg(fighter_data.get('weight', '')),
                age=int(fighter_data.get('age', 0)) if fighter_data.get('age', '').isdigit() else None,
                birth_date=self.parse_birth_date(fighter_data.get('birthdate', '')),
                weight_class=fighter_data.get('weight_class', ''),
                career='UFC',
                win=int(fighter_data.get('wins', {}).get('total', 0)),
                lose=int(fighter_data.get('losses', {}).get('total', 0)),
                draw=0  # UFC API не предоставляет ничьи отдельно
            )
            
            self.db.add(fighter)
            self.db.flush()
            
            # Создаем боевой рекорд
            fight_record = FightRecord(
                fighter_id=fighter.id,
                wins=fighter.win,
                losses=fighter.lose,
                draws=fighter.draw
            )
            self.db.add(fight_record)
            
            # Создаем весовую категорию если нужно
            if fighter_data.get('weight_class'):
                weight_class = self.get_or_create_weight_class(fighter_data['weight_class'])
            
            print(f"✅ Боец {fighter_name} успешно импортирован")
            return fighter
            
        except Exception as e:
            print(f"❌ Ошибка импорта {fighter_name}: {e}")
            return None
    
    def import_top_fighters(self, count: int = 50) -> List[Fighter]:
        """Импортирует топ бойцов UFC"""
        print(f"🥊 Импорт топ-{count} бойцов UFC...")
        
        # Список известных топ бойцов UFC
        top_fighters = [
            'Jon Jones', 'Islam Makhachev', 'Alexander Volkanovski', 'Leon Edwards',
            'Kamaru Usman', 'Charles Oliveira', 'Dustin Poirier', 'Justin Gaethje',
            'Max Holloway', 'Yair Rodriguez', 'Aljamain Sterling', 'Petr Yan',
            'Sean O\'Malley', 'Brandon Moreno', 'Deiveson Figueiredo', 'Amanda Nunes',
            'Valentina Shevchenko', 'Rose Namajunas', 'Zhang Weili', 'Carla Esparza',
            'Conor McGregor', 'Khabib Nurmagomedov', 'Daniel Cormier', 'Stipe Miocic',
            'Francis Ngannou', 'Ciryl Gane', 'Derrick Lewis', 'Curtis Blaydes',
            'Jared Cannonier', 'Robert Whittaker', 'Israel Adesanya', 'Paulo Costa',
            'Colby Covington', 'Jorge Masvidal', 'Nate Diaz', 'Tony Ferguson',
            'Beneil Dariush', 'Rafael dos Anjos', 'Michael Chandler', 'Dan Hooker',
            'Calvin Kattar', 'Josh Emmett', 'Arnold Allen', 'Ilia Topuria',
            'Cory Sandhagen', 'Marlon Vera', 'Rob Font', 'Song Yadong',
            'Kai Kara-France', 'Askar Askarov', 'Alexandre Pantoja', 'Brandon Royval'
        ]
        
        imported_fighters = []
        
        for i, fighter_name in enumerate(top_fighters[:count], 1):
            print(f"\n[{i}/{count}] Импорт: {fighter_name}")
            fighter = self.import_fighter(fighter_name)
            if fighter:
                imported_fighters.append(fighter)
        
        self.db.commit()
        print(f"\n🎉 Импорт завершен! Импортировано {len(imported_fighters)} бойцов")
        return imported_fighters
    
    def close(self):
        """Закрывает соединение с БД"""
        self.db.close()


def main():
    """Главная функция для тестирования"""
    if not UFC_API_AVAILABLE:
        print("❌ UFC API не установлен. Установите: pip install ufc_api")
        return
    
    adapter = UFCAPIAdapter()
    
    try:
        # Тестируем импорт одного бойца
        print("🧪 Тестирование импорта одного бойца...")
        test_fighter = adapter.import_fighter('Jon Jones')
        
        if test_fighter:
            print("✅ Тест успешен!")
            
            # Спрашиваем пользователя о массовом импорте
            response = input("\n🤔 Хотите импортировать топ-20 бойцов? (y/n): ")
            if response.lower() == 'y':
                adapter.import_top_fighters(20)
        else:
            print("❌ Тест не прошел")
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        adapter.close()


if __name__ == "__main__":
    main()






