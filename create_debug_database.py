#!/usr/bin/env python3
"""
Создание расширенной тестовой базы данных для отладки страницы бойца
Включает детальную статистику боев, события, предстоящие бои и многое другое
"""

import sys
import os
from datetime import date, datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.models import (
    Base, Fighter, WeightClass, Ranking, FightRecord, 
    Event, Fight, FightStats, UpcomingFight
)

def create_debug_database():
    """Создает расширенную тестовую базу данных для отладки"""
    
    # Создаем тестовую базу данных
    engine = create_engine('sqlite:///debug_ufc_ranker.db', echo=False)
    
    # Создаем все таблицы
    Base.metadata.create_all(engine)
    
    # Создаем сессию
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("🗄️ Создание расширенной тестовой базы данных...")
        print("="*60)
        
        # 1. Создаем весовые категории
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
            ),
            WeightClass(
                name_ru="Средний вес",
                name_en="Middleweight",
                weight_min=77,
                weight_max=84,
                gender="male"
            ),
            WeightClass(
                name_ru="Полусредний вес",
                name_en="Welterweight",
                weight_min=70,
                weight_max=77,
                gender="male"
            )
        ]
        
        for wc in weight_classes:
            session.add(wc)
        
        session.commit()
        print("✅ Весовые категории созданы")
        
        # 2. Создаем расширенный список бойцов
        fighters = [
            # Легкий вес
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
                name_ru="Чарльз Оливейра",
                name_en="Charles Oliveira",
                nickname="Do Bronx",
                country="Бразилия",
                country_flag_url="https://flagcdn.com/w40/br.png",
                image_url="https://via.placeholder.com/300x400/FFD700/000000?text=Чарльз+Оливейра",
                height=178,
                weight=70,
                reach=188,
                age=34,
                birth_date=date(1989, 10, 17),
                weight_class="Легкий вес",
                win=34,
                draw=0,
                lose=9,
                career="UFC"
            ),
            Fighter(
                name_ru="Джастин Гейджи",
                name_en="Justin Gaethje",
                nickname="The Highlight",
                country="США",
                country_flag_url="https://flagcdn.com/w40/us.png",
                image_url="https://via.placeholder.com/300x400/C8102E/FFFFFF?text=Джастин+Гейджи",
                height=180,
                weight=70,
                reach=180,
                age=35,
                birth_date=date(1988, 11, 14),
                weight_class="Легкий вес",
                win=25,
                draw=0,
                lose=4,
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
            
            # Полулегкий вес
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
                name_ru="Илья Топурия",
                name_en="Ilia Topuria",
                nickname="El Matador",
                country="Грузия",
                country_flag_url="https://flagcdn.com/w40/ge.png",
                image_url="https://via.placeholder.com/300x400/FF0000/FFFFFF?text=Илья+Топурия",
                height=170,
                weight=66,
                reach=175,
                age=27,
                birth_date=date(1997, 1, 21),
                weight_class="Полулегкий вес",
                win=15,
                draw=0,
                lose=0,
                career="UFC"
            ),
            
            # Полутяжёлый вес
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
                name_ru="Александр Ракич",
                name_en="Aleksandar Rakić",
                nickname="Rocket",
                country="Австрия",
                country_flag_url="https://flagcdn.com/w40/at.png",
                image_url="https://via.placeholder.com/300x400/FF0000/FFFFFF?text=Александр+Ракич",
                height=196,
                weight=93,
                reach=198,
                age=32,
                birth_date=date(1992, 2, 6),
                weight_class="Полутяжёлый вес",
                win=14,
                draw=0,
                lose=3,
                career="UFC"
            ),
            
            # Тяжёлый вес
            Fighter(
                name_ru="Том Аспиналл",
                name_en="Tom Aspinall",
                nickname="The Grim Reaper",
                country="Великобритания",
                country_flag_url="https://flagcdn.com/w40/gb.png",
                image_url="https://via.placeholder.com/300x400/1E3A8A/FFFFFF?text=Том+Аспиналл",
                height=196,
                weight=120,
                reach=203,
                age=31,
                birth_date=date(1993, 4, 11),
                weight_class="Тяжёлый вес",
                win=14,
                draw=0,
                lose=3,
                career="UFC"
            ),
            Fighter(
                name_ru="Сергей Павлович",
                name_en="Sergei Pavlovich",
                nickname="The Polar Bear",
                country="Россия",
                country_flag_url="https://flagcdn.com/w40/ru.png",
                image_url="https://via.placeholder.com/300x400/1E3A8A/FFFFFF?text=Сергей+Павлович",
                height=191,
                weight=120,
                reach=213,
                age=32,
                birth_date=date(1992, 5, 13),
                weight_class="Тяжёлый вес",
                win=18,
                draw=0,
                lose=2,
                career="UFC"
            ),
            
            # Женский легчайший вес
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
                name_ru="Валентина Шевченко",
                name_en="Valentina Shevchenko",
                nickname="Bullet",
                country="Кыргызстан",
                country_flag_url="https://flagcdn.com/w40/kg.png",
                image_url="https://via.placeholder.com/300x400/FF0000/FFFFFF?text=Валентина+Шевченко",
                height=165,
                weight=57,
                reach=170,
                age=36,
                birth_date=date(1988, 3, 7),
                weight_class="Женский легчайший вес",
                win=23,
                draw=0,
                lose=4,
                career="UFC"
            ),
            
            # Средний вес
            Fighter(
                name_ru="Исраэль Адесанья",
                name_en="Israel Adesanya",
                nickname="The Last Stylebender",
                country="Новая Зеландия",
                country_flag_url="https://flagcdn.com/w40/nz.png",
                image_url="https://via.placeholder.com/300x400/000000/FFFFFF?text=Исраэль+Адесанья",
                height=193,
                weight=84,
                reach=203,
                age=35,
                birth_date=date(1989, 7, 22),
                weight_class="Средний вес",
                win=24,
                draw=0,
                lose=3,
                career="UFC"
            ),
            Fighter(
                name_ru="Шон Стрикленд",
                name_en="Sean Strickland",
                nickname="Tarzan",
                country="США",
                country_flag_url="https://flagcdn.com/w40/us.png",
                image_url="https://via.placeholder.com/300x400/C8102E/FFFFFF?text=Шон+Стрикленд",
                height=185,
                weight=84,
                reach=193,
                age=33,
                birth_date=date(1991, 2, 27),
                weight_class="Средний вес",
                win=28,
                draw=0,
                lose=5,
                career="UFC"
            ),
            
            # Полусредний вес
            Fighter(
                name_ru="Леон Эдвардс",
                name_en="Leon Edwards",
                nickname="Rocky",
                country="Великобритания",
                country_flag_url="https://flagcdn.com/w40/gb.png",
                image_url="https://via.placeholder.com/300x400/1E3A8A/FFFFFF?text=Леон+Эдвардс",
                height=183,
                weight=77,
                reach=188,
                age=32,
                birth_date=date(1991, 8, 25),
                weight_class="Полусредний вес",
                win=22,
                draw=0,
                lose=3,
                career="UFC"
            ),
            Fighter(
                name_ru="Камзат Чимаев",
                name_en="Khamzat Chimaev",
                nickname="Borz",
                country="Швеция",
                country_flag_url="https://flagcdn.com/w40/se.png",
                image_url="https://via.placeholder.com/300x400/FFD700/000000?text=Камзат+Чимаев",
                height=185,
                weight=77,
                reach=190,
                age=30,
                birth_date=date(1994, 5, 1),
                weight_class="Полусредний вес",
                win=13,
                draw=0,
                lose=0,
                career="UFC"
            )
        ]
        
        for fighter in fighters:
            session.add(fighter)
        
        session.commit()
        print("✅ Бойцы созданы")
        
        # 3. Создаем рейтинги
        lightweight = session.query(WeightClass).filter(WeightClass.name_ru == "Легкий вес").first()
        featherweight = session.query(WeightClass).filter(WeightClass.name_ru == "Полулегкий вес").first()
        light_heavyweight = session.query(WeightClass).filter(WeightClass.name_ru == "Полутяжёлый вес").first()
        heavyweight = session.query(WeightClass).filter(WeightClass.name_ru == "Тяжёлый вес").first()
        womens_bantamweight = session.query(WeightClass).filter(WeightClass.name_ru == "Женский легчайший вес").first()
        middleweight = session.query(WeightClass).filter(WeightClass.name_ru == "Средний вес").first()
        welterweight = session.query(WeightClass).filter(WeightClass.name_ru == "Полусредний вес").first()
        
        rankings = [
            # Легкий вес
            Ranking(fighter_id=1, weight_class_id=lightweight.id, rank_position=1, is_champion=True),  # Ислам Махачев
            Ranking(fighter_id=2, weight_class_id=lightweight.id, rank_position=2, is_champion=False), # Чарльз Оливейра
            Ranking(fighter_id=3, weight_class_id=lightweight.id, rank_position=3, is_champion=False), # Джастин Гейджи
            Ranking(fighter_id=4, weight_class_id=lightweight.id, rank_position=4, is_champion=False), # Конор Макгрегор
            
            # Полулегкий вес
            Ranking(fighter_id=5, weight_class_id=featherweight.id, rank_position=1, is_champion=True),  # Александр Волкановски
            Ranking(fighter_id=6, weight_class_id=featherweight.id, rank_position=2, is_champion=False), # Макс Холловэй
            Ranking(fighter_id=7, weight_class_id=featherweight.id, rank_position=3, is_champion=False), # Илья Топурия
            
            # Полутяжёлый вес
            Ranking(fighter_id=8, weight_class_id=light_heavyweight.id, rank_position=1, is_champion=True), # Джон Джонс
            Ranking(fighter_id=9, weight_class_id=light_heavyweight.id, rank_position=2, is_champion=False), # Александр Ракич
            
            # Тяжёлый вес
            Ranking(fighter_id=10, weight_class_id=heavyweight.id, rank_position=1, is_champion=True), # Том Аспиналл
            Ranking(fighter_id=11, weight_class_id=heavyweight.id, rank_position=2, is_champion=False), # Сергей Павлович
            
            # Женский легчайший вес
            Ranking(fighter_id=12, weight_class_id=womens_bantamweight.id, rank_position=1, is_champion=True), # Аманда Нунес
            Ranking(fighter_id=13, weight_class_id=womens_bantamweight.id, rank_position=2, is_champion=False), # Валентина Шевченко
            
            # Средний вес
            Ranking(fighter_id=14, weight_class_id=middleweight.id, rank_position=1, is_champion=True), # Исраэль Адесанья
            Ranking(fighter_id=15, weight_class_id=middleweight.id, rank_position=2, is_champion=False), # Шон Стрикленд
            
            # Полусредний вес
            Ranking(fighter_id=16, weight_class_id=welterweight.id, rank_position=1, is_champion=True), # Леон Эдвардс
            Ranking(fighter_id=17, weight_class_id=welterweight.id, rank_position=2, is_champion=False), # Камзат Чимаев
        ]
        
        for ranking in rankings:
            session.add(ranking)
        
        session.commit()
        print("✅ Рейтинги созданы")
        
        # 4. Создаем боевые рекорды
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
        
        # 5. Создаем события UFC
        events = [
            Event(
                name="UFC 300: Pereira vs Hill",
                date=date(2024, 4, 13),
                location="Лас-Вегас, США",
                venue="T-Mobile Arena",
                description="Грандиозное событие UFC 300 с титульными боями",
                image_url="https://via.placeholder.com/800x400/1E3A8A/FFFFFF?text=UFC+300",
                is_upcoming=False,
                attendance=20000
            ),
            Event(
                name="UFC 301: Holloway vs Allen",
                date=date(2024, 5, 4),
                location="Рио-де-Жанейро, Бразилия",
                venue="Farmasi Arena",
                description="UFC возвращается в Бразилию",
                image_url="https://via.placeholder.com/800x400/FFD700/000000?text=UFC+301",
                is_upcoming=False,
                attendance=15000
            ),
            Event(
                name="UFC 302: Makhachev vs Oliveira 2",
                date=date(2024, 6, 1),
                location="Ньюарк, США",
                venue="Prudential Center",
                description="Рематч за титул легкого веса",
                image_url="https://via.placeholder.com/800x400/1E3A8A/FFFFFF?text=UFC+302",
                is_upcoming=False,
                attendance=18000
            ),
            Event(
                name="UFC 303: McGregor vs Chandler",
                date=date(2024, 6, 29),
                location="Лас-Вегас, США",
                venue="T-Mobile Arena",
                description="Возвращение Конора Макгрегора",
                image_url="https://via.placeholder.com/800x400/FFD700/000000?text=UFC+303",
                is_upcoming=True,
                attendance=20000
            ),
            Event(
                name="UFC 304: Edwards vs Chimaev",
                date=date(2024, 7, 27),
                location="Манчестер, Великобритания",
                venue="Manchester Arena",
                description="Титульный бой в полусреднем весе",
                image_url="https://via.placeholder.com/800x400/1E3A8A/FFFFFF?text=UFC+304",
                is_upcoming=True,
                attendance=21000
            )
        ]
        
        for event in events:
            session.add(event)
        
        session.commit()
        print("✅ События созданы")
        
        # 6. Создаем исторические бои
        ufc300 = session.query(Event).filter(Event.name == "UFC 300: Pereira vs Hill").first()
        ufc301 = session.query(Event).filter(Event.name == "UFC 301: Holloway vs Allen").first()
        ufc302 = session.query(Event).filter(Event.name == "UFC 302: Makhachev vs Oliveira 2").first()
        
        fights = [
            # UFC 300
            Fight(
                event_id=ufc300.id,
                fighter1_id=1,  # Ислам Махачев
                fighter2_id=2,  # Чарльз Оливейра
                weight_class_id=lightweight.id,
                scheduled_rounds=5,
                result="Decision",
                winner_id=1,
                fight_date=date(2024, 4, 13),
                is_title_fight=True,
                is_main_event=True
            ),
            Fight(
                event_id=ufc300.id,
                fighter1_id=5,  # Александр Волкановски
                fighter2_id=6,  # Макс Холловэй
                weight_class_id=featherweight.id,
                scheduled_rounds=5,
                result="KO",
                winner_id=5,
                fight_date=date(2024, 4, 13),
                is_title_fight=True,
                is_main_event=False
            ),
            
            # UFC 301
            Fight(
                event_id=ufc301.id,
                fighter1_id=6,  # Макс Холловэй
                fighter2_id=7,  # Илья Топурия
                weight_class_id=featherweight.id,
                scheduled_rounds=3,
                result="Decision",
                winner_id=7,
                fight_date=date(2024, 5, 4),
                is_title_fight=False,
                is_main_event=True
            ),
            
            # UFC 302
            Fight(
                event_id=ufc302.id,
                fighter1_id=1,  # Ислам Махачев
                fighter2_id=2,  # Чарльз Оливейра
                weight_class_id=lightweight.id,
                scheduled_rounds=5,
                result="Submission",
                winner_id=1,
                fight_date=date(2024, 6, 1),
                is_title_fight=True,
                is_main_event=True
            )
        ]
        
        for fight in fights:
            session.add(fight)
        
        session.commit()
        print("✅ Исторические бои созданы")
        
        # 7. Создаем детальную статистику боев
        fight1 = session.query(Fight).filter(Fight.event_id == ufc300.id, Fight.fighter1_id == 1).first()
        fight2 = session.query(Fight).filter(Fight.event_id == ufc300.id, Fight.fighter1_id == 5).first()
        
        # Статистика для боя Махачев vs Оливейра (UFC 300)
        fight_stats = [
            # Ислам Махачев - Раунд 1
            FightStats(
                fight_id=fight1.id,
                fighter_id=1,
                round_number=1,
                knockdowns=0,
                significant_strikes_landed=15,
                significant_strikes_attempted=25,
                significant_strikes_rate=60.0,
                total_strikes_landed=18,
                total_strikes_attempted=30,
                takedown_successful=2,
                takedown_attempted=3,
                takedown_rate=66.7,
                submission_attempt=1,
                reversals=0,
                head_landed=8,
                head_attempted=12,
                body_landed=5,
                body_attempted=8,
                leg_landed=2,
                leg_attempted=5,
                distance_landed=12,
                distance_attempted=18,
                clinch_landed=3,
                clinch_attempted=5,
                ground_landed=0,
                ground_attempted=0,
                result="Decision",
                last_round=False,
                time="5:00",
                winner="W"
            ),
            # Ислам Махачев - Раунд 2
            FightStats(
                fight_id=fight1.id,
                fighter_id=1,
                round_number=2,
                knockdowns=1,
                significant_strikes_landed=22,
                significant_strikes_attempted=35,
                significant_strikes_rate=62.9,
                total_strikes_landed=28,
                total_strikes_attempted=42,
                takedown_successful=1,
                takedown_attempted=2,
                takedown_rate=50.0,
                submission_attempt=0,
                reversals=0,
                head_landed=12,
                head_attempted=18,
                body_landed=7,
                body_attempted=12,
                leg_landed=3,
                leg_attempted=5,
                distance_landed=18,
                distance_attempted=28,
                clinch_landed=4,
                clinch_attempted=7,
                ground_landed=0,
                ground_attempted=0,
                result="Decision",
                last_round=False,
                time="5:00",
                winner="W"
            ),
            # Ислам Махачев - Раунд 3
            FightStats(
                fight_id=fight1.id,
                fighter_id=1,
                round_number=3,
                knockdowns=0,
                significant_strikes_landed=18,
                significant_strikes_attempted=28,
                significant_strikes_rate=64.3,
                total_strikes_landed=24,
                total_strikes_attempted=35,
                takedown_successful=3,
                takedown_attempted=4,
                takedown_rate=75.0,
                submission_attempt=2,
                reversals=0,
                head_landed=10,
                head_attempted=15,
                body_landed=6,
                body_attempted=9,
                leg_landed=2,
                leg_attempted=4,
                distance_landed=14,
                distance_attempted=22,
                clinch_landed=2,
                clinch_attempted=3,
                ground_landed=2,
                ground_attempted=3,
                result="Decision",
                last_round=False,
                time="5:00",
                winner="W"
            ),
            # Ислам Махачев - Раунд 4
            FightStats(
                fight_id=fight1.id,
                fighter_id=1,
                round_number=4,
                knockdowns=0,
                significant_strikes_landed=20,
                significant_strikes_attempted=32,
                significant_strikes_rate=62.5,
                total_strikes_landed=26,
                total_strikes_attempted=40,
                takedown_successful=2,
                takedown_attempted=3,
                takedown_rate=66.7,
                submission_attempt=1,
                reversals=0,
                head_landed=11,
                head_attempted=17,
                body_landed=6,
                body_attempted=10,
                leg_landed=3,
                leg_attempted=5,
                distance_landed=16,
                distance_attempted=25,
                clinch_landed=3,
                clinch_attempted=5,
                ground_landed=1,
                ground_attempted=2,
                result="Decision",
                last_round=False,
                time="5:00",
                winner="W"
            ),
            # Ислам Махачев - Раунд 5
            FightStats(
                fight_id=fight1.id,
                fighter_id=1,
                round_number=5,
                knockdowns=0,
                significant_strikes_landed=16,
                significant_strikes_attempted=26,
                significant_strikes_rate=61.5,
                total_strikes_landed=22,
                total_strikes_attempted=33,
                takedown_successful=1,
                takedown_attempted=2,
                takedown_rate=50.0,
                submission_attempt=0,
                reversals=0,
                head_landed=9,
                head_attempted=14,
                body_landed=5,
                body_attempted=8,
                leg_landed=2,
                leg_attempted=4,
                distance_landed=13,
                distance_attempted=20,
                clinch_landed=2,
                clinch_attempted=4,
                ground_landed=1,
                ground_attempted=2,
                result="Decision",
                last_round=True,
                time="5:00",
                winner="W"
            ),
            
            # Чарльз Оливейра - Раунд 1
            FightStats(
                fight_id=fight1.id,
                fighter_id=2,
                round_number=1,
                knockdowns=0,
                significant_strikes_landed=12,
                significant_strikes_attempted=28,
                significant_strikes_rate=42.9,
                total_strikes_landed=15,
                total_strikes_attempted=35,
                takedown_successful=0,
                takedown_attempted=2,
                takedown_rate=0.0,
                submission_attempt=0,
                reversals=1,
                head_landed=6,
                head_attempted=15,
                body_landed=4,
                body_attempted=8,
                leg_landed=2,
                leg_attempted=5,
                distance_landed=10,
                distance_attempted=25,
                clinch_landed=2,
                clinch_attempted=3,
                ground_landed=0,
                ground_attempted=0,
                result="Decision",
                last_round=False,
                time="5:00",
                winner="L"
            ),
            # Чарльз Оливейра - Раунд 2
            FightStats(
                fight_id=fight1.id,
                fighter_id=2,
                round_number=2,
                knockdowns=0,
                significant_strikes_landed=18,
                significant_strikes_attempted=32,
                significant_strikes_rate=56.3,
                total_strikes_landed=22,
                total_strikes_attempted=38,
                takedown_successful=0,
                takedown_attempted=1,
                takedown_rate=0.0,
                submission_attempt=1,
                reversals=0,
                head_landed=10,
                head_attempted=18,
                body_landed=5,
                body_attempted=9,
                leg_landed=3,
                leg_attempted=5,
                distance_landed=15,
                distance_attempted=28,
                clinch_landed=2,
                clinch_attempted=3,
                ground_landed=1,
                ground_attempted=1,
                result="Decision",
                last_round=False,
                time="5:00",
                winner="L"
            ),
            # Чарльз Оливейра - Раунд 3
            FightStats(
                fight_id=fight1.id,
                fighter_id=2,
                round_number=3,
                knockdowns=0,
                significant_strikes_landed=14,
                significant_strikes_attempted=25,
                significant_strikes_rate=56.0,
                total_strikes_landed=18,
                total_strikes_attempted=30,
                takedown_successful=0,
                takedown_attempted=2,
                takedown_rate=0.0,
                submission_attempt=2,
                reversals=1,
                head_landed=8,
                head_attempted=14,
                body_landed=4,
                body_attempted=7,
                leg_landed=2,
                leg_attempted=4,
                distance_landed=12,
                distance_attempted=22,
                clinch_landed=1,
                clinch_attempted=2,
                ground_landed=1,
                ground_attempted=1,
                result="Decision",
                last_round=False,
                time="5:00",
                winner="L"
            ),
            # Чарльз Оливейра - Раунд 4
            FightStats(
                fight_id=fight1.id,
                fighter_id=2,
                round_number=4,
                knockdowns=0,
                significant_strikes_landed=16,
                significant_strikes_attempted=28,
                significant_strikes_rate=57.1,
                total_strikes_landed=20,
                total_strikes_attempted=33,
                takedown_successful=0,
                takedown_attempted=1,
                takedown_rate=0.0,
                submission_attempt=1,
                reversals=0,
                head_landed=9,
                head_attempted=16,
                body_landed=5,
                body_attempted=8,
                leg_landed=2,
                leg_attempted=4,
                distance_landed=14,
                distance_attempted=25,
                clinch_landed=1,
                clinch_attempted=2,
                ground_landed=1,
                ground_attempted=1,
                result="Decision",
                last_round=False,
                time="5:00",
                winner="L"
            ),
            # Чарльз Оливейра - Раунд 5
            FightStats(
                fight_id=fight1.id,
                fighter_id=2,
                round_number=5,
                knockdowns=0,
                significant_strikes_landed=13,
                significant_strikes_attempted=24,
                significant_strikes_rate=54.2,
                total_strikes_landed=17,
                total_strikes_attempted=29,
                takedown_successful=0,
                takedown_attempted=1,
                takedown_rate=0.0,
                submission_attempt=0,
                reversals=0,
                head_landed=7,
                head_attempted=13,
                body_landed=4,
                body_attempted=7,
                leg_landed=2,
                leg_attempted=4,
                distance_landed=11,
                distance_attempted=21,
                clinch_landed=1,
                clinch_attempted=2,
                ground_landed=1,
                ground_attempted=1,
                result="Decision",
                last_round=True,
                time="5:00",
                winner="L"
            )
        ]
        
        for stat in fight_stats:
            session.add(stat)
        
        session.commit()
        print("✅ Детальная статистика боев создана")
        
        # 8. Создаем предстоящие бои
        ufc303 = session.query(Event).filter(Event.name == "UFC 303: McGregor vs Chandler").first()
        ufc304 = session.query(Event).filter(Event.name == "UFC 304: Edwards vs Chimaev").first()
        
        upcoming_fights = [
            UpcomingFight(
                fighter1_id=4,  # Конор Макгрегор
                fighter2_id=3,  # Джастин Гейджи
                weight_class_id=lightweight.id,
                event_name="UFC 303: McGregor vs Chandler",
                event_date=date(2024, 6, 29),
                location="Лас-Вегас, США",
                is_main_event=True,
                is_title_fight=False
            ),
            UpcomingFight(
                fighter1_id=16,  # Леон Эдвардс
                fighter2_id=17,  # Камзат Чимаев
                weight_class_id=welterweight.id,
                event_name="UFC 304: Edwards vs Chimaev",
                event_date=date(2024, 7, 27),
                location="Манчестер, Великобритания",
                is_main_event=True,
                is_title_fight=True
            ),
            UpcomingFight(
                fighter1_id=10,  # Том Аспиналл
                fighter2_id=11,  # Сергей Павлович
                weight_class_id=heavyweight.id,
                event_name="UFC 305: Aspinall vs Pavlovich",
                event_date=date(2024, 8, 17),
                location="Лондон, Великобритания",
                is_main_event=True,
                is_title_fight=True
            ),
            UpcomingFight(
                fighter1_id=7,  # Илья Топурия
                fighter2_id=5,  # Александр Волкановски
                weight_class_id=featherweight.id,
                event_name="UFC 306: Topuria vs Volkanovski",
                event_date=date(2024, 9, 14),
                location="Мадрид, Испания",
                is_main_event=True,
                is_title_fight=True
            )
        ]
        
        for fight in upcoming_fights:
            session.add(fight)
        
        session.commit()
        print("✅ Предстоящие бои созданы")
        
        # Выводим статистику
        fighters_count = session.query(Fighter).count()
        weight_classes_count = session.query(WeightClass).count()
        rankings_count = session.query(Ranking).count()
        records_count = session.query(FightRecord).count()
        events_count = session.query(Event).count()
        fights_count = session.query(Fight).count()
        fight_stats_count = session.query(FightStats).count()
        upcoming_fights_count = session.query(UpcomingFight).count()
        
        print("\n" + "="*60)
        print("📊 Статистика расширенной тестовой базы данных:")
        print("="*60)
        print(f"🥊 Бойцов: {fighters_count}")
        print(f"⚖️ Весовых категорий: {weight_classes_count}")
        print(f"🏆 Рейтингов: {rankings_count}")
        print(f"📋 Боевых рекордов: {records_count}")
        print(f"🎪 Событий: {events_count}")
        print(f"🥊 Исторических боев: {fights_count}")
        print(f"📈 Статистики боев: {fight_stats_count}")
        print(f"📅 Предстоящих боев: {upcoming_fights_count}")
        print("="*60)
        print("✅ Расширенная тестовая база данных создана: debug_ufc_ranker.db")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        session.rollback()
        raise
    finally:
        session.close()

def main():
    """Главная функция"""
    print("🗄️ Создание расширенной тестовой базы данных для отладки")
    print("="*60)
    
    try:
        create_debug_database()
    except Exception as e:
        print(f"❌ Ошибка создания базы данных: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Расширенная тестовая база данных готова для отладки страницы бойца!")
        print("💡 Теперь вы можете использовать debug_ufc_ranker.db для тестирования")
    else:
        print("\n💥 Не удалось создать расширенную тестовую базу данных")





