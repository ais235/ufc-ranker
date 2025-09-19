#!/usr/bin/env python3
"""
Менеджер источников данных с системой приоритетов
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
from .ufc_official_api import UFCOfficialAPIParser
from .ufc_stats_enhanced import UFCStatsEnhanced
from .ufc_rankings import UFCRankingsParser
from .fighter_profiles import FighterProfilesParser
from .upcoming_cards import UpcomingCardsParser
from database.config import SessionLocal
from database.models import Fighter, WeightClass, Ranking, Event, Fight, FightStats


class DataSourcePriority(Enum):
    """Приоритеты источников данных"""
    HIGH = 1      # Официальные источники
    MEDIUM = 2    # Проверенные сторонние источники
    LOW = 3       # Резервные источники


class DataSourceManager:
    """Менеджер источников данных с системой приоритетов"""
    
    def __init__(self):
        self.sources = {
            'ufc_official': {
                'parser': UFCOfficialAPIParser(),
                'priority': DataSourcePriority.HIGH,
                'enabled': True,
                'last_update': None,
                'success_rate': 0.0
            },
            'ufc_stats': {
                'parser': UFCStatsEnhanced(),
                'priority': DataSourcePriority.HIGH,
                'enabled': True,
                'last_update': None,
                'success_rate': 0.0
            },
            'fight_ru_rankings': {
                'parser': UFCRankingsParser(),
                'priority': DataSourcePriority.MEDIUM,
                'enabled': True,
                'last_update': None,
                'success_rate': 0.0
            },
            'fight_ru_profiles': {
                'parser': FighterProfilesParser(),
                'priority': DataSourcePriority.MEDIUM,
                'enabled': True,
                'last_update': None,
                'success_rate': 0.0
            },
            'fight_ru_cards': {
                'parser': UpcomingCardsParser(),
                'priority': DataSourcePriority.MEDIUM,
                'enabled': True,
                'last_update': None,
                'success_rate': 0.0
            }
        }
    
    def get_rankings(self, force_refresh: bool = False) -> Dict[str, List[Dict]]:
        """Получает рейтинги с приоритетных источников"""
        print("🏆 Получение рейтингов с приоритетных источников...")
        
        # Сортируем источники по приоритету
        ranking_sources = [
            (name, config) for name, config in self.sources.items()
            if config['enabled'] and hasattr(config['parser'], 'get_rankings')
        ]
        ranking_sources.sort(key=lambda x: x[1]['priority'].value)
        
        for source_name, config in ranking_sources:
            try:
                print(f"  🔄 Пробуем {source_name}...")
                
                if hasattr(config['parser'], 'get_rankings'):
                    rankings = config['parser'].get_rankings()
                else:
                    rankings = config['parser'].parse()
                
                if rankings and len(rankings) > 0:
                    print(f"  ✅ {source_name}: получено {len(rankings)} категорий")
                    self._update_source_stats(source_name, True)
                    return rankings
                else:
                    print(f"  ⚠️ {source_name}: нет данных")
                    self._update_source_stats(source_name, False)
                    
            except Exception as e:
                print(f"  ❌ {source_name}: ошибка - {e}")
                self._update_source_stats(source_name, False)
        
        print("❌ Не удалось получить рейтинги ни с одного источника")
        return {}
    
    def get_fighters(self, force_refresh: bool = False) -> List[Dict]:
        """Получает бойцов с приоритетных источников"""
        print("👥 Получение бойцов с приоритетных источников...")
        
        # Сортируем источники по приоритету
        fighter_sources = [
            (name, config) for name, config in self.sources.items()
            if config['enabled'] and hasattr(config['parser'], 'get_fighters')
        ]
        fighter_sources.sort(key=lambda x: x[1]['priority'].value)
        
        for source_name, config in fighter_sources:
            try:
                print(f"  🔄 Пробуем {source_name}...")
                
                if hasattr(config['parser'], 'get_fighters'):
                    fighters = config['parser'].get_fighters()
                else:
                    # Для парсеров без get_fighters, пробуем parse
                    data = config['parser'].parse()
                    fighters = data.get('fighters', []) if isinstance(data, dict) else []
                
                if fighters and len(fighters) > 0:
                    print(f"  ✅ {source_name}: получено {len(fighters)} бойцов")
                    self._update_source_stats(source_name, True)
                    return fighters
                else:
                    print(f"  ⚠️ {source_name}: нет данных")
                    self._update_source_stats(source_name, False)
                    
            except Exception as e:
                print(f"  ❌ {source_name}: ошибка - {e}")
                self._update_source_stats(source_name, False)
        
        print("❌ Не удалось получить бойцов ни с одного источника")
        return []
    
    def get_events(self, force_refresh: bool = False) -> List[Dict]:
        """Получает события с приоритетных источников"""
        print("🎪 Получение событий с приоритетных источников...")
        
        # Сортируем источники по приоритету
        event_sources = [
            (name, config) for name, config in self.sources.items()
            if config['enabled'] and hasattr(config['parser'], 'get_events')
        ]
        event_sources.sort(key=lambda x: x[1]['priority'].value)
        
        for source_name, config in event_sources:
            try:
                print(f"  🔄 Пробуем {source_name}...")
                
                if hasattr(config['parser'], 'get_events'):
                    events = config['parser'].get_events()
                else:
                    # Для парсеров без get_events, пробуем parse
                    data = config['parser'].parse()
                    events = data.get('events', []) if isinstance(data, dict) else []
                
                if events and len(events) > 0:
                    print(f"  ✅ {source_name}: получено {len(events)} событий")
                    self._update_source_stats(source_name, True)
                    return events
                else:
                    print(f"  ⚠️ {source_name}: нет данных")
                    self._update_source_stats(source_name, False)
                    
            except Exception as e:
                print(f"  ❌ {source_name}: ошибка - {e}")
                self._update_source_stats(source_name, False)
        
        print("❌ Не удалось получить события ни с одного источника")
        return []
    
    def get_fight_stats(self, force_refresh: bool = False) -> List[Dict]:
        """Получает статистику боев с приоритетных источников"""
        print("📊 Получение статистики боев с приоритетных источников...")
        
        # Сортируем источники по приоритету
        stats_sources = [
            (name, config) for name, config in self.sources.items()
            if config['enabled'] and 'stats' in name.lower()
        ]
        stats_sources.sort(key=lambda x: x[1]['priority'].value)
        
        for source_name, config in stats_sources:
            try:
                print(f"  🔄 Пробуем {source_name}...")
                
                data = config['parser'].parse()
                fight_stats = data.get('fight_stats', []) if isinstance(data, dict) else []
                
                if fight_stats and len(fight_stats) > 0:
                    print(f"  ✅ {source_name}: получено {len(fight_stats)} записей статистики")
                    self._update_source_stats(source_name, True)
                    return fight_stats
                else:
                    print(f"  ⚠️ {source_name}: нет данных")
                    self._update_source_stats(source_name, False)
                    
            except Exception as e:
                print(f"  ❌ {source_name}: ошибка - {e}")
                self._update_source_stats(source_name, False)
        
        print("❌ Не удалось получить статистику боев ни с одного источника")
        return []
    
    def update_all_data(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Обновляет все данные с приоритетных источников"""
        print("🔄 Обновление всех данных...")
        
        results = {
            'rankings': self.get_rankings(force_refresh),
            'fighters': self.get_fighters(force_refresh),
            'events': self.get_events(force_refresh),
            'fight_stats': self.get_fight_stats(force_refresh),
            'sources_status': self.get_sources_status()
        }
        
        return results
    
    def _update_source_stats(self, source_name: str, success: bool) -> None:
        """Обновляет статистику источника"""
        if source_name in self.sources:
            self.sources[source_name]['last_update'] = datetime.now()
            
            # Простое обновление success_rate
            current_rate = self.sources[source_name]['success_rate']
            if success:
                new_rate = min(1.0, current_rate + 0.1)
            else:
                new_rate = max(0.0, current_rate - 0.05)
            
            self.sources[source_name]['success_rate'] = new_rate
    
    def get_sources_status(self) -> Dict[str, Dict]:
        """Возвращает статус всех источников"""
        status = {}
        for name, config in self.sources.items():
            status[name] = {
                'enabled': config['enabled'],
                'priority': config['priority'].name,
                'last_update': config['last_update'].isoformat() if config['last_update'] else None,
                'success_rate': config['success_rate']
            }
        return status
    
    def enable_source(self, source_name: str) -> bool:
        """Включает источник данных"""
        if source_name in self.sources:
            self.sources[source_name]['enabled'] = True
            print(f"✅ Источник {source_name} включен")
            return True
        else:
            print(f"❌ Источник {source_name} не найден")
            return False
    
    def disable_source(self, source_name: str) -> bool:
        """Отключает источник данных"""
        if source_name in self.sources:
            self.sources[source_name]['enabled'] = False
            print(f"⏸️ Источник {source_name} отключен")
            return True
        else:
            print(f"❌ Источник {source_name} не найден")
            return False
    
    def set_source_priority(self, source_name: str, priority: DataSourcePriority) -> bool:
        """Устанавливает приоритет источника"""
        if source_name in self.sources:
            self.sources[source_name]['priority'] = priority
            print(f"📊 Приоритет источника {source_name} установлен на {priority.name}")
            return True
        else:
            print(f"❌ Источник {source_name} не найден")
            return False
    
    def get_recommended_sources(self) -> List[str]:
        """Возвращает рекомендуемые источники на основе статистики"""
        # Сортируем по success_rate и priority
        sorted_sources = sorted(
            self.sources.items(),
            key=lambda x: (x[1]['success_rate'], -x[1]['priority'].value),
            reverse=True
        )
        
        return [name for name, config in sorted_sources if config['enabled']]
    
    def validate_data_quality(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Валидирует качество данных"""
        quality_scores = {}
        
        # Проверяем рейтинги
        if 'rankings' in data and data['rankings']:
            rankings = data['rankings']
            total_categories = len(rankings)
            categories_with_fighters = sum(1 for cat in rankings.values() if len(cat) > 0)
            quality_scores['rankings'] = (categories_with_fighters / total_categories) * 100 if total_categories > 0 else 0
        
        # Проверяем бойцов
        if 'fighters' in data and data['fighters']:
            fighters = data['fighters']
            fighters_with_complete_data = sum(1 for f in fighters if f.get('name') and f.get('country'))
            quality_scores['fighters'] = (fighters_with_complete_data / len(fighters)) * 100 if fighters else 0
        
        # Проверяем события
        if 'events' in data and data['events']:
            events = data['events']
            events_with_complete_data = sum(1 for e in events if e.get('name') and e.get('date'))
            quality_scores['events'] = (events_with_complete_data / len(events)) * 100 if events else 0
        
        return quality_scores

