#!/usr/bin/env python3
"""
SQLAlchemy модели для UFC базы данных
"""

from sqlalchemy import Column, Integer, String, Date, Boolean, Float, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class WeightClass(Base):
    """Весовые категории"""
    __tablename__ = "weight_classes"
    
    id = Column(Integer, primary_key=True)
    name_ru = Column(String(100), nullable=False)
    name_en = Column(String(100))
    weight_min = Column(Integer)  # минимальный вес в кг
    weight_max = Column(Integer)  # максимальный вес в кг
    gender = Column(String(10), default='male')  # 'male', 'female'
    is_p4p = Column(Boolean, default=False)  # pound for pound
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    rankings = relationship("Ranking", back_populates="weight_class")
    upcoming_fights = relationship("UpcomingFight", back_populates="weight_class")


class Fighter(Base):
    """Бойцы"""
    __tablename__ = "fighters"
    
    id = Column(Integer, primary_key=True)
    name_ru = Column(String(100), nullable=False)
    name_en = Column(String(100))
    nickname = Column(String(100))
    country = Column(String(50))
    country_flag_url = Column(String(500))
    image_url = Column(String(500))
    profile_url = Column(String(500))  # URL профиля на fight.ru
    height = Column(Integer)  # в см
    weight = Column(Integer)  # в кг
    reach = Column(Integer)   # в см
    age = Column(Integer)
    birth_date = Column(Date)
    weight_class = Column(String(100))  # Весовая категория (Женский легчайший вес, Полутяжёлый вес и т.д.)
    win = Column(Integer, default=0)    # Количество побед
    draw = Column(Integer, default=0)   # Количество ничьих
    lose = Column(Integer, default=0)   # Количество поражений
    career = Column(String(100))        # Бойцовская организация (UFC, Bellator и т.д.)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    rankings = relationship("Ranking", back_populates="fighter")
    fight_record = relationship("FightRecord", back_populates="fighter", uselist=False)
    upcoming_fights_fighter1 = relationship("UpcomingFight", foreign_keys="UpcomingFight.fighter1_id", back_populates="fighter1")
    upcoming_fights_fighter2 = relationship("UpcomingFight", foreign_keys="UpcomingFight.fighter2_id", back_populates="fighter2")


class Ranking(Base):
    """Рейтинги бойцов по весовым категориям"""
    __tablename__ = "rankings"
    
    id = Column(Integer, primary_key=True)
    fighter_id = Column(Integer, ForeignKey('fighters.id'), nullable=False)
    weight_class_id = Column(Integer, ForeignKey('weight_classes.id'), nullable=False)
    rank_position = Column(Integer)  # позиция в рейтинге
    is_champion = Column(Boolean, default=False)
    rank_change = Column(Integer, default=0)  # изменение позиции (+1, -1, 0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    fighter = relationship("Fighter", back_populates="rankings")
    weight_class = relationship("WeightClass", back_populates="rankings")


class FightRecord(Base):
    """Боевые рекорды бойцов"""
    __tablename__ = "fight_records"
    
    id = Column(Integer, primary_key=True)
    fighter_id = Column(Integer, ForeignKey('fighters.id'), nullable=False, unique=True)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    no_contests = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    fighter = relationship("Fighter", back_populates="fight_record")
    
    @property
    def total_fights(self):
        """Общее количество боев"""
        return self.wins + self.losses + self.draws + self.no_contests
    
    @property
    def win_percentage(self):
        """Процент побед"""
        if self.total_fights == 0:
            return 0.0
        return round((self.wins / self.total_fights) * 100, 1)


class UpcomingFight(Base):
    """Предстоящие бои"""
    __tablename__ = "upcoming_fights"
    
    id = Column(Integer, primary_key=True)
    fighter1_id = Column(Integer, ForeignKey('fighters.id'), nullable=False)
    fighter2_id = Column(Integer, ForeignKey('fighters.id'), nullable=False)
    weight_class_id = Column(Integer, ForeignKey('weight_classes.id'), nullable=False)
    event_name = Column(String(200))
    event_date = Column(Date)
    location = Column(String(100))
    is_main_event = Column(Boolean, default=False)
    is_title_fight = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    fighter1 = relationship("Fighter", foreign_keys=[fighter1_id], back_populates="upcoming_fights_fighter1")
    fighter2 = relationship("Fighter", foreign_keys=[fighter2_id], back_populates="upcoming_fights_fighter2")
    weight_class = relationship("WeightClass", back_populates="upcoming_fights")


class Event(Base):
    """События UFC"""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    date = Column(Date)
    location = Column(String(100))
    venue = Column(String(100))
    description = Column(Text)
    image_url = Column(String(500))
    is_upcoming = Column(Boolean, default=True)
    attendance = Column(Integer, nullable=True)  # Количество зрителей
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    fights = relationship("Fight", back_populates="event")


