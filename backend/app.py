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
    allow_origins=[
        "http://localhost:3000",  # Локальная разработка
        "https://*.railway.app",  # Railway домены
        "https://your-domain.com",  # Ваш домен (замените на реальный)
        "https://www.your-domain.com"  # Ваш домен с www
    ],
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
    name: str  # Основное имя для отображения (будет заполнено из name_ru)
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
    id: int
    fighter: FighterResponse
    weight_class: str
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
    event_date: Optional[str] = None
    location: Optional[str] = None
    venue: Optional[str] = None
    attendance: Optional[int] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    is_upcoming: Optional[bool] = None
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        data = obj.__dict__.copy()
        if 'date' in data and data['date']:
            data['event_date'] = str(data['date'])
        return cls(**data)

class FightResponse(BaseModel):
    id: int
    event_name: Optional[str] = None
    fighter1_name: Optional[str] = None
    fighter2_name: Optional[str] = None
    weight_class: Optional[str] = None
    scheduled_rounds: int = 3
    method: Optional[str] = None
    method_details: Optional[str] = None
    round: Optional[int] = None
    time: Optional[str] = None
    fight_date: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    is_title_fight: bool = False
    is_main_event: bool = False
    is_win: Optional[str] = None
    is_loss: Optional[str] = None
    is_draw: Optional[str] = None
    is_nc: Optional[str] = None
    fighter1_record: Optional[str] = None
    fighter2_record: Optional[str] = None
    fighter1_country: Optional[str] = None
    fighter2_country: Optional[str] = None
    card_type: Optional[str] = None
    referee: Optional[str] = None
    winner_name: Optional[str] = None
    judges_score: Optional[str] = None
    fight_order: Optional[int] = None
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        data = obj.__dict__.copy()
        # Удаляем служебные поля SQLAlchemy
        data.pop('_sa_instance_state', None)
        if 'fight_date' in data and data['fight_date']:
            data['fight_date'] = str(data['fight_date'])
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
        "version": "1.0.1-FIXED",  # Изменили версию, чтобы убедиться, что изменения применились
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
        # Безопасная подстановка имени (защита от NULL)
        safe_name_ru = fighter.name_ru or fighter.name_en or "Unknown Fighter"
        safe_name_en = fighter.name_en or fighter.name_ru or "Unknown Fighter"
        
        result.append(FighterResponse(
            id=fighter.id,
            name=safe_name_ru,  # Основное имя
            name_ru=safe_name_ru,
            name_en=safe_name_en,
            nickname=fighter.nickname,
            country=fighter.country,
            country_flag_url=fighter.country_flag_url,
            image_url=fighter.image_url,
            height=fighter.height,
            weight=fighter.weight,
            reach=fighter.reach,
            age=fighter.age,
            weight_class=fighter.weight_class,
            wins=fighter.wins or 0,
            losses=fighter.losses or 0,
            draws=fighter.draws or 0,
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
    try:
        weight_classes = db.query(WeightClass).all()
        
        # Простое преобразование данных
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
                name=wc.name_ru or wc.name_en or "Неизвестная категория",
                name_ru=wc.name_ru or "",
                name_en=wc.name_en or "",
                weight_min=wc.weight_min,
                weight_max=wc.weight_max,
                weight_limit=weight_limit,
                gender=wc.gender or "male",
                is_p4p=wc.is_p4p or False
            ))
        
        return result
    except Exception as e:
        print(f"Ошибка в get_weight_classes: {e}")
        return []

