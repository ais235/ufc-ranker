# PythonAnywhere конфигурация для UFC Ranker

# Основные настройки
DEBUG = False
SECRET_KEY = 'your-secret-key-here'

# База данных SQLite (для PythonAnywhere)
DATABASE_URL = 'sqlite:///./ufc_ranker.db'

# CORS настройки для PythonAnywhere
ALLOWED_ORIGINS = [
    "https://voltfighters.ru",
    "https://www.voltfighters.ru",
    "http://voltfighters.ru",
    "http://www.voltfighters.ru",
    "https://yourusername.pythonanywhere.com",
    "http://yourusername.pythonanywhere.com"
]

# Настройки для статических файлов
STATIC_URL = '/static/'
STATIC_ROOT = '/home/yourusername/ufc-ranker/static/'

# Настройки медиа файлов
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/yourusername/ufc-ranker/media/'

# Домен сайта
SITE_DOMAIN = 'voltfighters.ru'
SITE_URL = 'https://voltfighters.ru'
