#!/usr/bin/env python3
"""
Фоновые задачи для обновления данных UFC
"""

import sys
import os
from typing import Dict, List, Any
from datetime import datetime, timedelta

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tasks.celery_app import celery_app
from parsers.data_source_manager import DataSourceManager
from database.config import SessionLocal
from database.models import Fighter, WeightClass, Ranking, Event, Fight, FightStats
from sqlalchemy import func, desc


@celery_app.task(bind=True, max_retries=3)
def update_rankings(self, force_refresh: bool = False):
    """Обновляет рейтинги UFC"""
    try:
        print(f"🔄 Запуск обновления рейтингов (попытка {self.request.retries + 1})")
        
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
            raise Exception("No rankings data received")
            
    except Exception as e:
        print(f"❌ Ошибка при обновлении рейтингов: {e}")
        if self.request.retries < self.max_retries:
            print(f"🔄 Повторная попытка через 60 секунд...")
            raise self.retry(countdown=60)
        else:
            print(f"❌ Максимальное количество попыток превышено")
            raise


@celery_app.task(bind=True, max_retries=3)
def update_fighters(self, force_refresh: bool = False):
    """Обновляет данные бойцов"""
    try:
        print(f"🔄 Запуск обновления бойцов (попытка {self.request.retries + 1})")
        
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
                        fighter.updated_at = datetime.utcnow()
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
            raise Exception("No fighters data received")
            
    except Exception as e:
        print(f"❌ Ошибка при обновлении бойцов: {e}")
        if self.request.retries < self.max_retries:
            print(f"🔄 Повторная попытка через 60 секунд...")
            raise self.retry(countdown=60)
        else:
            print(f"❌ Максимальное количество попыток превышено")
            raise


@celery_app.task(bind=True, max_retries=3)
def update_events(self, force_refresh: bool = False):
    """Обновляет события UFC"""
    try:
        print(f"🔄 Запуск обновления событий (попытка {self.request.retries + 1})")
        
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
                        event.date = datetime.strptime(event_data.get('date', ''), '%Y-%m-%d').date() if event_data.get('date') else event.date
                        event.location = event_data.get('location', event.location)
                        event.venue = event_data.get('venue', event.venue)
                        event.attendance = event_data.get('attendance', event.attendance)
                        event.image_url = event_data.get('image_url', event.image_url)
                        event.is_upcoming = event_data.get('is_upcoming', event.is_upcoming)
                        event.updated_at = datetime.utcnow()
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
            raise Exception("No events data received")
            
    except Exception as e:
        print(f"❌ Ошибка при обновлении событий: {e}")
        if self.request.retries < self.max_retries:
            print(f"🔄 Повторная попытка через 60 секунд...")
            raise self.retry(countdown=60)
        else:
            print(f"❌ Максимальное количество попыток превышено")
            raise


