#!/usr/bin/env python3
"""
Парсер профилей бойцов UFC
"""

import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from .base_parser import BaseParser
from database.models import Fighter, FightRecord
from database.config import SessionLocal


class FighterProfilesParser(BaseParser):
    """Парсер профилей бойцов"""
    
    def __init__(self, cache_dir: str = ".cache/fighters"):
        super().__init__(cache_dir)
        self.base_url = "https://fight.ru"
    
    def extract_profile_data(self, profile_html: str) -> Dict[str, str]:
        """Извлекает данные профиля из HTML"""
        soup = self.parse_html(profile_html)
        
        # Изображение
        image_url = self._extract_image_url(soup)
        
        # Имена
        name_ru, name_en = self._extract_names(soup)
        
        # Страна и флаг
        country_name, country_flag = self._extract_country_info(soup)
        
        # Боевой рекорд
        fight_score = self._extract_fight_score(soup)
        
        # Физические данные
        height, weight, reach, age, nickname = self._extract_physical_data(soup)
        
        return {
            'image_url': image_url,
            'name_ru': name_ru,
            'name_en': name_en,
            'country_name': country_name,
            'country_flag': country_flag,
            'fight_score': fight_score,
            'height': height,
            'weight': weight,
            'reach': reach,
            'age': age,
            'nickname': nickname,
        }
    
    def _extract_image_url(self, soup: BeautifulSoup) -> str:
        """Извлекает URL изображения"""
        # Пробуем разные селекторы для изображения
        selectors = [
            'img[itemprop="url"]',
            'meta[property="og:image"]',
            'img.fighter-photo',
            'img.profile-photo'
        ]
        
        for selector in selectors:
            if selector.startswith('meta'):
                element = soup.select_one(selector)
                if element and element.get('content'):
                    return element['content']
            else:
                element = soup.select_one(selector)
                if element and element.get('src'):
                    return element['src']
        
        # Если ничего не найдено, берем первое изображение
        first_img = soup.find('img')
        if first_img and first_img.get('src'):
            return first_img['src']
        
        return ''
    
    def _extract_names(self, soup: BeautifulSoup) -> tuple[str, str]:
        """Извлекает русское и английское имена"""
        name_ru = ''
        name_en = ''
        
        # Русское имя из h1 с классом fighter-name
        h1_name = soup.find('h1', class_='fighter-name')
        if h1_name:
            name_ru = self.clean_text(h1_name.get_text())
        
        # Английское имя из div с классом fighter-latin-name
        latin_name = soup.find('div', class_='fighter-latin-name')
        if latin_name:
            name_en = self.clean_text(latin_name.get_text())
        
        # Альтернативные способы поиска имен
        if not name_ru:
            h1 = soup.find(['h1', 'h2'])
            if h1:
                name_ru = self.clean_text(h1.get_text())
        
        if not name_en:
            en_candidates = [
                soup.find(class_='fighter-eng-name'),
                soup.find('div', class_='eng-name'),
                soup.find('span', class_='eng-name'),
            ]
            
            for cand in en_candidates:
                if cand and self.clean_text(cand.get_text()):
                    text = self.clean_text(cand.get_text())
                    if len(text) < 50 and re.search(r'^[A-Za-z\s\.\-\']+$', text):
                        name_en = text
                        break
        
        return name_ru, name_en
    
    def _extract_country_info(self, soup: BeautifulSoup) -> tuple[str, str]:
        """Извлекает информацию о стране"""
        country_name = ''
        country_flag = ''
        
        # Название страны
        cn = soup.find(class_='fighter-country-name')
        if cn:
            country_name = self.clean_text(cn.get_text())
        
        # Флаг страны
        cf = soup.find(class_='fighter-country-flag')
        if cf:
            flag_img = cf.find('img')
            if flag_img and flag_img.get('src'):
                country_flag = flag_img['src']
        
        return country_name, country_flag
    
    def _extract_fight_score(self, soup: BeautifulSoup) -> str:
        """Извлекает боевой рекорд"""
        fs = soup.find(class_='fight-score')
        if fs:
            return self.clean_text(fs.get_text())
        return ''
    
    def _extract_physical_data(self, soup: BeautifulSoup) -> tuple[str, str, str, str, str]:
        """Извлекает физические данные бойца"""
        height = ''
        weight = ''
        reach = ''
        age = ''
        nickname = ''
        
        # Ищем данные в структуре <li><span class="text">Label</span><span class="sub">Value</span></li>
        for li in soup.find_all('li'):
            text_span = li.find('span', class_='text')
            sub_span = li.find('span', class_='sub')
            
            if not text_span or not sub_span:
                continue
            
            label = self.clean_text(text_span.get_text())
            value = self.clean_text(sub_span.get_text())
            
            if not label or not value or len(value) > 100:
                continue
            
            label_lower = label.lower()
            
            if 'рост' in label_lower and 'вес' in label_lower:
                # Рост / Вес в одном поле
                if ' / ' in value:
                    parts = value.split(' / ')
                    if len(parts) >= 2:
                        height = parts[0].strip()
                        weight = parts[1].strip()
            elif 'рост' in label_lower:
                height = value
            elif 'вес' in label_lower:
                weight = value
            elif 'размах рук' in label_lower:
                reach = value
            elif 'возраст' in label_lower:
                age = value
            elif 'ник' in label_lower:
                nickname = value
        
        # Дополнительный поиск в meta тегах
        if not height:
            height_meta = soup.find('meta', {'itemprop': 'height'})
            if height_meta and height_meta.get('content'):
                height = self.clean_text(height_meta['content'])
        
        if not weight:
            weight_meta = soup.find('meta', {'itemprop': 'weight'})
            if weight_meta and weight_meta.get('content'):
                weight = self.clean_text(weight_meta['content'])
        
        if not age:
            birth_meta = soup.find('meta', {'itemprop': 'birthDate'})
            if birth_meta and birth_meta.get('content'):
                age = birth_meta['content']
        
        return height, weight, reach, age, nickname
    
    def parse_fighter_profile(self, profile_url: str) -> Optional[Dict]:
        """Парсит профиль конкретного бойца"""
        if not profile_url:
            return None
        
        html = self.fetch(profile_url)
        if not html:
            return None
        
        return self.extract_profile_data(html)
    
    def update_fighters_from_rankings(self) -> None:
        """Обновляет профили бойцов из рейтингов"""
        db = SessionLocal()
        try:
            # Получаем всех бойцов без полных профилей
            fighters = db.query(Fighter).filter(
                Fighter.image_url.is_(None) | (Fighter.image_url == '')
            ).all()
            
            print(f"🔄 Обновляем профили {len(fighters)} бойцов...")
            
            for i, fighter in enumerate(fighters, 1):
                print(f"   {i}/{len(fighters)}: {fighter.name_ru}")
                
                if not fighter.profile_url:
                    continue
                
                profile_data = self.parse_fighter_profile(fighter.profile_url)
                if not profile_data:
                    continue
                
                # Обновляем данные бойца
                fighter.name_en = profile_data.get('name_en') or fighter.name_en
                fighter.nickname = profile_data.get('nickname') or fighter.nickname
                fighter.country = profile_data.get('country_name') or fighter.country
                fighter.country_flag_url = profile_data.get('country_flag') or fighter.country_flag_url
                fighter.image_url = profile_data.get('image_url') or fighter.image_url
                
                # Обновляем физические данные
                if profile_data.get('height'):
                    fighter.height = self._parse_height(profile_data['height'])
                if profile_data.get('weight'):
                    fighter.weight = self._parse_weight(profile_data['weight'])
                if profile_data.get('reach'):
                    fighter.reach = self._parse_reach(profile_data['reach'])
                if profile_data.get('age'):
                    fighter.age = self._parse_age(profile_data['age'])
                
                # Обновляем боевой рекорд
                if profile_data.get('fight_score'):
                    self._update_fight_record(fighter, profile_data['fight_score'])
            
            db.commit()
            print("✅ Профили бойцов обновлены")
            
        except Exception as e:
            db.rollback()
            print(f"❌ Ошибка при обновлении профилей: {e}")
        finally:
            db.close()
    
    def _parse_height(self, height_str: str) -> Optional[int]:
        """Парсит рост в сантиметры"""
        if not height_str:
            return None
        
        # Ищем числа в строке
        numbers = re.findall(r'\d+', height_str)
        if numbers:
            return int(numbers[0])
        return None
    
    def _parse_weight(self, weight_str: str) -> Optional[int]:
        """Парсит вес в килограммы"""
        if not weight_str:
            return None
        
        # Ищем числа в строке
        numbers = re.findall(r'\d+', weight_str)
        if numbers:
            return int(numbers[0])
        return None
    
    def _parse_reach(self, reach_str: str) -> Optional[int]:
        """Парсит размах рук в сантиметры"""
        if not reach_str:
            return None
        
        # Ищем числа в строке
        numbers = re.findall(r'\d+', reach_str)
        if numbers:
            return int(numbers[0])
        return None
    
    def _parse_age(self, age_str: str) -> Optional[int]:
        """Парсит возраст"""
        if not age_str:
            return None
        
        # Ищем числа в строке
        numbers = re.findall(r'\d+', age_str)
        if numbers:
            return int(numbers[0])
        return None
    
    def _update_fight_record(self, fighter: Fighter, fight_score: str) -> None:
        """Обновляет боевой рекорд бойца"""
        if not fight_score:
            return
        
        # Парсим рекорд (например: "25-5-0")
        parts = fight_score.split('-')
        if len(parts) >= 3:
            try:
                wins = int(parts[0])
                losses = int(parts[1])
                draws = int(parts[2])
                
                # Создаем или обновляем рекорд
                record = fighter.fight_record
                if not record:
                    record = FightRecord(fighter_id=fighter.id)
                    fighter.fight_record = record
                
                record.wins = wins
                record.losses = losses
                record.draws = draws
                
            except ValueError:
                pass
    
    def parse(self, *args, **kwargs) -> None:
        """Основной метод парсинга"""
        print("🥊 Обновление профилей бойцов...")
        self.update_fighters_from_rankings()













