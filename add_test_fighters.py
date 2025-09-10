#!/usr/bin/env python3
"""
Добавление тестовых бойцов в базу данных для демонстрации
"""

import sqlite3
import random

def add_test_fighters():
    """Добавляем тестовых бойцов в БД"""
    conn = sqlite3.connect('ufc_ranker_v2.db')
    cursor = conn.cursor()
    
    # Тестовые бойцы для легкого веса
    lightweight_fighters = [
        ("Ислам Махачев", "Islam Makhachev", "Россия", 25, 1, 0),
        ("Александр Волкановски", "Alexander Volkanovski", "Австралия", 26, 3, 0),
        ("Макс Холловэй", "Max Holloway", "США", 25, 7, 0),
        ("Чарльз Оливейра", "Charles Oliveira", "Бразилия", 34, 9, 0),
        ("Джастин Гэйтжи", "Justin Gaethje", "США", 25, 4, 0),
        ("Дэн Хукер", "Dan Hooker", "Новая Зеландия", 23, 12, 0),
        ("Пэдди Пимблетт", "Paddy Pimblett", "Великобритания", 20, 3, 0),
        ("Матеуш Гэмрот", "Mateusz Gamrot", "Польша", 23, 2, 0),
        ("Бенил Дариуш", "Beneil Dariush", "США", 22, 5, 1),
        ("Рафаэль Физиев", "Rafael Fiziev", "Азербайджан", 12, 2, 0),
        ("Ренато Мойкано", "Renato Carneiro", "Бразилия", 18, 5, 1),
        ("Майкл Чендлер", "Michael Chandler", "США", 23, 8, 0),
        ("Бенуа Сен-Дени", "Benoit St.Denis", "Франция", 13, 1, 0),
        ("Грант Доусон", "Grant Dawson", "США", 20, 2, 1),
        ("Йоэль Альварез", "Joel Alvarez", "Испания", 20, 3, 0)
    ]
    
    # Тестовые бойцы для полулегкого веса
    featherweight_fighters = [
        ("Илия Топурия", "Ilia Topuria", "Грузия", 14, 0, 0),
        ("Александр Волкановски", "Alexander Volkanovski", "Австралия", 26, 3, 0),
        ("Макс Холловэй", "Max Holloway", "США", 25, 7, 0),
        ("Брайан Ортега", "Brian Ortega", "США", 15, 3, 0),
        ("Яир Родригес", "Yair Rodriguez", "Мексика", 16, 4, 0),
        ("Кэлвин Каттар", "Calvin Kattar", "США", 23, 7, 0),
        ("Джош Эмметт", "Josh Emmett", "США", 18, 4, 0),
        ("Арнольд Аллен", "Arnold Allen", "Великобритания", 19, 2, 0),
        ("Дэн Иге", "Dan Ige", "США", 17, 7, 0),
        ("Содик Юсуфф", "Sodiq Yusuff", "Нигерия", 13, 3, 0)
    ]
    
    # Тестовые бойцы для тяжелого веса
    heavyweight_fighters = [
        ("Джон Джонс", "Jon Jones", "США", 27, 1, 0),
        ("Фрэнсис Нганну", "Francis Ngannou", "Камерун", 17, 3, 0),
        ("Стипе Миочич", "Stipe Miocic", "США", 20, 4, 0),
        ("Дэниел Кормье", "Daniel Cormier", "США", 22, 3, 0),
        ("Кайл Диллашоу", "Kyle Dillashaw", "США", 18, 5, 0),
        ("Джонни Уокер", "Johnny Walker", "Бразилия", 21, 7, 0),
        ("Доминик Рейес", "Dominick Reyes", "США", 12, 4, 0),
        ("Волкан Оздемир", "Volkan Oezdemir", "Швейцария", 18, 7, 0),
        ("Антонио Родриго Ногейра", "Antonio Rodrigo Nogueira", "Бразилия", 34, 10, 1),
        ("Фабрисио Вердум", "Fabricio Werdum", "Бразилия", 24, 9, 1)
    ]
    
    # Тестовые бойцы для полусреднего веса
    welterweight_fighters = [
        ("Леон Эдвардс", "Leon Edwards", "Великобритания", 22, 3, 0),
        ("Колби Ковингтон", "Colby Covington", "США", 17, 4, 0),
        ("Хамзат Чимаев", "Khamzat Chimaev", "Швеция", 13, 0, 0),
        ("Белал Мухаммад", "Belal Muhammad", "США", 23, 3, 0),
        ("Шавкат Рахмонов", "Shavkat Rakhmonov", "Казахстан", 18, 0, 0),
        ("Иан Мачадо Гарри", "Ian Machado Garry", "Ирландия", 14, 0, 0),
        ("Джефф Нил", "Geoff Neal", "США", 15, 5, 0),
        ("Висенте Люке", "Vicente Luque", "Бразилия", 22, 9, 0),
        ("Нил Магни", "Neil Magny", "США", 28, 11, 0),
        ("Джордж Масвидал", "Jorge Masvidal", "США", 35, 17, 0)
    ]
    
    # Обновляем существующих бойцов
    print("🔄 Обновляем существующих бойцов...")
    
    # Ислам Махачев - легкий вес
    cursor.execute("""
        UPDATE fighters 
        SET weight_class = 'Легкий вес', win = 25, lose = 1, draw = 0
        WHERE name_ru = 'Ислам Махачев'
    """)
    
    # Александр Волкановски - полулегкий вес
    cursor.execute("""
        UPDATE fighters 
        SET weight_class = 'Полулегкий вес', win = 26, lose = 3, draw = 0
        WHERE name_ru = 'Александр Волкановски'
    """)
    
    # Макс Холловэй - полулегкий вес
    cursor.execute("""
        UPDATE fighters 
        SET weight_class = 'Полулегкий вес', win = 25, lose = 7, draw = 0
        WHERE name_ru = 'Макс Холловэй'
    """)
    
    # Джон Джонс - тяжелый вес
    cursor.execute("""
        UPDATE fighters 
        SET weight_class = 'Тяжелый вес', win = 27, lose = 1, draw = 0
        WHERE name_ru = 'Джон Джонс'
    """)
    
    # Фрэнсис Нганну - тяжелый вес
    cursor.execute("""
        UPDATE fighters 
        SET weight_class = 'Тяжелый вес', win = 17, lose = 3, draw = 0
        WHERE name_ru = 'Фрэнсис Нганну'
    """)
    
    # Добавляем новых бойцов
    print("➕ Добавляем новых бойцов...")
    
    all_fighters = [
        ("Легкий вес", lightweight_fighters),
        ("Полулегкий вес", featherweight_fighters),
        ("Тяжелый вес", heavyweight_fighters),
        ("Полусредний вес", welterweight_fighters)
    ]
    
    for weight_class, fighters in all_fighters:
        print(f"   📝 Добавляем {len(fighters)} бойцов в {weight_class}")
        
        for fighter in fighters:
            try:
                cursor.execute("""
                    INSERT INTO fighters (name_ru, name_en, country, weight_class, win, lose, draw)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (fighter[0], fighter[1], fighter[2], weight_class, fighter[3], fighter[4], fighter[5]))
            except sqlite3.IntegrityError:
                # Боец уже существует, пропускаем
                pass
    
    conn.commit()
    conn.close()
    
    print("✅ Тестовые бойцы добавлены!")

def main():
    """Основная функция"""
    print("🥊 Добавление тестовых бойцов в базу данных...")
    add_test_fighters()
    print("🎉 Готово!")

if __name__ == "__main__":
    main()
