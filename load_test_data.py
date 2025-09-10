#!/usr/bin/env python3
"""
Простой скрипт для загрузки тестовых данных
"""

import sys
import os
from datetime import datetime, date

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.config import SessionLocal, init_database
from database.models import Fighter, WeightClass, Event, Fight, FightStats


def load_test_data():
    """Загружает тестовые данные в БД"""
    print("🔧 Инициализация базы данных...")
    init_database()
    
    print("📝 Загрузка тестовых данных...")
    db = SessionLocal()
    
    try:
        # Создаем весовые категории
        weight_classes = [
            {"name_ru": "Легкий вес", "name_en": "Lightweight", "gender": "male"},
            {"name_ru": "Полулегкий вес", "name_en": "Featherweight", "gender": "male"},
            {"name_ru": "Тяжелый вес", "name_en": "Heavyweight", "gender": "male"},
        ]
        
        for wc_data in weight_classes:
            wc = db.query(WeightClass).filter(WeightClass.name_ru == wc_data["name_ru"]).first()
            if not wc:
                wc = WeightClass(**wc_data)
                db.add(wc)
        
        db.flush()
        
        # Создаем события
        events_data = [
            {"name": "UFC 300", "date": date(2024, 4, 13), "location": "Las Vegas", "attendance": 20000},
            {"name": "UFC 299", "date": date(2024, 3, 9), "location": "Miami", "attendance": 18000},
            {"name": "UFC 298", "date": date(2024, 2, 17), "location": "Anaheim", "attendance": 16000},
        ]
        
        for event_data in events_data:
            event = db.query(Event).filter(Event.name == event_data["name"]).first()
            if not event:
                event = Event(**event_data)
                db.add(event)
        
        db.flush()
        
        # Создаем бойцов
        fighters_data = [
            {"name_ru": "Ислам Махачев", "name_en": "Islam Makhachev", "country": "Россия", "career": "UFC"},
            {"name_ru": "Александр Волкановски", "name_en": "Alexander Volkanovski", "country": "Австралия", "career": "UFC"},
            {"name_ru": "Макс Холловэй", "name_en": "Max Holloway", "country": "США", "career": "UFC"},
            {"name_ru": "Джон Джонс", "name_en": "Jon Jones", "country": "США", "career": "UFC"},
            {"name_ru": "Фрэнсис Нганну", "name_en": "Francis Ngannou", "country": "Камерун", "career": "UFC"},
        ]
        
        for fighter_data in fighters_data:
            fighter = db.query(Fighter).filter(Fighter.name_ru == fighter_data["name_ru"]).first()
            if not fighter:
                fighter = Fighter(**fighter_data)
                db.add(fighter)
        
        db.flush()
        
        # Создаем бои
        events = db.query(Event).all()
        fighters = db.query(Fighter).all()
        weight_classes = db.query(WeightClass).all()
        
        if events and fighters and weight_classes:
            fight = Fight(
                event_id=events[0].id,
                fighter1_id=fighters[0].id,
                fighter2_id=fighters[1].id,
                weight_class_id=weight_classes[0].id,
                scheduled_rounds=5,
                result="Decision",
                fight_date=events[0].date,
                is_title_fight=True,
                is_main_event=True
            )
            db.add(fight)
            db.flush()
            
            # Создаем статистику боя
            for round_num in range(1, 6):
                for fighter in [fighters[0], fighters[1]]:
                    stats = FightStats(
                        fight_id=fight.id,
                        fighter_id=fighter.id,
                        round_number=round_num,
                        significant_strikes_landed=20 + (round_num * 5),
                        significant_strikes_attempted=30 + (round_num * 8),
                        significant_strikes_rate=65.0 + (round_num * 2),
                        total_strikes_landed=25 + (round_num * 6),
                        total_strikes_attempted=35 + (round_num * 10),
                        takedown_successful=1 if round_num % 2 == 0 else 0,
                        takedown_attempted=2 if round_num % 2 == 0 else 1,
                        takedown_rate=50.0,
                        knockdowns=1 if round_num == 3 else 0,
                        submission_attempt=0,
                        reversals=0,
                        head_landed=15 + (round_num * 3),
                        head_attempted=20 + (round_num * 5),
                        body_landed=5 + round_num,
                        body_attempted=8 + (round_num * 2),
                        leg_landed=2 + round_num,
                        leg_attempted=3 + (round_num * 2),
                        distance_landed=18 + (round_num * 4),
                        distance_attempted=25 + (round_num * 6),
                        clinch_landed=2 + round_num,
                        clinch_attempted=3 + (round_num * 2),
                        ground_landed=0,
                        ground_attempted=0,
                        result="Decision" if round_num == 5 else None,
                        last_round=(round_num == 5),
                        time=f"5:00",
                        winner="W" if fighter.id == fighters[0].id else "L"
                    )
                    db.add(stats)
        
        db.commit()
        print("✅ Тестовые данные загружены успешно!")
        
        # Проверяем результат
        fighters_count = db.query(Fighter).count()
        events_count = db.query(Event).count()
        fights_count = db.query(Fight).count()
        stats_count = db.query(FightStats).count()
        
        print(f"📊 Загружено:")
        print(f"   Бойцов: {fighters_count}")
        print(f"   Событий: {events_count}")
        print(f"   Боев: {fights_count}")
        print(f"   Записей статистики: {stats_count}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при загрузке данных: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    load_test_data()
