import os

# Токены
USER_TOKEN = os.getenv("USER_TOKEN")
GROUP_TOKEN = os.getenv("GROUP_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID", "0"))
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Настройки
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "30"))
PUBLISH_INTERVAL = int(os.getenv("PUBLISH_INTERVAL", "1800"))
BAN_HOURS = int(os.getenv("BAN_HOURS", "24"))

# Для Callback API
CONFIRMATION_CODE = os.getenv("CONFIRMATION_CODE", "")

# Файлы
PUBLISHED_FILE = "published.json"
BAN_FILE = "bans.json"
DB_PATH = "posts.db"

# Спам-фильтры
FORBIDDEN_WORDS = [
    "реклама", "реклам", "раскрутка", "накрутка",
    "магазин", "скидка", "акция", "распродажа",
    "заработок", "заработать", "биткоин", "крипта",
    "бесплатно", "предложение", "услуги", "услуг"
]

FORBIDDEN_LINKS = [
    "vk.com/app", "vk.com/market", "t.me", "telegram",
    "instagram", "instagram.com", "wa.me", "whatsapp",
    "youtube", "youtu.be"
]

# Ключевые слова анонимности
ANONYMOUS_KEYWORDS = [
    "анон", "анонимно", "аноним",
    "#анон", "#анонимно", "#аноним"
]
