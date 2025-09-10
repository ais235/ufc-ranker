#!/usr/bin/env python3
"""
FastAPI приложение для UFC Ranker
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import sys
import os

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import get_db, init_database
from database.models import Fighter, WeightClass, Ranking, FightRecord, UpcomingFight, Event, Fight, FightStats
from pydantic import BaseModel

# Инициализируем FastAPI
app = FastAPI(
    title="UFC Ranker API",
    description="API для UFC рейтингов и сравнения бойцов",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене замените на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic модели для API
class FighterResponse(BaseModel):
    id: int
    name: str  # Основное имя для отображения
    name_ru: str
    name_en: Optional[str] = None
    nickname: Optional[str] = None
    country: Optional[str] = None
    country_flag_url: Optional[str] = None
    image_url: Optional[str] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    reach: Optional[int] = None
    age: Optional[int] = None
    weight_class: Optional[str] = None
    wins: int = 0  # Переименуем для консистентности
    losses: int = 0
    draws: int = 0
    weight_class_id: Optional[int] = None
    career: Optional[str] = None
    
    class Config:
        from_attributes = True

class WeightClassResponse(BaseModel):
    id: int
    name: str  # Основное имя для отображения
    name_ru: str
    name_en: Optional[str] = None
    weight_min: Optional[int] = None
    weight_max: Optional[int] = None
    weight_limit: Optional[str] = None  # Строка для отображения
    gender: str
    is_p4p: bool
    
    class Config:
        from_attributes = True

class RankingResponse(BaseModel):
    fighter: FighterResponse
    rank_position: Optional[int] = None
    is_champion: bool = False
    rank_change: int = 0
    
    class Config:
        from_attributes = True

class FightRecordResponse(BaseModel):
    wins: int
    losses: int
    draws: int
    no_contests: int
    total_fights: int
    win_percentage: float
    
    class Config:
        from_attributes = True

class FighterDetailResponse(FighterResponse):
    fight_record: Optional[FightRecordResponse] = None
    
    class Config:
        from_attributes = True

class UpcomingFightResponse(BaseModel):
    id: int
    fighter1: FighterResponse
    fighter2: FighterResponse
    weight_class: WeightClassResponse
    is_main_event: bool = False
    is_title_fight: bool = False
    
    class Config:
        from_attributes = True

class EventResponse(BaseModel):
    id: int
    name: str
    date: Optional[str] = None
    location: Optional[str] = None
    venue: Optional[str] = None
    attendance: Optional[int] = None
    image_url: Optional[str] = None
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        data = obj.__dict__.copy()
        if 'date' in data and data['date']:
            data['date'] = str(data['date'])
        return cls(**data)

class FightResponse(BaseModel):
    id: int
    event: EventResponse
    fighter1: FighterResponse
    fighter2: FighterResponse
    weight_class: WeightClassResponse
    scheduled_rounds: int
    result: Optional[str] = None
    fight_date: Optional[str] = None
    is_title_fight: bool = False
    is_main_event: bool = False
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        data = obj.__dict__.copy()
        if 'fight_date' in data and data['fight_date']:
            data['fight_date'] = str(data['fight_date'])
        if 'event' in data and data['event']:
            data['event'] = EventResponse.from_orm(data['event'])
        return cls(**data)

class FightStatsResponse(BaseModel):
    id: int
    fighter: FighterResponse
    round_number: int
    knockdowns: int = 0
    significant_strikes_landed: int = 0
    significant_strikes_attempted: int = 0
    significant_strikes_rate: float = 0.0
    total_strikes_landed: int = 0
    total_strikes_attempted: int = 0
    takedown_successful: int = 0
    takedown_attempted: int = 0
    takedown_rate: float = 0.0
    submission_attempt: int = 0
    reversals: int = 0
    head_landed: int = 0
    head_attempted: int = 0
    body_landed: int = 0
    body_attempted: int = 0
    leg_landed: int = 0
    leg_attempted: int = 0
    distance_landed: int = 0
    distance_attempted: int = 0
    clinch_landed: int = 0
    clinch_attempted: int = 0
    ground_landed: int = 0
    ground_attempted: int = 0
    result: Optional[str] = None
    last_round: bool = False
    time: Optional[str] = None
    winner: Optional[str] = None
    
    class Config:
        from_attributes = True

class FighterStatsSummary(BaseModel):
    fighter: FighterResponse
    total_fights: int
    total_rounds: int
    total_significant_strikes_landed: int
    total_significant_strikes_attempted: int
    average_significant_strikes_rate: float
    total_takedowns_successful: int
    total_takedowns_attempted: int
    average_takedown_rate: float
    total_knockdowns: int
    total_submission_attempts: int
    total_reversals: int
    
    class Config:
        from_attributes = True

# Инициализация БД при запуске
@app.on_event("startup")
async def startup_event():
    init_database()

# API эндпоинты
@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "UFC Ranker API",
        "version": "1.0.0",
        "endpoints": {
            "fighters": "/api/fighters",
            "weight_classes": "/api/weight-classes",
            "rankings": "/api/rankings/{class_id}",
            "upcoming_fights": "/api/upcoming-fights"
        }
    }

@app.get("/api/fighters", response_model=List[FighterResponse])
async def get_fighters(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    country: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Получить список бойцов с фильтрацией"""
    query = db.query(Fighter)
    
    if search:
        query = query.filter(Fighter.name_ru.ilike(f"%{search}%"))
    
    if country:
        query = query.filter(Fighter.country.ilike(f"%{country}%"))
    
    fighters = query.offset(skip).limit(limit).all()
    
    # Преобразуем данные для API
    result = []
    for fighter in fighters:
        result.append(FighterResponse(
            id=fighter.id,
            name=fighter.name_ru,  # Основное имя
            name_ru=fighter.name_ru,
            name_en=fighter.name_en,
            nickname=fighter.nickname,
            country=fighter.country,
            country_flag_url=fighter.country_flag_url,
            image_url=fighter.image_url,
            height=fighter.height,
            weight=fighter.weight,
            reach=fighter.reach,
            age=fighter.age,
            weight_class=fighter.weight_class,
            wins=fighter.win or 0,
            losses=fighter.lose or 0,
            draws=fighter.draw or 0,
            weight_class_id=None,  # Пока нет связи
            career=getattr(fighter, 'career', None)
        ))
    
    return result

