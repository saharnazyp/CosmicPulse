import html
import logging
import re
import time
import requests

from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, REQUEST_TIMEOUT

log = logging.getLogger("cosmicpulse.publisher")

def esc(value):
    return html.escape(str(value or ""), quote=True)

def _send(method, payload):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise RuntimeError("Missing Telegram configuration.")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}"
    response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
    if not response.ok:
        raise RuntimeError(f"Telegram HTTP {response.status_code}: {response.text[:400]}")
    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API rejected request: {data}")
    return data

def _split(text, limit=3900):
    parts, current = [], ""
    for paragraph in text.split("\n\n"):
        candidate = (current + "\n\n" + paragraph).strip()
        if len(candidate) > limit and current:
            parts.append(current)
            current = paragraph
        else:
            current = candidate
    if current:
        parts.append(current)
    return parts

def send_text(text):
    for part in _split(text):
        _send("sendMessage", {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": part,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        })
        time.sleep(0.4)

def _source_line(name, url):
    if url and url.startswith("https://"):
        return f'\n\n🔗 <a href="{esc(url)}">{esc(name or "منبع اصلی")}</a>'
    return "\n\n⚠️ لینک منبع در داده‌های ورودی موجود نبود."

def publish_news(post, index):
    text = (
        f"🌌 <b>نبض کیهان | خبر {index}</b>\n"
        f"📂 {esc(post.get('category'))}\n\n"
        f"<b>{esc(post.get('headline_fa'))}</b>\n\n"
        f"{esc(post.get('summary_fa'))}\n\n"
        f"<b>چرا مهم است؟</b> {esc(post.get('why_it_matters'))}\n"
        f"🔬 <b>وضعیت شواهد:</b> {esc(post.get('evidence_status'))}\n"
        f"📊 <b>ارزیابی تحریریه:</b> {esc(post.get('confidence', 'نامشخص'))}/100"
        + _source_line(post.get("source_name"), post.get("source_url"))
    )
    send_text(text)
    voice = post.get("voiceover_fa")
    if voice:
        send_text("🎙 <b>متن گویندگی پیشنهادی</b>\n" + esc(voice))
    subtitles = post.get("english_subtitles") or []
    if subtitles:
        send_text("🇬🇧 <b>English subtitles</b>\n" + esc("\n".join(subtitles[:8])))
    prompt = post.get("visual_prompt_en")
    if prompt:
        send_text("🎨 <b>Visual prompt</b>\n<code>" + esc(prompt[:2500]) + "</code>")

def publish_educational(post, index):
    text = (
        f"🧠 <b>یک دقیقه علم | {index}</b>\n"
        f"📂 {esc(post.get('category'))}\n\n"
        f"<b>{esc(post.get('headline_fa'))}</b>\n\n"
        f"{esc(post.get('body_fa'))}\n\n"
        f"💡 <b>می‌دانستید؟</b> {esc(post.get('did_you_know'))}"
    )
    if post.get("source_note"):
        text += "\n\n📚 <b>یادداشت منبع:</b> " + esc(post["source_note"])
    send_text(text)
    if post.get("voiceover_fa"):
        send_text("🎙 <b>متن گویندگی</b>\n" + esc(post["voiceover_fa"]))
    if post.get("visual_prompt_en"):
        send_text("🎨 <b>Visual prompt</b>\n<code>" + esc(post["visual_prompt_en"][:2500]) + "</code>")

def publish_package(package, news_count, social_count):
    header = (
        "🌌 <b>CosmicPulse 2.0 | نبض کیهان</b>\n"
        "🛰 <b>گزارش روزانه تحریریه</b>\n"
        f"📡 {news_count} خبر و {social_count} سیگنال اجتماعی بررسی شد.\n\n"
        + esc(package.get("editor_note") or "گزیده امروز دنیای علم و فناوری")
    )
    send_text(header)
    for i, post in enumerate(package.get("news_posts", []), 1):
        publish_news(post, i)
    for i, post in enumerate(package.get("educational_posts", []), 1):
        publish_educational(post, i)
    watch = package.get("watchlist") or []
    if watch:
        send_text("🔭 <b>در رصد روزهای آینده</b>\n" + esc("\n".join("• " + x for x in watch[:6])))
    send_text("✨ <i>CosmicPulse | کنجکاوی، تا بی‌نهایت.</i>")