class Fight(Base):
    """Бои UFC"""
    __tablename__ = "fights"
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    fighter1_id = Column(Integer, ForeignKey('fighters.id'), nullable=False)
    fighter2_id = Column(Integer, ForeignKey('fighters.id'), nullable=False)
    weight_class_id = Column(Integer, ForeignKey('weight_classes.id'), nullable=False)
    scheduled_rounds = Column(Integer, default=3)  # Запланированное количество раундов
    result = Column(String(50))  # Результат боя (KO, TKO, Decision, etc.)
    winner_id = Column(Integer, ForeignKey('fighters.id'))  # ID победителя
    fight_date = Column(Date)
    is_title_fight = Column(Boolean, default=False)
    is_main_event = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    event = relationship("Event", back_populates="fights")
    fighter1 = relationship("Fighter", foreign_keys=[fighter1_id])
    fighter2 = relationship("Fighter", foreign_keys=[fighter2_id])
    winner = relationship("Fighter", foreign_keys=[winner_id])
    weight_class = relationship("WeightClass")
    fight_stats = relationship("FightStats", back_populates="fight")


class FightStats(Base):
    """Детальная статистика боев по раундам (как в ufc.stats)"""
    __tablename__ = "fight_stats"
    
    id = Column(Integer, primary_key=True)
    fight_id = Column(Integer, ForeignKey('fights.id'), nullable=False)
    fighter_id = Column(Integer, ForeignKey('fighters.id'), nullable=False)
    round_number = Column(Integer, nullable=False)  # Номер раунда
    
    # Основная статистика
    knockdowns = Column(Integer, default=0)  # Нокдауны
    significant_strikes_landed = Column(Integer, default=0)  # Значимые удары (попали)
    significant_strikes_attempted = Column(Integer, default=0)  # Значимые удары (попытки)
    significant_strikes_rate = Column(Float, default=0.0)  # Процент попаданий
    
    total_strikes_landed = Column(Integer, default=0)  # Все удары (попали)
    total_strikes_attempted = Column(Integer, default=0)  # Все удары (попытки)
    
    # Тейкдауны
    takedown_successful = Column(Integer, default=0)  # Успешные тейкдауны
    takedown_attempted = Column(Integer, default=0)  # Попытки тейкдаунов
    takedown_rate = Column(Float, default=0.0)  # Процент успешных тейкдаунов
    
    # Субмиссии и реверсалы
    submission_attempt = Column(Integer, default=0)  # Попытки субмиссий
    reversals = Column(Integer, default=0)  # Реверсалы
    
    # Удары по частям тела
    head_landed = Column(Integer, default=0)  # Удары в голову (попали)
    head_attempted = Column(Integer, default=0)  # Удары в голову (попытки)
    body_landed = Column(Integer, default=0)  # Удары по корпусу (попали)
    body_attempted = Column(Integer, default=0)  # Удары по корпусу (попытки)
    leg_landed = Column(Integer, default=0)  # Лоу-кики (попали)
    leg_attempted = Column(Integer, default=0)  # Лоу-кики (попытки)
    
    # Удары по дистанции
    distance_landed = Column(Integer, default=0)  # Удары на дистанции (попали)
    distance_attempted = Column(Integer, default=0)  # Удары на дистанции (попытки)
    clinch_landed = Column(Integer, default=0)  # Удары в клинче (попали)
    clinch_attempted = Column(Integer, default=0)  # Удары в клинче (попытки)
    ground_landed = Column(Integer, default=0)  # Удары в партере (попали)
    ground_attempted = Column(Integer, default=0)  # Удары в партере (попытки)
    
    # Результат и время
    result = Column(String(50))  # Результат раунда/боя
    last_round = Column(Boolean, default=False)  # Последний раунд боя
    time = Column(String(10))  # Время в раунде (например, "4:32")
    winner = Column(String(1))  # Победитель раунда (W/L)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    fight = relationship("Fight", back_populates="fight_stats")
    fighter = relationship("Fighter")
    
    # Вычисляемые поля
    @property
    def significant_strikes_rate_calculated(self):
        """Вычисляет процент значимых ударов"""
        if self.significant_strikes_attempted == 0:
            return 0.0
        return round((self.significant_strikes_landed / self.significant_strikes_attempted) * 100, 2)
    
    @property
    def takedown_rate_calculated(self):
        """Вычисляет процент успешных тейкдаунов"""
        if self.takedown_attempted == 0:
            return 0.0
        return round((self.takedown_successful / self.takedown_attempted) * 100, 2)
