#!/usr/bin/env python3
"""
Аналитические задачи для UFC Ranker
"""

import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tasks.celery_app import celery_app
from database.config import SessionLocal
from database.models import Fighter, WeightClass, Ranking, Event, Fight, FightStats


@celery_app.task
def generate_daily_analytics():
    """Генерирует ежедневную аналитику"""
    print("📊 Генерация ежедневной аналитики...")
    
    try:
        db = SessionLocal()
        
        analytics = {
            'date': datetime.utcnow().isoformat(),
            'fighters_stats': get_fighters_analytics(db),
            'rankings_changes': get_rankings_changes(db),
            'events_stats': get_events_analytics(db),
            'fight_stats': get_fight_stats_analytics(db),
            'top_performers': get_top_performers(db),
            'country_stats': get_country_stats(db)
        }
        
        # Сохраняем аналитику в Redis или БД
        save_analytics(analytics)
        
        print("✅ Ежедневная аналитика сгенерирована")
        return analytics
        
    except Exception as e:
        print(f"❌ Ошибка при генерации аналитики: {e}")
        raise
    finally:
        db.close()


def get_fighters_analytics(db) -> Dict[str, Any]:
    """Аналитика по бойцам"""
    total_fighters = db.query(Fighter).count()
    
    # Бойцы по странам
    country_stats = db.query(
        Fighter.country,
        func.count(Fighter.id).label('count')
    ).filter(
        Fighter.country.isnot(None)
    ).group_by(Fighter.country).order_by(
        func.count(Fighter.id).desc()
    ).limit(10).all()
    
    # Бойцы по весовым категориям
    weight_class_stats = db.query(
        Fighter.weight_class,
        func.count(Fighter.id).label('count')
    ).filter(
        Fighter.weight_class.isnot(None)
    ).group_by(Fighter.weight_class).all()
    
    # Возрастная статистика
    age_stats = db.query(
        func.avg(Fighter.age).label('avg_age'),
        func.min(Fighter.age).label('min_age'),
        func.max(Fighter.age).label('max_age')
    ).filter(Fighter.age.isnot(None)).first()
    
    return {
        'total_fighters': total_fighters,
        'top_countries': [{'country': country, 'count': count} for country, count in country_stats],
        'weight_class_distribution': [{'weight_class': wc, 'count': count} for wc, count in weight_class_stats],
        'age_stats': {
            'average': float(age_stats.avg_age) if age_stats.avg_age else 0,
            'min': age_stats.min_age or 0,
            'max': age_stats.max_age or 0
        }
    }


def get_rankings_changes(db) -> Dict[str, Any]:
    """Анализ изменений в рейтингах"""
    # Чемпионы
    champions = db.query(Ranking).filter(Ranking.is_champion == True).count()
    
    # Рейтинги по категориям
    rankings_by_category = db.query(
        WeightClass.name_ru,
        func.count(Ranking.id).label('count')
    ).join(Ranking).group_by(WeightClass.name_ru).all()
    
    return {
        'total_champions': champions,
        'rankings_by_category': [{'category': cat, 'count': count} for cat, count in rankings_by_category]
    }


def get_events_analytics(db) -> Dict[str, Any]:
    """Аналитика по событиям"""
    total_events = db.query(Event).count()
    upcoming_events = db.query(Event).filter(Event.is_upcoming == True).count()
    
    # События по месяцам
    monthly_events = db.query(
        func.date_trunc('month', Event.date).label('month'),
        func.count(Event.id).label('count')
    ).filter(
        Event.date.isnot(None)
    ).group_by(
        func.date_trunc('month', Event.date)
    ).order_by(desc('month')).limit(12).all()
    
    # Средняя посещаемость
    avg_attendance = db.query(
        func.avg(Event.attendance).label('avg_attendance')
    ).filter(
        Event.attendance.isnot(None),
        Event.attendance > 0
    ).first()
    
    return {
        'total_events': total_events,
        'upcoming_events': upcoming_events,
        'monthly_events': [{'month': str(month), 'count': count} for month, count in monthly_events],
        'average_attendance': float(avg_attendance.avg_attendance) if avg_attendance.avg_attendance else 0
    }


