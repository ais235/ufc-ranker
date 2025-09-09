"""
Парсеры для UFC данных
"""

from .base_parser import BaseParser
from .ufc_rankings import UFCRankingsParser
from .fighter_profiles import FighterProfilesParser
from .upcoming_cards import UpcomingCardsParser

__all__ = [
    'BaseParser',
    'UFCRankingsParser', 
    'FighterProfilesParser',
    'UpcomingCardsParser'
]