@celery_app.task(bind=True, max_retries=3)
def update_fight_stats(self, force_refresh: bool = False):
    """Обновляет статистику боев"""
    try:
        print(f"🔄 Запуск обновления статистики боев (попытка {self.request.retries + 1})")
        
        manager = DataSourceManager()
        fight_stats = manager.get_fight_stats()
        
        if fight_stats:
            db = SessionLocal()
            try:
                # Очищаем старую статистику
                db.query(FightStats).delete()
                
                # Сохраняем новую статистику
                for stats_data in fight_stats:
                    fight_stat = FightStats(
                        fight_id=stats_data.get('fight_id', 0),
                        fighter_id=stats_data.get('fighter_id', 0),
                        round_number=stats_data.get('round_number', 1),
                        knockdowns=stats_data.get('knockdowns', 0),
                        significant_strikes_landed=stats_data.get('significant_strikes_landed', 0),
                        significant_strikes_attempted=stats_data.get('significant_strikes_attempted', 0),
                        significant_strikes_rate=stats_data.get('significant_strikes_rate', 0.0),
                        total_strikes_landed=stats_data.get('total_strikes_landed', 0),
                        total_strikes_attempted=stats_data.get('total_strikes_attempted', 0),
                        takedown_successful=stats_data.get('takedown_successful', 0),
                        takedown_attempted=stats_data.get('takedown_attempted', 0),
                        takedown_rate=stats_data.get('takedown_rate', 0.0),
                        submission_attempt=stats_data.get('submission_attempt', 0),
                        reversals=stats_data.get('reversals', 0),
                        head_landed=stats_data.get('head_landed', 0),
                        head_attempted=stats_data.get('head_attempted', 0),
                        body_landed=stats_data.get('body_landed', 0),
                        body_attempted=stats_data.get('body_attempted', 0),
                        leg_landed=stats_data.get('leg_landed', 0),
                        leg_attempted=stats_data.get('leg_attempted', 0),
                        distance_landed=stats_data.get('distance_landed', 0),
                        distance_attempted=stats_data.get('distance_attempted', 0),
                        clinch_landed=stats_data.get('clinch_landed', 0),
                        clinch_attempted=stats_data.get('clinch_attempted', 0),
                        ground_landed=stats_data.get('ground_landed', 0),
                        ground_attempted=stats_data.get('ground_attempted', 0),
                        result=stats_data.get('result', ''),
                        last_round=stats_data.get('last_round', False),
                        time=stats_data.get('time', ''),
                        winner=stats_data.get('winner', '')
                    )
                    db.add(fight_stat)
                
                db.commit()
                print(f"✅ Статистика боев обновлена: {len(fight_stats)} записей")
                
                return {
                    'status': 'success',
                    'records_updated': len(fight_stats),
                    'timestamp': datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                db.rollback()
                print(f"❌ Ошибка при сохранении статистики: {e}")
                raise
            finally:
                db.close()
        else:
            print("❌ Не удалось получить статистику боев")
            raise Exception("No fight stats data received")
            
    except Exception as e:
        print(f"❌ Ошибка при обновлении статистики боев: {e}")
        if self.request.retries < self.max_retries:
            print(f"🔄 Повторная попытка через 60 секунд...")
            raise self.retry(countdown=60)
        else:
            print(f"❌ Максимальное количество попыток превышено")
            raise


@celery_app.task(bind=True, max_retries=2)
def cleanup_old_data(self, days_to_keep: int = 365):
    """Очищает старые данные"""
    try:
        print(f"🧹 Запуск очистки старых данных (старше {days_to_keep} дней)")
        
        db = SessionLocal()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Удаляем старые события
            old_events = db.query(Event).filter(
                Event.date < cutoff_date,
                Event.is_upcoming == False
            ).all()
            
            for event in old_events:
                # Удаляем связанные бои и статистику
                db.query(FightStats).filter(FightStats.fight.has(event_id=event.id)).delete()
                db.query(Fight).filter(Fight.event_id == event.id).delete()
                db.delete(event)
            
            # Удаляем старые записи статистики без связанных боев
            old_stats = db.query(FightStats).filter(
                FightStats.created_at < cutoff_date
            ).all()
            
            for stat in old_stats:
                db.delete(stat)
            
            db.commit()
            
            print(f"✅ Очистка завершена: удалено {len(old_events)} событий и {len(old_stats)} записей статистики")
            
            return {
                'status': 'success',
                'events_deleted': len(old_events),
                'stats_deleted': len(old_stats),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            db.rollback()
            print(f"❌ Ошибка при очистке данных: {e}")
            raise
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Ошибка при очистке старых данных: {e}")
        if self.request.retries < self.max_retries:
            print(f"🔄 Повторная попытка через 300 секунд...")
            raise self.retry(countdown=300)
        else:
            print(f"❌ Максимальное количество попыток превышено")
            raise


@celery_app.task
def update_all_data(force_refresh: bool = False):
    """Обновляет все данные"""
    print("🔄 Запуск полного обновления данных...")
    
    try:
        # Запускаем все задачи обновления
        rankings_task = update_rankings.delay(force_refresh)
        fighters_task = update_fighters.delay(force_refresh)
        events_task = update_events.delay(force_refresh)
        stats_task = update_fight_stats.delay(force_refresh)
        
        # Ждем завершения всех задач
        results = {
            'rankings': rankings_task.get(timeout=600),
            'fighters': fighters_task.get(timeout=600),
            'events': events_task.get(timeout=600),
            'fight_stats': stats_task.get(timeout=600)
        }
        
        print("✅ Все данные успешно обновлены")
        return {
            'status': 'success',
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Ошибка при полном обновлении данных: {e}")
        raise