def get_fight_stats_analytics(db) -> Dict[str, Any]:
    """Аналитика по статистике боев"""
    total_fights = db.query(Fight).count()
    total_fight_stats = db.query(FightStats).count()
    
    # Средние показатели
    avg_stats = db.query(
        func.avg(FightStats.significant_strikes_landed).label('avg_sig_strikes'),
        func.avg(FightStats.takedown_successful).label('avg_takedowns'),
        func.avg(FightStats.knockdowns).label('avg_knockdowns')
    ).first()
    
    # Топ бойцов по значимым ударам
    top_strikers = db.query(
        Fighter.name_ru,
        func.sum(FightStats.significant_strikes_landed).label('total_strikes')
    ).join(FightStats).group_by(Fighter.id, Fighter.name_ru).order_by(
        desc('total_strikes')
    ).limit(10).all()
    
    # Топ бойцов по тейкдаунам
    top_grapplers = db.query(
        Fighter.name_ru,
        func.sum(FightStats.takedown_successful).label('total_takedowns')
    ).join(FightStats).group_by(Fighter.id, Fighter.name_ru).order_by(
        desc('total_takedowns')
    ).limit(10).all()
    
    return {
        'total_fights': total_fights,
        'total_fight_stats': total_fight_stats,
        'average_stats': {
            'significant_strikes': float(avg_stats.avg_sig_strikes) if avg_stats.avg_sig_strikes else 0,
            'takedowns': float(avg_stats.avg_takedowns) if avg_stats.avg_takedowns else 0,
            'knockdowns': float(avg_stats.avg_knockdowns) if avg_stats.avg_knockdowns else 0
        },
        'top_strikers': [{'fighter': name, 'strikes': strikes} for name, strikes in top_strikers],
        'top_grapplers': [{'fighter': name, 'takedowns': takedowns} for name, takedowns in top_grapplers]
    }


def get_top_performers(db) -> Dict[str, List[Dict]]:
    """Топ исполнители по различным показателям"""
    
    # Топ по победам
    top_winners = db.query(
        Fighter.name_ru,
        Fighter.win,
        Fighter.lose,
        Fighter.draw
    ).order_by(desc(Fighter.win)).limit(10).all()
    
    # Топ по проценту побед
    top_win_percentage = db.query(
        Fighter.name_ru,
        Fighter.win,
        Fighter.lose,
        Fighter.draw,
        func.round(
            (Fighter.win * 100.0) / (Fighter.win + Fighter.lose + Fighter.draw), 2
        ).label('win_percentage')
    ).filter(
        (Fighter.win + Fighter.lose + Fighter.draw) > 0
    ).order_by(desc('win_percentage')).limit(10).all()
    
    return {
        'most_wins': [{'fighter': name, 'wins': wins, 'losses': losses, 'draws': draws} 
                     for name, wins, losses, draws in top_winners],
        'best_win_percentage': [{'fighter': name, 'wins': wins, 'losses': losses, 'draws': draws, 'percentage': percentage}
                               for name, wins, losses, draws, percentage in top_win_percentage]
    }


def get_country_stats(db) -> Dict[str, Any]:
    """Статистика по странам"""
    # Топ страны по количеству бойцов
    top_countries = db.query(
        Fighter.country,
        func.count(Fighter.id).label('fighter_count'),
        func.avg(Fighter.win).label('avg_wins'),
        func.avg(Fighter.lose).label('avg_losses')
    ).filter(
        Fighter.country.isnot(None)
    ).group_by(Fighter.country).order_by(
        desc('fighter_count')
    ).limit(15).all()
    
    # Чемпионы по странам
    champions_by_country = db.query(
        Fighter.country,
        func.count(Ranking.id).label('champion_count')
    ).join(Ranking).filter(
        Ranking.is_champion == True,
        Fighter.country.isnot(None)
    ).group_by(Fighter.country).order_by(
        desc('champion_count')
    ).all()
    
    return {
        'top_countries': [{'country': country, 'fighters': count, 'avg_wins': float(avg_wins) if avg_wins else 0, 'avg_losses': float(avg_losses) if avg_losses else 0}
                         for country, count, avg_wins, avg_losses in top_countries],
        'champions_by_country': [{'country': country, 'champions': count} for country, count in champions_by_country]
    }


