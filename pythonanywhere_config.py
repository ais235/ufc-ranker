# PythonAnywhere конфигурация для UFC Ranker

# Основные настройки
DEBUG = False
SECRET_KEY = 'your-secret-key-here'

# База данных SQLite (для PythonAnywhere)
DATABASE_URL = 'sqlite:///./ufc_ranker.db'

# CORS настройки для PythonAnywhere
ALLOWED_ORIGINS = [
    "https://yourusername.pythonanywhere.com",
    "http://yourusername.pythonanywhere.com",
    "https://www.yourusername.pythonanywhere.com",
    "http://www.yourusername.pythonanywhere.com"
]

# Настройки для статических файлов
STATIC_URL = '/static/'
STATIC_ROOT = '/home/yourusername/ufc-ranker/static/'

# Настройки медиа файлов
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/yourusername/ufc-ranker/media/'
