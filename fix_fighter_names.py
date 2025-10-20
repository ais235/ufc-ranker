#!/usr/bin/env python3
"""
Исправление бойцов с пустыми русскими именами
"""

from database.config import SessionLocal
from database.models import Fighter

def fix_fighter_names():
    """Исправляет бойцов с пустыми name_ru"""
    db = SessionLocal()
    
    try:
        # Находим всех бойцов с пустым name_ru
        fighters = db.query(Fighter).filter(Fighter.name_ru == None).all()
        
        print(f"Найдено бойцов с пустыми именами: {len(fighters)}")
        print()
        
        for fighter in fighters:
            old_name_ru = fighter.name_ru
            # Используем английское имя если русское пусто
            fighter.name_ru = fighter.name_en or "Unknown Fighter"
            
            print(f"ID {fighter.id}: '{old_name_ru}' -> '{fighter.name_ru}'")
        
        db.commit()
        print()
        print(f"Успешно исправлено {len(fighters)} бойцов!")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_fighter_names()

