#!/usr/bin/env python3
"""
Парсер предстоящих кардов UFC
"""

from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from .base_parser import BaseParser
from database.models import Fighter, WeightClass, UpcomingFight, Event
from database.config import SessionLocal


class UpcomingCardsParser(BaseParser):
    """Парсер предстоящих кардов UFC"""
    
    def __init__(self, cache_dir: str = ".cache/cards"):
        super().__init__(cache_dir)
        self.base_url = "https://www.ufc.com/events"
    
    def parse_upcoming_events(self, html: str) -> List[Dict]:
        """Парсит предстоящие события из HTML"""
        soup = self.parse_html(html)
        events = []
        
        # Ищем карточки событий
        event_cards = soup.find_all(['div', 'article'], class_=lambda x: x and 'event' in x.lower())
        
        for card in event_cards:
            event_data = self._extract_event_data(card)
            if event_data:
                events.append(event_data)
        
        return events
    
    def _extract_event_data(self, card) -> Optional[Dict]:
        """Извлекает данные события из карточки"""
        try:
            # Название события
            title_elem = card.find(['h2', 'h3', 'h4'], class_=lambda x: x and 'title' in x.lower())
            if not title_elem:
                title_elem = card.find(['h2', 'h3', 'h4'])
            
            event_name = self.clean_text(title_elem.get_text()) if title_elem else ''
            
            # Дата события
            date_elem = card.find(class_=lambda x: x and 'date' in x.lower())
            event_date = self.clean_text(date_elem.get_text()) if date_elem else ''
            
            # Место проведения
            location_elem = card.find(class_=lambda x: x and 'location' in x.lower())
            location = self.clean_text(location_elem.get_text()) if location_elem else ''
            
            # Ссылка на событие
            link_elem = card.find('a')
            event_url = link_elem['href'] if link_elem and link_elem.get('href') else ''
            if event_url and not event_url.startswith('http'):
                event_url = f"https://www.ufc.com{event_url}"
            
            # Изображение события
            img_elem = card.find('img')
            image_url = img_elem['src'] if img_elem and img_elem.get('src') else ''
            
            if not event_name:
                return None
            
            return {
                'name': event_name,
                'date': event_date,
                'location': location,
                'url': event_url,
                'image_url': image_url
            }
            
        except Exception as e:
            print(f"❌ Ошибка при извлечении данных события: {e}")
            return None
    
    def parse_event_details(self, event_url: str) -> Optional[Dict]:
        """Парсит детали конкретного события"""
        if not event_url:
            return None
        
        html = self.fetch(event_url)
        if not html:
            return None
        
        soup = self.parse_html(html)
        
        # Извлекаем бои
        fights = self._extract_fights_from_event(soup)
        
        return {
            'fights': fights
        }
    
    def _extract_fights_from_event(self, soup: BeautifulSoup) -> List[Dict]:
        """Извлекает бои из страницы события"""
        fights = []
        
        # Ищем карточки боев
        fight_cards = soup.find_all(['div', 'article'], class_=lambda x: x and 'fight' in x.lower())
        
        for card in fight_cards:
            fight_data = self._extract_fight_data(card)
            if fight_data:
                fights.append(fight_data)
        
        return fights
    
    def _extract_fight_data(self, card) -> Optional[Dict]:
        """Извлекает данные боя из карточки"""
        try:
            # Имена бойцов
            fighter_names = []
            name_elems = card.find_all(['h3', 'h4', 'span'], class_=lambda x: x and 'name' in x.lower())
            
            for elem in name_elems:
                name = self.clean_text(elem.get_text())
                if name and len(name) > 2:
                    fighter_names.append(name)
            
            if len(fighter_names) < 2:
                return None
            
            # Весовая категория
            weight_class_elem = card.find(class_=lambda x: x and ('weight' in x.lower() or 'class' in x.lower()))
            weight_class = self.clean_text(weight_class_elem.get_text()) if weight_class_elem else ''
            
            # Тип боя (главный, титульный и т.д.)
            fight_type_elem = card.find(class_=lambda x: x and ('main' in x.lower() or 'title' in x.lower()))
            fight_type = self.clean_text(fight_type_elem.get_text()) if fight_type_elem else ''
            
            is_main_event = 'main' in fight_type.lower()
            is_title_fight = 'title' in fight_type.lower() or 'championship' in fight_type.lower()
            
            return {
                'fighter1_name': fighter_names[0],
                'fighter2_name': fighter_names[1],
                'weight_class': weight_class,
                'is_main_event': is_main_event,
                'is_title_fight': is_title_fight
            }
            
        except Exception as e:
            print(f"❌ Ошибка при извлечении данных боя: {e}")
            return None
    
    def save_to_database(self, events: List[Dict]) -> None:
        """Сохраняет события в базу данных"""
        db = SessionLocal()
        try:
            for event_data in events:
                # Создаем или получаем событие
                event = db.query(Event).filter(
                    Event.name == event_data['name']
                ).first()
                
                if not event:
                    event = Event(
                        name=event_data['name'],
                        location=event_data.get('location'),
                        image_url=event_data.get('image_url'),
                        is_upcoming=True
                    )
                    db.add(event)
                    db.flush()
                
                # Парсим детали события
                if event_data.get('url'):
                    details = self.parse_event_details(event_data['url'])
                    if details and details.get('fights'):
                        self._save_fights_to_database(db, event.id, details['fights'])
            
            db.commit()
            print(f"✅ Сохранено {len(events)} событий в БД")
            
        except Exception as e:
            db.rollback()
            print(f"❌ Ошибка при сохранении событий: {e}")
        finally:
            db.close()
    
    def _save_fights_to_database(self, db, event_id: int, fights: List[Dict]) -> None:
        """Сохраняет бои в базу данных"""
        for fight_data in fights:
            # Находим бойцов
            fighter1 = db.query(Fighter).filter(
                Fighter.name_ru.ilike(f"%{fight_data['fighter1_name']}%")
            ).first()
            
            fighter2 = db.query(Fighter).filter(
                Fighter.name_ru.ilike(f"%{fight_data['fighter2_name']}%")
            ).first()
            
            if not fighter1 or not fighter2:
                continue
            
            # Находим весовую категорию
            weight_class = db.query(WeightClass).filter(
                WeightClass.name_ru.ilike(f"%{fight_data['weight_class']}%")
            ).first()
            
            if not weight_class:
                continue
            
            # Создаем бой
            fight = UpcomingFight(
                fighter1_id=fighter1.id,
                fighter2_id=fighter2.id,
                weight_class_id=weight_class.id,
                is_main_event=fight_data.get('is_main_event', False),
                is_title_fight=fight_data.get('is_title_fight', False)
            )
            db.add(fight)
    
    def parse(self, use_cache: bool = True) -> List[Dict]:
        """Основной метод парсинга"""
        print("🥊 Парсинг предстоящих кардов UFC...")
        
        html = self.fetch(self.base_url, use_cache=use_cache)
        if not html:
            print("❌ Не удалось загрузить страницу событий")
            return []
        
        events = self.parse_upcoming_events(html)
        print(f"✅ Найдено событий: {len(events)}")
        
        # Сохраняем в БД
        self.save_to_database(events)
        
        return events