@app.get("/api/fighters/{fighter_id}", response_model=FighterDetailResponse)
async def get_fighter(fighter_id: int, db: Session = Depends(get_db)):
    """Получить детальную информацию о бойце"""
    fighter = db.query(Fighter).filter(Fighter.id == fighter_id).first()
    
    if not fighter:
        raise HTTPException(status_code=404, detail="Боец не найден")
    
    return fighter

@app.get("/api/weight-classes", response_model=List[WeightClassResponse])
async def get_weight_classes(db: Session = Depends(get_db)):
    """Получить список весовых категорий"""
    weight_classes = db.query(WeightClass).all()
    
    # Преобразуем данные для API
    result = []
    for wc in weight_classes:
        # Формируем строку с лимитом веса
        weight_limit = None
        if wc.weight_min is not None and wc.weight_max is not None:
            weight_limit = f"{wc.weight_min}-{wc.weight_max} кг"
        elif wc.weight_max is not None:
            weight_limit = f"до {wc.weight_max} кг"
        elif wc.weight_min is not None:
            weight_limit = f"от {wc.weight_min} кг"
        
        result.append(WeightClassResponse(
            id=wc.id,
            name=wc.name_ru,  # Основное имя
            name_ru=wc.name_ru,
            name_en=wc.name_en,
            weight_min=wc.weight_min,
            weight_max=wc.weight_max,
            weight_limit=weight_limit,
            gender=wc.gender,
            is_p4p=wc.is_p4p
        ))
    
    return result

@app.get("/api/rankings", response_model=List[RankingResponse])
async def get_rankings(db: Session = Depends(get_db)):
    """Получить все рейтинги"""
    try:
        rankings = db.query(Ranking).join(Fighter).join(WeightClass).all()
        return rankings
    except Exception as e:
        return []

@app.get("/api/rankings/{class_id}", response_model=List[RankingResponse])
async def get_rankings(class_id: int, db: Session = Depends(get_db)):
    """Получить рейтинг весовой категории"""
    rankings = db.query(Ranking).filter(
        Ranking.weight_class_id == class_id
    ).order_by(Ranking.rank_position).all()
    
    return rankings

@app.get("/api/rankings/{class_id}/champion", response_model=Optional[RankingResponse])
async def get_champion(class_id: int, db: Session = Depends(get_db)):
    """Получить чемпиона весовой категории"""
    champion = db.query(Ranking).filter(
        Ranking.weight_class_id == class_id,
        Ranking.is_champion == True
    ).first()
    
    return champion