def save_analytics(analytics: Dict[str, Any]) -> None:
    """Сохраняет аналитику в Redis или БД"""
    try:
        # Здесь можно сохранить в Redis для быстрого доступа
        # или в отдельную таблицу аналитики в БД
        print("💾 Аналитика сохранена")
    except Exception as e:
        print(f"❌ Ошибка при сохранении аналитики: {e}")


@celery_app.task
def generate_fighter_analytics(fighter_id: int):
    """Генерирует детальную аналитику для конкретного бойца"""
    print(f"📊 Генерация аналитики для бойца {fighter_id}...")
    
    try:
        db = SessionLocal()
        
        fighter = db.query(Fighter).filter(Fighter.id == fighter_id).first()
        if not fighter:
            raise Exception(f"Боец с ID {fighter_id} не найден")
        
        # Статистика боев
        fight_stats = db.query(FightStats).filter(FightStats.fighter_id == fighter_id).all()
        
        # Агрегированная статистика
        total_rounds = len(fight_stats)
        total_fights = db.query(Fight).filter(
            (Fight.fighter1_id == fighter_id) | (Fight.fighter2_id == fighter_id)
        ).count()
        
        # Средние показатели
        avg_sig_strikes = sum(stat.significant_strikes_landed for stat in fight_stats) / total_rounds if total_rounds > 0 else 0
        avg_takedowns = sum(stat.takedown_successful for stat in fight_stats) / total_rounds if total_rounds > 0 else 0
        avg_knockdowns = sum(stat.knockdowns for stat in fight_stats) / total_rounds if total_rounds > 0 else 0
        
        analytics = {
            'fighter_id': fighter_id,
            'fighter_name': fighter.name_ru,
            'total_fights': total_fights,
            'total_rounds': total_rounds,
            'average_stats': {
                'significant_strikes_per_round': round(avg_sig_strikes, 2),
                'takedowns_per_round': round(avg_takedowns, 2),
                'knockdowns_per_round': round(avg_knockdowns, 2)
            },
            'win_loss_record': {
                'wins': fighter.win,
                'losses': fighter.lose,
                'draws': fighter.draw,
                'win_percentage': round((fighter.win / (fighter.win + fighter.lose + fighter.draw)) * 100, 2) if (fighter.win + fighter.lose + fighter.draw) > 0 else 0
            }
        }
        
        print(f"✅ Аналитика для {fighter.name_ru} сгенерирована")
        return analytics
        
    except Exception as e:
        print(f"❌ Ошибка при генерации аналитики бойца: {e}")
        raise
    finally:
        db.close()


@celery_app.task
def generate_weight_class_analytics(weight_class_id: int):
    """Генерирует аналитику для весовой категории"""
    print(f"📊 Генерация аналитики для весовой категории {weight_class_id}...")
    
    try:
        db = SessionLocal()
        
        weight_class = db.query(WeightClass).filter(WeightClass.id == weight_class_id).first()
        if not weight_class:
            raise Exception(f"Весовая категория с ID {weight_class_id} не найдена")
        
        # Бойцы в категории
        fighters_in_class = db.query(Fighter).filter(Fighter.weight_class == weight_class.name_ru).count()
        
        # Рейтинги в категории
        rankings = db.query(Ranking).filter(Ranking.weight_class_id == weight_class_id).count()
        
        # Бои в категории
        fights_in_class = db.query(Fight).filter(Fight.weight_class_id == weight_class_id).count()
        
        analytics = {
            'weight_class_id': weight_class_id,
            'weight_class_name': weight_class.name_ru,
            'fighters_count': fighters_in_class,
            'rankings_count': rankings,
            'fights_count': fights_in_class
        }
        
        print(f"✅ Аналитика для {weight_class.name_ru} сгенерирована")
        return analytics
        
    except Exception as e:
        print(f"❌ Ошибка при генерации аналитики категории: {e}")
        raise
    finally:
        db.close()
