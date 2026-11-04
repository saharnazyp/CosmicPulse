import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
GEMINI_FALLBACK_MODELS = [
    model.strip()
    for model in os.getenv(
        "GEMINI_FALLBACK_MODELS",
        "gemini-3.7-flash,gemini-3.6-flash",
    ).split(",")
    if model.strip()
]
MAX_AGE_HOURS = int(os.getenv("MAX_AGE_HOURS", "48"))
MAX_ITEMS_PER_FEED = int(os.getenv("MAX_ITEMS_PER_FEED", "20"))
MAX_CANDIDATES = int(os.getenv("MAX_CANDIDATES", "80"))
MAX_NEWS_POSTS = int(os.getenv("MAX_NEWS_POSTS", "4"))
MAX_EDUCATIONAL_POSTS = int(os.getenv("MAX_EDUCATIONAL_POSTS", "1"))
STATE_PATH = os.getenv("STATE_PATH", "state/state.json")
FEEDS_PATH = os.getenv("FEEDS_PATH", "config/feeds.json")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "20"))
