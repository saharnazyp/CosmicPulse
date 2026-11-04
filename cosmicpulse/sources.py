import json
import logging
import re
import html
from datetime import datetime, timedelta, timezone

import feedparser
import requests

from .config import FEEDS_PATH, MAX_AGE_HOURS, MAX_ITEMS_PER_FEED, MAX_CANDIDATES, REQUEST_TIMEOUT

log = logging.getLogger("cosmicpulse.sources")
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "CosmicPulse/2.0 (+https://github.com/saharnazyp/CosmicPulse)"})

def clean(value):
    value = re.sub(r"<[^>]*>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(value)).strip()

def read_feeds():
    with open(FEEDS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("feeds", [])

def _published(entry):
    for key in ("published_parsed", "updated_parsed"):
        parsed = entry.get(key)
        if parsed:
            try:
                return datetime(*parsed[:6], tzinfo=timezone.utc)
            except (TypeError, ValueError):
                pass
    return None

def _image(entry):
    for key in ("media_content", "media_thumbnail"):
        for media in entry.get(key, []) or []:
            url = media.get("url")
            if url and url.startswith("https://"):
                return url
    for enclosure in entry.get("enclosures", []) or []:
        url = enclosure.get("href") or enclosure.get("url")
        typ = enclosure.get("type", "")
        if url and url.startswith("https://") and typ.startswith("image/"):
            return url
    summary = entry.get("summary", "") or ""
    match = re.search(r'<img[^>]+src=["\'](https://[^"\']+)["\']', summary, re.I)
    return match.group(1) if match else None

def collect_news():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=MAX_AGE_HOURS)
    collected, seen = [], set()
    for source in read_feeds():
        name, url = source.get("name", "Unknown"), source.get("url", "")
        if not url.startswith("https://"):
            log.warning("Skipping non-HTTPS feed: %s", name)
            continue
        try:
            parsed = feedparser.parse(url)
            if getattr(parsed, "bozo", False):
                log.warning("Feed warning [%s]: %s", name, parsed.bozo_exception)
            for entry in parsed.entries[:MAX_ITEMS_PER_FEED]:
                title = clean(entry.get("title", ""))
                link = (entry.get("link") or "").strip()
                if not title or not link.startswith("https://"):
                    continue
                published = _published(entry)
                if published and published < cutoff:
                    continue
                key = link.split("#")[0].rstrip("/")
                if key in seen:
                    continue
                seen.add(key)
                collected.append({
                    "source": name,
                    "title": title[:300],
                    "summary": clean(entry.get("summary", "") or entry.get("description", ""))[:1200],
                    "url": link,
                    "published_utc": published.isoformat() if published else None,
                    "image_url": _image(entry),
                })
        except Exception as exc:
            log.warning("Feed unavailable [%s]: %s", name, exc)
    collected.sort(key=lambda x: x.get("published_utc") or "", reverse=True)
    return collected[:MAX_CANDIDATES]

def collect_social_signals():
    # Optional source. A 403/429 must never stop the editorial pipeline.
    results = []
    for subreddit in ("space", "science", "astronomy", "Futurology"):
        try:
            response = SESSION.get(
                f"https://www.reddit.com/r/{subreddit}/hot.json?limit=8",
                timeout=REQUEST_TIMEOUT,
            )
            if response.status_code in (403, 429):
                log.info("Reddit throttled r/%s (HTTP %s); skipping.", subreddit, response.status_code)
                continue
            response.raise_for_status()
            for child in response.json().get("data", {}).get("children", []):
                post = child.get("data", {})
                permalink = post.get("permalink")
                if not permalink:
                    continue
                results.append({
                    "source": f"Reddit r/{subreddit}",
                    "title": clean(post.get("title", ""))[:250],
                    "url": "https://www.reddit.com" + permalink,
                    "score": post.get("score", 0),
                    "comments": post.get("num_comments", 0),
                    "evidence_type": "community_signal_not_scientific_evidence",
                })
        except Exception as exc:
            log.warning("Social signal source r/%s unavailable: %s", subreddit, exc)
    return results
