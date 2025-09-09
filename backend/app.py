#!/usr/bin/env python3
"""
FastAPI приложение для UFC Ranker
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import get_db, init_database
from database.models import Fighter, WeightClass, Ranking, FightRecord, UpcomingFight, Event
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
    
    class Config:
        from_attributes = True

class WeightClassResponse(BaseModel):
    id: int
    name_ru: str
    name_en: Optional[str] = None
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
    return fighters

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
    return weight_classes

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
    total_fighters = db.query(Fighter).count()
    total_weight_classes = db.query(WeightClass).count()
    total_upcoming_fights = db.query(UpcomingFight).count()
    
    # Топ стран по количеству бойцов
    country_stats = db.query(
        Fighter.country,
        db.func.count(Fighter.id).label('count')
    ).filter(
        Fighter.country.isnot(None)
    ).group_by(Fighter.country).order_by(
        db.func.count(Fighter.id).desc()
    ).limit(10).all()
    
    return {
        "total_fighters": total_fighters,
        "total_weight_classes": total_weight_classes,
        "total_upcoming_fights": total_upcoming_fights,
        "top_countries": [{"country": country, "count": count} for country, count in country_stats]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
