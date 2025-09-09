#!/usr/bin/env python3
"""
Обновление дизайна HTML страниц
"""

import os
import shutil

def update_design():
    """Обновляет дизайн HTML страниц"""
    
    # Удаляем старые файлы
    if os.path.exists('category_pages'):
        shutil.rmtree('category_pages')
    
    # Импортируем и запускаем функцию
    from build_category_pages import build_pages
    build_pages()
    
    print("✅ Дизайн обновлен!")

if __name__ == "__main__":
    update_design()

