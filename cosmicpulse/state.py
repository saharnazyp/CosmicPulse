import hashlib
import json
import os
from datetime import datetime, timezone

from .config import STATE_PATH

def load_state():
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            data.setdefault("published", [])
            return data
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return {"published": [], "last_success_utc": None}

def item_key(item):
    raw = (item.get("url") or item.get("headline_fa") or item.get("title") or "").strip().lower()
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH) or ".", exist_ok=True)
    state["last_success_utc"] = datetime.now(timezone.utc).isoformat()
    state["published"] = list(dict.fromkeys(state.get("published", [])))[-1000:]
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, STATE_PATH)
