#!/usr/bin/env python3
"""
Скрипт для просмотра данных в отладочной базе данных
"""

import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.models import (
    Fighter, WeightClass, Ranking, FightRecord, 
    Event, Fight, FightStats, UpcomingFight
)

def view_debug_data():
    """Показывает данные из отладочной базы"""
    
    # Подключаемся к БД
    engine = create_engine('sqlite:///ufc_ranker_v2.db', echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("🔍 Просмотр данных отладочной базы")
        print("="*60)
        
        # 1. Бойцы
        print("\n🥊 БОЙЦЫ:")
        print("-" * 30)
        fighters = session.query(Fighter).all()
        for fighter in fighters:
            print(f"  {fighter.id:2d}. {fighter.name_ru} ({fighter.nickname})")
            print(f"      Страна: {fighter.country} | Вес: {fighter.weight}кг | Рост: {fighter.height}см")
            print(f"      Рекорд: {fighter.win}-{fighter.lose}-{fighter.draw} | Категория: {fighter.weight_class}")
            print()
        
        # 2. Весовые категории
        print("\n⚖️ ВЕСОВЫЕ КАТЕГОРИИ:")
        print("-" * 30)
        weight_classes = session.query(WeightClass).all()
        for wc in weight_classes:
            print(f"  {wc.name_ru} ({wc.name_en})")
            print(f"      Вес: {wc.weight_min}-{wc.weight_max}кг | Пол: {wc.gender}")
            print()
        
        # 3. Рейтинги
        print("\n🏆 РЕЙТИНГИ:")
        print("-" * 30)
        rankings = session.query(Ranking).join(Fighter).join(WeightClass).all()
        for ranking in rankings:
            champion = "👑" if ranking.is_champion else "  "
            print(f"  {champion} #{ranking.rank_position:2d}. {ranking.fighter.name_ru}")
            print(f"      Категория: {ranking.weight_class.name_ru}")
            print()
        
        # 4. События
        print("\n🎪 СОБЫТИЯ:")
        print("-" * 30)
        events = session.query(Event).all()
        for event in events:
            status = "📅 Предстоящее" if event.is_upcoming else "✅ Прошедшее"
            print(f"  {event.name}")
            print(f"      Дата: {event.date} | Место: {event.location}")
            print(f"      Статус: {status}")
            print()
        
        # 5. Исторические бои
        print("\n🥊 ИСТОРИЧЕСКИЕ БОИ:")
        print("-" * 30)
        fights = session.query(Fight).join(Event).all()
        for fight in fights:
            title = "🏆 ТИТУЛЬНЫЙ" if fight.is_title_fight else "  Обычный"
            main = "⭐ ГЛАВНЫЙ" if fight.is_main_event else "  Обычный"
            print(f"  {fight.fighter1.name_ru} vs {fight.fighter2.name_ru}")
            print(f"      Событие: {fight.event.name}")
            print(f"      Результат: {fight.result} | Победитель: {fight.winner.name_ru if fight.winner else 'Не определен'}")
            print(f"      Тип: {title} | {main}")
            print()
        
        # 6. Предстоящие бои
        print("\n📅 ПРЕДСТОЯЩИЕ БОИ:")
        print("-" * 30)
        upcoming = session.query(UpcomingFight).all()
        for fight in upcoming:
            title = "🏆 ТИТУЛЬНЫЙ" if fight.is_title_fight else "  Обычный"
            main = "⭐ ГЛАВНЫЙ" if fight.is_main_event else "  Обычный"
            print(f"  {fight.fighter1.name_ru} vs {fight.fighter2.name_ru}")
            print(f"      Событие: {fight.event_name}")
            print(f"      Дата: {fight.event_date} | Место: {fight.location}")
            print(f"      Тип: {title} | {main}")
            print()
        
        # 7. Статистика боев (пример для первого боя)
        print("\n📈 СТАТИСТИКА БОЕВ (пример - Махачев vs Оливейра):")
        print("-" * 30)
        fight_stats = session.query(FightStats).join(Fight).filter(Fight.id == 1).all()
        for stat in fight_stats:
            print(f"  Раунд {stat.round_number}: {stat.fighter.name_ru}")
            print(f"      Значимые удары: {stat.significant_strikes_landed}/{stat.significant_strikes_attempted} ({stat.significant_strikes_rate}%)")
            print(f"      Тейкдауны: {stat.takedown_successful}/{stat.takedown_attempted} ({stat.takedown_rate}%)")
            print(f"      Удары в голову: {stat.head_landed}/{stat.head_attempted}")
            print(f"      Результат раунда: {stat.winner}")
            print()
        
        # Общая статистика
        print("\n📊 ОБЩАЯ СТАТИСТИКА:")
        print("-" * 30)
        print(f"  Бойцов: {session.query(Fighter).count()}")
        print(f"  Весовых категорий: {session.query(WeightClass).count()}")
        print(f"  Рейтингов: {session.query(Ranking).count()}")
        print(f"  Событий: {session.query(Event).count()}")
        print(f"  Исторических боев: {session.query(Fight).count()}")
        print(f"  Предстоящих боев: {session.query(UpcomingFight).count()}")
        print(f"  Записей статистики: {session.query(FightStats).count()}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        session.close()

def main():
    """Главная функция"""
    view_debug_data()

if __name__ == "__main__":
    main()