@app.get("/api/compare/{fighter1_id}/{fighter2_id}")
async def compare_fighters(fighter1_id: int, fighter2_id: int, db: Session = Depends(get_db)):
    """Сравнить двух бойцов"""
    fighter1 = db.query(Fighter).filter(Fighter.id == fighter1_id).first()
    fighter2 = db.query(Fighter).filter(Fighter.id == fighter2_id).first()
    
    if not fighter1 or not fighter2:
        raise HTTPException(status_code=404, detail="Один или оба бойца не найдены")
    
    return {
        "fighter1": FighterDetailResponse.from_orm(fighter1),
        "fighter2": FighterDetailResponse.from_orm(fighter2),
        "comparison": {
            "height": {
                "fighter1": fighter1.height,
                "fighter2": fighter2.height,
                "difference": (fighter1.height or 0) - (fighter2.height or 0)
            },
            "weight": {
                "fighter1": fighter1.weight,
                "fighter2": fighter2.weight,
                "difference": (fighter1.weight or 0) - (fighter2.weight or 0)
            },
            "reach": {
                "fighter1": fighter1.reach,
                "fighter2": fighter2.reach,
                "difference": (fighter1.reach or 0) - (fighter2.reach or 0)
            },
            "age": {
                "fighter1": fighter1.age,
                "fighter2": fighter2.age,
                "difference": (fighter1.age or 0) - (fighter2.age or 0)
            }
        }
    }

@app.get("/api/upcoming-fights", response_model=List[UpcomingFightResponse])
async def get_upcoming_fights(
    limit: int = 20,
    main_event_only: bool = False,
    db: Session = Depends(get_db)
):
    """Получить предстоящие бои"""
    query = db.query(UpcomingFight)
    
    if main_event_only:
        query = query.filter(UpcomingFight.is_main_event == True)
    
    fights = query.limit(limit).all()
    return fights

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Получить общую статистику"""
    try:
        total_fighters = db.query(Fighter).count()
        total_weight_classes = db.query(WeightClass).count()
        total_upcoming_fights = db.query(UpcomingFight).count()
        total_fights = db.query(Fight).count()
        total_fight_stats = db.query(FightStats).count()
        
        # Топ стран по количеству бойцов
        from sqlalchemy import func
        country_stats = db.query(
            Fighter.country,
            func.count(Fighter.id).label('count')
        ).filter(
            Fighter.country.isnot(None)
        ).group_by(Fighter.country).order_by(
            func.count(Fighter.id).desc()
        ).limit(10).all()
        
        return {
            "total_fighters": total_fighters,
            "total_weight_classes": total_weight_classes,
            "total_upcoming_fights": total_upcoming_fights,
            "total_fights": total_fights,
            "total_fight_stats": total_fight_stats,
            "top_countries": [{"country": country, "count": count} for country, count in country_stats]
        }
    except Exception as e:
        return {
            "total_fighters": 0,
            "total_weight_classes": 0,
            "total_upcoming_fights": 0,
            "total_fights": 0,
            "total_fight_stats": 0,
            "top_countries": [],
            "error": str(e)
        }

# Новые эндпоинты для статистики боев

@app.get("/api/events", response_model=List[EventResponse])
async def get_events(
    skip: int = 0,
    limit: int = 50,
    upcoming_only: bool = False,
    db: Session = Depends(get_db)
):
    """Получить список событий UFC"""
    try:
        query = db.query(Event)
        
        if upcoming_only:
            query = query.filter(Event.is_upcoming == True)
        
        events = query.order_by(Event.date.desc()).offset(skip).limit(limit).all()
        return [EventResponse.from_orm(event) for event in events]
    except Exception as e:
        return []

@app.get("/api/events/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    """Получить детальную информацию о событии"""
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    
    return event

@app.get("/api/fights", response_model=List[FightResponse])
async def get_fights(
    skip: int = 0,
    limit: int = 50,
    fighter_id: Optional[int] = None,
    weight_class_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Получить список боев"""
    try:
        query = db.query(Fight)
        
        if fighter_id:
            query = query.filter(
                (Fight.fighter1_id == fighter_id) | (Fight.fighter2_id == fighter_id)
            )
        
        if weight_class_id:
            query = query.filter(Fight.weight_class_id == weight_class_id)
        
        fights = query.order_by(Fight.fight_date.desc()).offset(skip).limit(limit).all()
        return [FightResponse.from_orm(fight) for fight in fights]
    except Exception as e:
        return []

