#!/usr/bin/env python3
"""
Создание тестовой базы данных с готовыми данными для отладки
"""

import sys
import os
from datetime import date, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.models import Base, Fighter, WeightClass, Ranking, FightRecord

def create_test_database():
    """Создает тестовую базу данных с данными"""
    
    # Создаем тестовую базу данных
    engine = create_engine('sqlite:///test_ufc_ranker.db', echo=False)
    
    # Создаем все таблицы
    Base.metadata.create_all(engine)
    
    # Создаем сессию
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Создаем весовые категории
        weight_classes = [
            WeightClass(
                name_ru="Легкий вес",
                name_en="Lightweight",
                weight_min=66,
                weight_max=70,
                gender="male"
            ),
            WeightClass(
                name_ru="Полулегкий вес",
                name_en="Featherweight", 
                weight_min=61,
                weight_max=66,
                gender="male"
            ),
            WeightClass(
                name_ru="Полутяжёлый вес",
                name_en="Light Heavyweight",
                weight_min=84,
                weight_max=93,
                gender="male"
            ),
            WeightClass(
                name_ru="Тяжёлый вес",
                name_en="Heavyweight",
                weight_min=93,
                weight_max=120,
                gender="male"
            ),
            WeightClass(
                name_ru="Женский легчайший вес",
                name_en="Women's Bantamweight",
                weight_min=54,
                weight_max=61,
                gender="female"
            )
        ]
        
        for wc in weight_classes:
            session.add(wc)
        
        session.commit()
        print("✅ Весовые категории созданы")
        
        # Создаем бойцов
        fighters = [
            Fighter(
                name_ru="Ислам Махачев",
                name_en="Islam Makhachev",
                nickname="The Eagle",
                country="Россия",
                country_flag_url="https://flagcdn.com/w40/ru.png",
                image_url="https://via.placeholder.com/300x400/1E3A8A/FFFFFF?text=Ислам+Махачев",
                height=178,
                weight=70,
                reach=180,
                age=32,
                birth_date=date(1991, 10, 27),
                weight_class="Легкий вес",
                win=25,
                draw=0,
                lose=1,
                career="UFC"
            ),
            Fighter(
                name_ru="Александр Волкановски",
                name_en="Alexander Volkanovski",
                nickname="The Great",
                country="Австралия",
                country_flag_url="https://flagcdn.com/w40/au.png",
                image_url="https://via.placeholder.com/300x400/FFD700/000000?text=Александр+Волкановски",
                height=168,
                weight=66,
                reach=183,
                age=35,
                birth_date=date(1988, 9, 29),
                weight_class="Полулегкий вес",
                win=26,
                draw=0,
                lose=3,
                career="UFC"
            ),
            Fighter(
                name_ru="Джон Джонс",
                name_en="Jon Jones",
                nickname="Bones",
                country="США",
                country_flag_url="https://flagcdn.com/w40/us.png",
                image_url="https://via.placeholder.com/300x400/C8102E/FFFFFF?text=Джон+Джонс",
                height=193,
                weight=93,
                reach=215,
                age=36,
                birth_date=date(1987, 7, 19),
                weight_class="Полутяжёлый вес",
                win=27,
                draw=0,
                lose=1,
                career="UFC"
            ),
            Fighter(
                name_ru="Макс Холловэй",
                name_en="Max Holloway",
                nickname="Blessed",
                country="США",
                country_flag_url="https://flagcdn.com/w40/us.png",
                image_url="https://via.placeholder.com/300x400/1E3A8A/FFFFFF?text=Макс+Холловэй",
                height=180,
                weight=66,
                reach=175,
                age=32,
                birth_date=date(1991, 12, 4),
                weight_class="Полулегкий вес",
                win=25,
                draw=0,
                lose=7,
                career="UFC"
            ),
            Fighter(
                name_ru="Фрэнсис Нганну",
                name_en="Francis Ngannou",
                nickname="The Predator",
                country="Камерун",
                country_flag_url="https://flagcdn.com/w40/cm.png",
                image_url="https://via.placeholder.com/300x400/000000/FFFFFF?text=Фрэнсис+Нганну",
                height=193,
                weight=120,
                reach=211,
                age=37,
                birth_date=date(1986, 9, 5),
                weight_class="Тяжёлый вес",
                win=17,
                draw=0,
                lose=3,
                career="UFC"
            ),
            Fighter(
                name_ru="Аманда Нунес",
                name_en="Amanda Nunes",
                nickname="The Lioness",
                country="Бразилия",
                country_flag_url="https://flagcdn.com/w40/br.png",
                image_url="https://via.placeholder.com/300x400/FFD700/000000?text=Аманда+Нунес",
                height=170,
                weight=61,
                reach=180,
                age=35,
                birth_date=date(1988, 5, 30),
                weight_class="Женский легчайший вес",
                win=22,
                draw=0,
                lose=5,
                career="UFC"
            ),
            Fighter(
                name_ru="Конор Макгрегор",
                name_en="Conor McGregor",
                nickname="The Notorious",
                country="Ирландия",
                country_flag_url="https://flagcdn.com/w40/ie.png",
                image_url="https://via.placeholder.com/300x400/FFD700/000000?text=Конор+Макгрегор",
                height=175,
                weight=70,
                reach=188,
                age=35,
                birth_date=date(1988, 7, 14),
                weight_class="Легкий вес",
                win=22,
                draw=0,
                lose=6,
                career="UFC"
            ),
            Fighter(
                name_ru="Хабиб Нурмагомедов",
                name_en="Khabib Nurmagomedov",
                nickname="The Eagle",
                country="Россия",
                country_flag_url="https://flagcdn.com/w40/ru.png",
                image_url="https://via.placeholder.com/300x400/1E3A8A/FFFFFF?text=Хабиб+Нурмагомедов",
                height=175,
                weight=70,
                reach=178,
                age=35,
                birth_date=date(1988, 9, 20),
                weight_class="Легкий вес",
                win=29,
                draw=0,
                lose=0,
                career="UFC"
            )
        ]
        
        for fighter in fighters:
            session.add(fighter)
        
        session.commit()
        print("✅ Бойцы созданы")
        
        # Создаем рейтинги
        # Получаем созданные объекты
        lightweight = session.query(WeightClass).filter(WeightClass.name_ru == "Легкий вес").first()
        featherweight = session.query(WeightClass).filter(WeightClass.name_ru == "Полулегкий вес").first()
        light_heavyweight = session.query(WeightClass).filter(WeightClass.name_ru == "Полутяжёлый вес").first()
        heavyweight = session.query(WeightClass).filter(WeightClass.name_ru == "Тяжёлый вес").first()
        womens_bantamweight = session.query(WeightClass).filter(WeightClass.name_ru == "Женский легчайший вес").first()
        
        # Создаем рейтинги
        rankings = [
            # Легкий вес
            Ranking(fighter_id=1, weight_class_id=lightweight.id, rank_position=1, is_champion=True),  # Ислам Махачев
            Ranking(fighter_id=7, weight_class_id=lightweight.id, rank_position=2, is_champion=False), # Конор Макгрегор
            Ranking(fighter_id=8, weight_class_id=lightweight.id, rank_position=3, is_champion=False), # Хабиб Нурмагомедов
            
            # Полулегкий вес
            Ranking(fighter_id=2, weight_class_id=featherweight.id, rank_position=1, is_champion=True),  # Александр Волкановски
            Ranking(fighter_id=4, weight_class_id=featherweight.id, rank_position=2, is_champion=False), # Макс Холловэй
            
            # Полутяжёлый вес
            Ranking(fighter_id=3, weight_class_id=light_heavyweight.id, rank_position=1, is_champion=True), # Джон Джонс
            
            # Тяжёлый вес
            Ranking(fighter_id=5, weight_class_id=heavyweight.id, rank_position=1, is_champion=True), # Фрэнсис Нганну
            
            # Женский легчайший вес
            Ranking(fighter_id=6, weight_class_id=womens_bantamweight.id, rank_position=1, is_champion=True), # Аманда Нунес
        ]
        
        for ranking in rankings:
            session.add(ranking)
        
        session.commit()
        print("✅ Рейтинги созданы")
        
        # Создаем боевые рекорды
        for fighter in fighters:
            record = FightRecord(
                fighter_id=fighter.id,
                wins=fighter.win,
                losses=fighter.lose,
                draws=fighter.draw
            )
            session.add(record)
        
        session.commit()
        print("✅ Боевые рекорды созданы")
        
        # Выводим статистику
        fighters_count = session.query(Fighter).count()
        weight_classes_count = session.query(WeightClass).count()
        rankings_count = session.query(Ranking).count()
        records_count = session.query(FightRecord).count()
        
        print("\n" + "="*50)
        print("📊 Статистика тестовой базы данных:")
        print("="*50)
        print(f"🥊 Бойцов: {fighters_count}")
        print(f"⚖️ Весовых категорий: {weight_classes_count}")
        print(f"🏆 Рейтингов: {rankings_count}")
        print(f"📋 Боевых рекордов: {records_count}")
        print("="*50)
        print("✅ Тестовая база данных создана: test_ufc_ranker.db")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        session.rollback()
        raise
    finally:
        session.close()

def main():
    """Главная функция"""
    print("🗄️ Создание тестовой базы данных")
    print("="*50)
    
    try:
        create_test_database()
    except Exception as e:
        print(f"❌ Ошибка создания базы данных: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Тестовая база данных готова для отладки!")
    else:
        print("\n💥 Не удалось создать тестовую базу данных")