@app.get("/api/rankings", response_model=List[RankingResponse])
async def get_rankings(db: Session = Depends(get_db)):
    """Получить все рейтинги"""
    try:
        # Используем прямой SQL запрос
        from sqlalchemy import text
        
        result = db.execute(text("""
            SELECT r.id, r.fighter_id, r.weight_class, r.rank_position, r.is_champion, r.rank_change,
                   f.name_ru, f.name_en, f.nickname, f.country, f.age, f.height, f.reach, f.weight,
                   f.wins, f.losses, f.draws, f.no_contests, f.ufc_wins, f.ufc_losses, f.ufc_draws, f.ufc_no_contests, f.fighting_out_of
            FROM rankings r
            LEFT JOIN fighters f ON r.fighter_id = f.id
            ORDER BY r.weight_class, r.rank_position
        """)).fetchall()
        
        rankings = []
        for row in result:
            rankings.append(RankingResponse(
                id=row[0],
                fighter=FighterResponse(
                    id=row[1],
                    name=row[6] or row[7] or "Боец",
                    name_ru=row[6] or "",
                    name_en=row[7] or "",
                    nickname=row[8] or "",
                    country=row[9] or "",
                    age=row[10],
                    height=row[11],
                    reach=row[12],
                    weight=row[13],
                    weight_class_id=None,  # Убираем проблемное поле
                    wins=row[14] or 0,
                    losses=row[15] or 0,
                    draws=row[16] or 0,
                    no_contests=row[17] or 0,
                    ufc_wins=row[18] or 0,
                    ufc_losses=row[19] or 0,
                    ufc_draws=row[20] or 0,
                    ufc_no_contests=row[21] or 0,
                    fighting_out_of=row[22] or "",
                    career=None
                ),
                weight_class=row[2],
                rank_position=row[3],
                is_champion=row[4],
                rank_change=row[5]
            ))
        
        print(f"API: Загружено {len(rankings)} рейтингов")
        return rankings
    except Exception as e:
        print(f"Ошибка API рейтингов: {e}")
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
    event_id: Optional[int] = None,
    event_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Получить список боев с дополнительной информацией о бойцах"""
    import logging
    logger = logging.getLogger("uvicorn.error")
    logger.error(f"!!! FIGHTS API CALLED: event_id={event_id}, event_name={event_name}")
    
    try:
        query = db.query(Fight)
        logger.error(f"!!! Query created")
        
        if fighter_id:
            # Получаем имя бойца по ID
            fighter = db.query(Fighter).filter(Fighter.id == fighter_id).first()
            if fighter:
                fighter_name = fighter.name_en or fighter.name_ru
                query = query.filter(
                    (Fight.fighter1_name == fighter_name) | (Fight.fighter2_name == fighter_name)
                )
        
        if weight_class_id:
            # Получаем название весовой категории по ID
            weight_class = db.query(WeightClass).filter(WeightClass.id == weight_class_id).first()
            if weight_class:
                query = query.filter(Fight.weight_class == weight_class.name_en)
        
        if event_id:
            # Получаем название события по ID
            event = db.query(Event).filter(Event.id == event_id).first()
            logger.error(f"!!! event_id = {event_id}, event = {event}")
            if event:
                logger.error(f"!!! Ищем бои для события '{event.name}' (ID: {event_id})")
                query = query.filter(Fight.event_name == event.name)
            else:
                logger.error(f"!!! Событие с ID {event_id} не найдено")
        
        if event_name:
            query = query.filter(Fight.event_name == event_name)
        
        # Сортируем бои: сначала по типу карты, затем по порядку в карте, затем по главному событию и титульному бою
        fights = query.order_by(
            Fight.card_type.desc(),  # Main card -> Preliminary card -> Early preliminary card
            Fight.fight_order.asc(),  # Порядок внутри карты
            Fight.is_main_event.desc(),
            Fight.is_title_fight.desc(),
            Fight.fight_date.desc()
        ).offset(skip).limit(limit).all()
        
        logger.error(f"!!! Итоговое количество боев после фильтрации: {len(fights)}")
        
        result = []
        for fight in fights:
            try:
                # Получаем дополнительную информацию о бойцах
                fighter1_data = None
                fighter2_data = None
                
                if fight.fighter1_name:
                    fighter1_data = db.query(Fighter).filter(
                        (Fighter.name_en == fight.fighter1_name) | (Fighter.name_ru == fight.fighter1_name)
                    ).first()
                
                if fight.fighter2_name:
                    fighter2_data = db.query(Fighter).filter(
                        (Fighter.name_en == fight.fighter2_name) | (Fighter.name_ru == fight.fighter2_name)
                    ).first()
                
                # Создаем расширенный ответ с информацией о бойцах
                fight_data = fight.__dict__.copy()
                fight_data.pop('_sa_instance_state', None)
                
                # Добавляем информацию о бойцах
                if fighter1_data:
                    fight_data['fighter1_country'] = fighter1_data.country
                    fight_data['fighter1_record'] = f"{fighter1_data.wins}-{fighter1_data.losses}-{fighter1_data.draws}-{fighter1_data.no_contests}"
                else:
                    fight_data['fighter1_country'] = None
                    fight_data['fighter1_record'] = fight.fighter1_record or '0-0-0-0'
                
                if fighter2_data:
                    fight_data['fighter2_country'] = fighter2_data.country
                    fight_data['fighter2_record'] = f"{fighter2_data.wins}-{fighter2_data.losses}-{fighter2_data.draws}-{fighter2_data.no_contests}"
                else:
                    fight_data['fighter2_country'] = None
                    fight_data['fighter2_record'] = fight.fighter2_record or '0-0-0-0'
                
                # Преобразуем дату в строку
                if 'fight_date' in fight_data and fight_data['fight_date']:
                    fight_data['fight_date'] = str(fight_data['fight_date'])
                
                fight_response = FightResponse(**fight_data)
                result.append(fight_response)
                
            except Exception as e:
                logger.error(f"!!! Ошибка при сериализации боя {fight.id}: {e}")
                continue
        
        logger.error(f"!!! Возвращаем {len(result)} боев")
        return result
    except Exception as e:
        logger.error(f"!!! Ошибка в get_fights: {e}")
        import traceback
        traceback.print_exc()
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

# Обслуживание статических файлов фронтенда (для Railway)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Проверяем существует ли папка frontend/dist
frontend_dist_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")

if os.path.exists(frontend_dist_path):
    # Обслуживание статических файлов
    app.mount("/static", StaticFiles(directory=frontend_dist_path), name="static")
    
    # Обслуживание главной страницы
    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_dist_path, "index.html"))
    
    # Обслуживание всех остальных маршрутов фронтенда
    @app.get("/{full_path:path}")
    async def serve_frontend_routes(full_path: str):
        # Если это API запрос, пропускаем
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        # Проверяем существует ли файл
        file_path = os.path.join(frontend_dist_path, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Иначе возвращаем index.html для SPA
        return FileResponse(os.path.join(frontend_dist_path, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