@app.get("/api/fights/{fight_id}", response_model=FightResponse)
async def get_fight(fight_id: int, db: Session = Depends(get_db)):
    """Получить детальную информацию о бое"""
    fight = db.query(Fight).filter(Fight.id == fight_id).first()
    
    if not fight:
        raise HTTPException(status_code=404, detail="Бой не найден")
    
    return fight

@app.get("/api/fights/{fight_id}/stats", response_model=List[FightStatsResponse])
async def get_fight_stats(fight_id: int, db: Session = Depends(get_db)):
    """Получить статистику боя по раундам"""
    stats = db.query(FightStats).filter(
        FightStats.fight_id == fight_id
    ).order_by(FightStats.round_number, FightStats.fighter_id).all()
    
    return stats

@app.get("/api/fighters/{fighter_id}/stats", response_model=FighterStatsSummary)
async def get_fighter_stats(fighter_id: int, db: Session = Depends(get_db)):
    """Получить статистику бойца"""
    fighter = db.query(Fighter).filter(Fighter.id == fighter_id).first()
    
    if not fighter:
        raise HTTPException(status_code=404, detail="Боец не найден")
    
    # Получаем статистику бойца
    stats_query = db.query(FightStats).filter(FightStats.fighter_id == fighter_id)
    
    total_rounds = stats_query.count()
    total_fights = db.query(Fight).filter(
        (Fight.fighter1_id == fighter_id) | (Fight.fighter2_id == fighter_id)
    ).count()
    
    # Агрегированная статистика
    stats = stats_query.with_entities(
        db.func.sum(FightStats.significant_strikes_landed).label('total_sig_strikes_landed'),
        db.func.sum(FightStats.significant_strikes_attempted).label('total_sig_strikes_attempted'),
        db.func.sum(FightStats.takedown_successful).label('total_takedowns_successful'),
        db.func.sum(FightStats.takedown_attempted).label('total_takedowns_attempted'),
        db.func.sum(FightStats.knockdowns).label('total_knockdowns'),
        db.func.sum(FightStats.submission_attempt).label('total_submission_attempts'),
        db.func.sum(FightStats.reversals).label('total_reversals')
    ).first()
    
    # Вычисляем средние показатели
    avg_sig_strikes_rate = 0.0
    if stats.total_sig_strikes_attempted and stats.total_sig_strikes_attempted > 0:
        avg_sig_strikes_rate = round((stats.total_sig_strikes_landed / stats.total_sig_strikes_attempted) * 100, 2)
    
    avg_takedown_rate = 0.0
    if stats.total_takedowns_attempted and stats.total_takedowns_attempted > 0:
        avg_takedown_rate = round((stats.total_takedowns_successful / stats.total_takedowns_attempted) * 100, 2)
    
    return FighterStatsSummary(
        fighter=fighter,
        total_fights=total_fights,
        total_rounds=total_rounds,
        total_significant_strikes_landed=stats.total_sig_strikes_landed or 0,
        total_significant_strikes_attempted=stats.total_sig_strikes_attempted or 0,
        average_significant_strikes_rate=avg_sig_strikes_rate,
        total_takedowns_successful=stats.total_takedowns_successful or 0,
        total_takedowns_attempted=stats.total_takedowns_attempted or 0,
        average_takedown_rate=avg_takedown_rate,
        total_knockdowns=stats.total_knockdowns or 0,
        total_submission_attempts=stats.total_submission_attempts or 0,
        total_reversals=stats.total_reversals or 0
    )

@app.get("/api/fighters/{fighter_id}/fights", response_model=List[FightResponse])
async def get_fighter_fights(
    fighter_id: int,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Получить бои бойца"""
    fights = db.query(Fight).filter(
        (Fight.fighter1_id == fighter_id) | (Fight.fighter2_id == fighter_id)
    ).order_by(Fight.fight_date.desc()).limit(limit).all()
    
    return fights

@app.post("/api/refresh-ufc-stats")
async def refresh_ufc_stats():
    """Обновить данные ufc.stats (аналог refresh_data())"""
    try:
        from parsers.ufc_stats_importer import UFCStatsImporter
        
        importer = UFCStatsImporter()
        importer.refresh_data()
        
        return {
            "message": "Данные ufc.stats успешно обновлены",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении данных: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
