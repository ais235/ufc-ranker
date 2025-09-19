#!/usr/bin/env python3
"""
Скрипт для создания тестовых данных бойцов в базе данных
"""

import sys
import os
from datetime import date, datetime

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.config import get_db, init_database
from database.models import Fighter, WeightClass, Ranking, FightRecord
from sqlalchemy.orm import Session

def create_test_fighters(db: Session):
    """Создает тестовых бойцов"""
    
    # Создаем весовые категории
    weight_classes = [
        {"name_ru": "Легкий вес", "name_en": "Lightweight", "weight_min": 66, "weight_max": 70, "gender": "male"},
        {"name_ru": "Полулегкий вес", "name_en": "Featherweight", "weight_min": 61, "weight_max": 66, "gender": "male"},
        {"name_ru": "Полутяжёлый вес", "name_en": "Light Heavyweight", "weight_min": 84, "weight_max": 93, "gender": "male"},
        {"name_ru": "Тяжёлый вес", "name_en": "Heavyweight", "weight_min": 93, "weight_max": 120, "gender": "male"},
    ]
    
    for wc_data in weight_classes:
        existing = db.query(WeightClass).filter(WeightClass.name_ru == wc_data["name_ru"]).first()
        if not existing:
            weight_class = WeightClass(**wc_data)
            db.add(weight_class)
    
    db.commit()
    
    # Получаем созданные весовые категории
    lightweight = db.query(WeightClass).filter(WeightClass.name_ru == "Легкий вес").first()
    featherweight = db.query(WeightClass).filter(WeightClass.name_ru == "Полулегкий вес").first()
    light_heavyweight = db.query(WeightClass).filter(WeightClass.name_ru == "Полутяжёлый вес").first()
    heavyweight = db.query(WeightClass).filter(WeightClass.name_ru == "Тяжёлый вес").first()
    
    # Тестовые бойцы
    test_fighters = [
        {
            "name_ru": "Ислам Махачев",
            "name_en": "Islam Makhachev",
            "nickname": "The Eagle",
            "country": "Россия",
            "height": 178,
            "weight": 70,
            "reach": 180,
            "age": 32,
            "birth_date": date(1991, 10, 27),
            "weight_class": "Легкий вес",
            "win": 25,
            "draw": 0,
            "lose": 1,
            "career": "UFC",
            "image_url": "https://via.placeholder.com/300x400/1E3A8A/FFFFFF?text=Ислам+Махачев"
        },
        {
            "name_ru": "Александр Волкановски",
            "name_en": "Alexander Volkanovski",
            "nickname": "The Great",
            "country": "Австралия",
            "height": 168,
            "weight": 66,
            "reach": 183,
            "age": 35,
            "birth_date": date(1988, 9, 29),
            "weight_class": "Полулегкий вес",
            "win": 26,
            "draw": 0,
            "lose": 3,
            "career": "UFC",
            "image_url": "https://via.placeholder.com/300x400/FFD700/000000?text=Александр+Волкановски"
        },
        {
            "name_ru": "Джон Джонс",
            "name_en": "Jon Jones",
            "nickname": "Bones",
            "country": "США",
            "height": 193,
            "weight": 93,
            "reach": 215,
            "age": 36,
            "birth_date": date(1987, 7, 19),
            "weight_class": "Полутяжёлый вес",
            "win": 27,
            "draw": 0,
            "lose": 1,
            "career": "UFC",
            "image_url": "https://via.placeholder.com/300x400/C8102E/FFFFFF?text=Джон+Джонс"
        },
        {
            "name_ru": "Макс Холловэй",
            "name_en": "Max Holloway",
            "nickname": "Blessed",
            "country": "США",
            "height": 180,
            "weight": 66,
            "reach": 175,
            "age": 32,
            "birth_date": date(1991, 12, 4),
            "weight_class": "Полулегкий вес",
            "win": 25,
            "draw": 0,
            "lose": 7,
            "career": "UFC",
            "image_url": "https://via.placeholder.com/300x400/1E3A8A/FFFFFF?text=Макс+Холловэй"
        },
        {
            "name_ru": "Фрэнсис Нганну",
            "name_en": "Francis Ngannou",
            "nickname": "The Predator",
            "country": "Камерун",
            "height": 193,
            "weight": 120,
            "reach": 211,
            "age": 37,
            "birth_date": date(1986, 9, 5),
            "weight_class": "Тяжёлый вес",
            "win": 17,
            "draw": 0,
            "lose": 3,
            "career": "UFC",
            "image_url": "https://via.placeholder.com/300x400/000000/FFFFFF?text=Фрэнсис+Нганну"
        }
    ]
    
    # Создаем бойцов
    created_fighters = []
    for fighter_data in test_fighters:
        existing = db.query(Fighter).filter(Fighter.name_ru == fighter_data["name_ru"]).first()
        if not existing:
            fighter = Fighter(**fighter_data)
            db.add(fighter)
            created_fighters.append(fighter)
        else:
            created_fighters.append(existing)
    
    db.commit()
    
    # Создаем рейтинги
    rankings_data = [
        {"fighter": "Ислам Махачев", "weight_class": "Легкий вес", "rank_position": 1, "is_champion": True},
        {"fighter": "Александр Волкановски", "weight_class": "Полулегкий вес", "rank_position": 1, "is_champion": True},
        {"fighter": "Джон Джонс", "weight_class": "Полутяжёлый вес", "rank_position": 1, "is_champion": True},
        {"fighter": "Макс Холловэй", "weight_class": "Полулегкий вес", "rank_position": 2, "is_champion": False},
        {"fighter": "Фрэнсис Нганну", "weight_class": "Тяжёлый вес", "rank_position": 1, "is_champion": True},
    ]
    
    for rank_data in rankings_data:
        fighter = db.query(Fighter).filter(Fighter.name_ru == rank_data["fighter"]).first()
        weight_class = db.query(WeightClass).filter(WeightClass.name_ru == rank_data["weight_class"]).first()
        
        if fighter and weight_class:
            existing_ranking = db.query(Ranking).filter(
                Ranking.fighter_id == fighter.id,
                Ranking.weight_class_id == weight_class.id
            ).first()
            
            if not existing_ranking:
                ranking = Ranking(
                    fighter_id=fighter.id,
                    weight_class_id=weight_class.id,
                    rank_position=rank_data["rank_position"],
                    is_champion=rank_data["is_champion"]
                )
                db.add(ranking)
    
    # Создаем боевые рекорды
    for fighter in created_fighters:
        existing_record = db.query(FightRecord).filter(FightRecord.fighter_id == fighter.id).first()
        if not existing_record:
            record = FightRecord(
                fighter_id=fighter.id,
                wins=fighter.win,
                losses=fighter.lose,
                draws=fighter.draw
            )
            db.add(record)
    
    db.commit()
    print("✅ Тестовые данные созданы успешно!")
    
    # Выводим статистику
    fighters_count = db.query(Fighter).count()
    weight_classes_count = db.query(WeightClass).count()
    rankings_count = db.query(Ranking).count()
    
    print(f"📊 Статистика:")
    print(f"   Бойцов: {fighters_count}")
    print(f"   Весовых категорий: {weight_classes_count}")
    print(f"   Рейтингов: {rankings_count}")

def main():
    """Главная функция"""
    print("🥊 Создание тестовых данных бойцов")
    print("=" * 50)
    
    # Инициализируем базу данных
    init_database()
    
    # Получаем сессию базы данных
    db = next(get_db())
    
    try:
        create_test_fighters(db)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()

