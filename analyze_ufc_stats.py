#!/usr/bin/env python3
"""
Анализ данных из проекта ufc.stats
Проверяем, есть ли реальная статистика в файле ufc_stats.rda
"""

import os
import subprocess
import sys

def install_r_packages():
    """Устанавливаем необходимые R пакеты"""
    packages = ['rpy2', 'pandas']
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Устанавливаем {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def analyze_ufc_stats():
    """Анализируем данные ufc.stats"""
    print("🥊 АНАЛИЗ ПРОЕКТА UFC.STATS")
    print("=" * 50)
    
    # Проверяем размер файла данных
    data_file = "temp_ufc_stats/data/ufc_stats.rda"
    if os.path.exists(data_file):
        file_size = os.path.getsize(data_file)
        print(f"📁 Файл данных: {data_file}")
        print(f"📊 Размер файла: {file_size:,} байт ({file_size/1024/1024:.1f} MB)")
        
        if file_size > 100000:  # Больше 100KB
            print("✅ Файл содержит значительный объем данных!")
        else:
            print("⚠️ Файл довольно маленький, возможно содержит только заголовки")
    else:
        print("❌ Файл данных не найден!")
        return
    
    # Пытаемся загрузить данные через R
    print("\n🔍 Попытка загрузки данных через R...")
    
    r_script = """
    # Загружаем данные
    load("temp_ufc_stats/data/ufc_stats.rda")
    
    # Выводим информацию о данных
    cat("Количество строк:", nrow(ufc_stats), "\\n")
    cat("Количество столбцов:", ncol(ufc_stats), "\\n")
    cat("Размер в памяти:", object.size(ufc_stats), "байт\\n")
    
    # Показываем первые несколько строк
    cat("\\nПервые 3 строки:\\n")
    print(head(ufc_stats, 3))
    
    # Показываем названия столбцов
    cat("\\nНазвания столбцов:\\n")
    print(colnames(ufc_stats))
    
    # Показываем уникальных бойцов
    if("fighter" %in% colnames(ufc_stats)) {
        cat("\\nКоличество уникальных бойцов:", length(unique(ufc_stats$fighter)), "\\n")
        cat("Первые 10 бойцов:\\n")
        print(head(unique(ufc_stats$fighter), 10))
    }
    
    # Показываем статистику по боям
    if("fight" %in% colnames(ufc_stats)) {
        cat("\\nКоличество уникальных боев:", length(unique(ufc_stats$fight)), "\\n")
    }
    """
    
    try:
        # Запускаем R скрипт
        result = subprocess.run(['R', '--slave', '-e', r_script], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print("✅ Данные успешно загружены!")
            print(result.stdout)
        else:
            print("❌ Ошибка при загрузке данных:")
            print(result.stderr)
            
    except FileNotFoundError:
        print("❌ R не установлен на системе")
        print("💡 Установите R с https://www.r-project.org/")
        
        # Альтернативный способ - пытаемся прочитать как бинарный файл
        print("\n🔍 Попытка анализа бинарного файла...")
        try:
            with open(data_file, 'rb') as f:
                content = f.read(1000)  # Читаем первые 1000 байт
                print(f"Первые 1000 байт (hex): {content[:100].hex()}")
                
                # Ищем текстовые строки
                text_content = content.decode('utf-8', errors='ignore')
                if 'fighter' in text_content.lower():
                    print("✅ Найдены данные о бойцах!")
                if 'strike' in text_content.lower():
                    print("✅ Найдены данные об ударах!")
                if 'ufc' in text_content.lower():
                    print("✅ Найдены данные UFC!")
                    
        except Exception as e:
            print(f"❌ Ошибка при чтении файла: {e}")

def main():
    print("🚀 Запуск анализа ufc.stats...")
    analyze_ufc_stats()
    print("\n✅ Анализ завершен!")

if __name__ == "__main__":
    main()
