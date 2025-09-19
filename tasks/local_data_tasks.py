#!/usr/bin/env python3
"""
Локальные фоновые задачи для обновления данных UFC (без Redis)
"""

import sys
import os
from typing import Dict, List, Any
from datetime import datetime, timedelta

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tasks.local_celery_app import task, local_celery_app, beat_scheduler, crontab
from parsers.data_source_manager import DataSourceManager
from database.local_config import SessionLocal
from database.models import Fighter, WeightClass, Ranking, Event, Fight, FightStats


@task
def update_rankings(force_refresh: bool = False):
    """Обновляет рейтинги UFC"""
    try:
        print(f"🔄 Запуск обновления рейтингов (force_refresh={force_refresh})")
        
        manager = DataSourceManager()
        rankings = manager.get_rankings(force_refresh)
        
        if rankings:
            # Сохраняем в БД
            db = SessionLocal()
            try:
                # Очищаем старые рейтинги
                db.query(Ranking).delete()
                
                # Сохраняем новые рейтинги
                for category_name, fighters in rankings.items():
                    # Получаем или создаем весовую категорию
                    weight_class = db.query(WeightClass).filter(
                        WeightClass.name_ru == category_name
                    ).first()
                    
                    if not weight_class:
                        weight_class = WeightClass(
                            name_ru=category_name,
                            name_en=category_name,  # Упрощенная версия
                            gender='male'  # По умолчанию
                        )
                        db.add(weight_class)
                        db.flush()
                    
                    # Сохраняем рейтинги бойцов
                    for fighter_data in fighters:
                        fighter = db.query(Fighter).filter(
                            Fighter.name_ru == fighter_data.get('name', '')
                        ).first()
                        
                        if fighter:
                            ranking = Ranking(
                                fighter_id=fighter.id,
                                weight_class_id=weight_class.id,
                                rank_position=fighter_data.get('rank_position'),
                                is_champion=fighter_data.get('is_champion', False)
                            )
                            db.add(ranking)
                
                db.commit()
                print(f"✅ Рейтинги обновлены: {len(rankings)} категорий")
                
                return {
                    'status': 'success',
                    'categories_updated': len(rankings),
                    'timestamp': datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                db.rollback()
                print(f"❌ Ошибка при сохранении рейтингов: {e}")
                raise
            finally:
                db.close()
        else:
            print("❌ Не удалось получить рейтинги")
            return {'status': 'error', 'message': 'No rankings data received'}
            
    except Exception as e:
        print(f"❌ Ошибка при обновлении рейтингов: {e}")
        return {'status': 'error', 'message': str(e)}


@task
def update_fighters(force_refresh: bool = False):
    """Обновляет данные бойцов"""
    try:
        print(f"🔄 Запуск обновления бойцов (force_refresh={force_refresh})")
        
        manager = DataSourceManager()
        fighters = manager.get_fighters()
        
        if fighters:
            db = SessionLocal()
            try:
                updated_count = 0
                created_count = 0
                
                for fighter_data in fighters:
                    fighter = db.query(Fighter).filter(
                        Fighter.name_ru == fighter_data.get('name', '')
                    ).first()
                    
                    if fighter:
                        # Обновляем существующего бойца
                        fighter.nickname = fighter_data.get('nickname', fighter.nickname)
                        fighter.country = fighter_data.get('country', fighter.country)
                        fighter.height = fighter_data.get('height', fighter.height)
                        fighter.weight = fighter_data.get('weight', fighter.weight)
                        fighter.reach = fighter_data.get('reach', fighter.reach)
                        fighter.age = fighter_data.get('age', fighter.age)
                        fighter.win = fighter_data.get('wins', fighter.win)
                        fighter.lose = fighter_data.get('losses', fighter.lose)
                        fighter.draw = fighter_data.get('draws', fighter.draw)
                        fighter.image_url = fighter_data.get('image_url', fighter.image_url)
                        updated_count += 1
                    else:
                        # Создаем нового бойца
                        fighter = Fighter(
                            name_ru=fighter_data.get('name', ''),
                            name_en=fighter_data.get('name', ''),
                            nickname=fighter_data.get('nickname', ''),
                            country=fighter_data.get('country', ''),
                            height=fighter_data.get('height', 0),
                            weight=fighter_data.get('weight', 0),
                            reach=fighter_data.get('reach', 0),
                            age=fighter_data.get('age', 0),
                            win=fighter_data.get('wins', 0),
                            lose=fighter_data.get('losses', 0),
                            draw=fighter_data.get('draws', 0),
                            weight_class=fighter_data.get('weight_class', ''),
                            image_url=fighter_data.get('image_url', ''),
                            profile_url=fighter_data.get('profile_url', ''),
                            career="UFC"
                        )
                        db.add(fighter)
                        created_count += 1
                
                db.commit()
                print(f"✅ Бойцы обновлены: {updated_count} обновлено, {created_count} создано")
                
                return {
                    'status': 'success',
                    'updated': updated_count,
                    'created': created_count,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                db.rollback()
                print(f"❌ Ошибка при сохранении бойцов: {e}")
                raise
            finally:
                db.close()
        else:
            print("❌ Не удалось получить данные бойцов")
            return {'status': 'error', 'message': 'No fighters data received'}
            
    except Exception as e:
        print(f"❌ Ошибка при обновлении бойцов: {e}")
        return {'status': 'error', 'message': str(e)}


@task
def update_events(force_refresh: bool = False):
    """Обновляет события UFC"""
    try:
        print(f"🔄 Запуск обновления событий (force_refresh={force_refresh})")
        
        manager = DataSourceManager()
        events = manager.get_events()
        
        if events:
            db = SessionLocal()
            try:
                updated_count = 0
                created_count = 0
                
                for event_data in events:
                    event = db.query(Event).filter(
                        Event.name == event_data.get('name', '')
                    ).first()
                    
                    if event:
                        # Обновляем существующее событие
                        if event_data.get('date'):
                            event.date = datetime.strptime(event_data.get('date', ''), '%Y-%m-%d').date()
                        event.location = event_data.get('location', event.location)
                        event.venue = event_data.get('venue', event.venue)
                        event.attendance = event_data.get('attendance', event.attendance)
                        event.image_url = event_data.get('image_url', event.image_url)
                        event.is_upcoming = event_data.get('is_upcoming', event.is_upcoming)
                        updated_count += 1
                    else:
                        # Создаем новое событие
                        event = Event(
                            name=event_data.get('name', ''),
                            date=datetime.strptime(event_data.get('date', ''), '%Y-%m-%d').date() if event_data.get('date') else None,
                            location=event_data.get('location', ''),
                            venue=event_data.get('venue', ''),
                            attendance=event_data.get('attendance', 0),
                            image_url=event_data.get('image_url', ''),
                            is_upcoming=event_data.get('is_upcoming', True)
                        )
                        db.add(event)
                        created_count += 1
                
                db.commit()
                print(f"✅ События обновлены: {updated_count} обновлено, {created_count} создано")
                
                return {
                    'status': 'success',
                    'updated': updated_count,
                    'created': created_count,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                db.rollback()
                print(f"❌ Ошибка при сохранении событий: {e}")
                raise
            finally:
                db.close()
        else:
            print("❌ Не удалось получить данные событий")
            return {'status': 'error', 'message': 'No events data received'}
            
    except Exception as e:
        print(f"❌ Ошибка при обновлении событий: {e}")
        return {'status': 'error', 'message': str(e)}


@task
def update_all_data(force_refresh: bool = False):
    """Обновляет все данные"""
    print("🔄 Запуск полного обновления данных...")
    
    try:
        # Запускаем все задачи обновления
        rankings_task = update_rankings.delay(force_refresh)
        fighters_task = update_fighters.delay(force_refresh)
        events_task = update_events.delay(force_refresh)
        
        # Ждем завершения всех задач
        results = {
            'rankings': rankings_task.result,
            'fighters': fighters_task.result,
            'events': events_task.result
        }
        
        print("✅ Все данные успешно обновлены")
        return {
            'status': 'success',
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Ошибка при полном обновлении данных: {e}")
        return {'status': 'error', 'message': str(e)}


def setup_periodic_tasks():
    """Настраивает периодические задачи"""
    print("📅 Настройка периодических задач...")
    
    # Ежедневное обновление рейтингов в 6:00
    beat_scheduler.add_periodic_task(
        crontab(hour=6, minute=0),
        update_rankings,
        name="daily_rankings_update"
    )
    
    # Ежедневное обновление бойцов в 7:00
    beat_scheduler.add_periodic_task(
        crontab(hour=7, minute=0),
        update_fighters,
        name="daily_fighters_update"
    )
    
    # Ежедневное обновление событий в 8:00
    beat_scheduler.add_periodic_task(
        crontab(hour=8, minute=0),
        update_events,
        name="daily_events_update"
    )
    
    print("✅ Периодические задачи настроены")


if __name__ == "__main__":
    # Тестируем локальные задачи
    print("🧪 Тестирование локальных задач...")
    
    # Запускаем worker
    local_celery_app.start_worker()
    
    # Запускаем планировщик
    setup_periodic_tasks()
    beat_scheduler.start()
    
    # Тестируем обновление данных
    print("\n🔄 Тестируем обновление рейтингов...")
    result = update_rankings.delay(force_refresh=True)
    
    # Ждем выполнения
    import time
    time.sleep(5)
    
    # Показываем результат
    task_result = local_celery_app.get_task_result(result.id)
    print(f"Результат задачи: {task_result}")
    
    # Показываем все задачи
    all_tasks = local_celery_app.get_all_tasks()
    print(f"\n📊 Всего задач: {len(all_tasks)}")
    for task_id, task_info in all_tasks.items():
        print(f"  {task_id}: {task_info['status']}")
    
    # Останавливаем worker
    local_celery_app.stop_worker()
    beat_scheduler.stop()
