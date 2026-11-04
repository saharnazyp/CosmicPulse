import logging
import os
import subprocess
import sys

from cosmicpulse.config import GEMINI_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from cosmicpulse.editor import create_editorial_package
from cosmicpulse.publisher import publish_package
from cosmicpulse.sources import collect_news, collect_social_signals
from cosmicpulse.state import item_key, load_state, save_state

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("cosmicpulse")


def persist_state():
    """Persist deduplication state between ephemeral GitHub-hosted runners."""
    if not os.getenv("GITHUB_ACTIONS"):
        log.info("Not running in GitHub Actions; state remains local.")
        return
    token = os.getenv("GITHUB_TOKEN", "")
    if not token:
        log.warning("GITHUB_TOKEN missing; deduplication state will not persist.")
        return

    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(
        ["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"],
        check=True,
    )
    subprocess.run(["git", "add", "state/state.json"], check=True)
    changed = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        check=False,
    )
    if changed.returncode == 0:
        log.info("No state changes to persist.")
        return
    if changed.returncode != 1:
        raise RuntimeError("Could not inspect staged state changes.")

    subprocess.run(
        ["git", "commit", "-m", "chore: update CosmicPulse publication state"],
        check=True,
    )
    repo = os.getenv("GITHUB_REPOSITORY", "")
    ref = os.getenv("GITHUB_REF_NAME", "main")
    if not repo:
        raise RuntimeError("GITHUB_REPOSITORY is missing; cannot persist state.")
    push_url = f"https://x-access-token:{token}@github.com/{repo}.git"
    subprocess.run(["git", "remote", "set-url", "origin", push_url], check=True)
    subprocess.run(["git", "push", "origin", f"HEAD:{ref}"], check=True)
    log.info("Publication state committed to branch %s.", ref)


def main():
    missing = [
        name for name, value in (
            ("GEMINI_API_KEY", GEMINI_API_KEY),
            ("TELEGRAM_BOT_TOKEN", TELEGRAM_BOT_TOKEN),
            ("TELEGRAM_CHAT_ID", TELEGRAM_CHAT_ID),
        ) if not value
    ]
    if missing:
        raise RuntimeError("Missing required GitHub Actions secrets: " + ", ".join(missing))

    log.info("Starting CosmicPulse 2.0 autopilot.")
    state = load_state()
    published = set(state.get("published", []))

    news = collect_news()
    social = collect_social_signals()
    log.info("Collected %d news candidates and %d social signals.", len(news), len(social))

    fresh = [item for item in news if item_key(item) not in published]
    log.info("%d candidates remain after deduplication.", len(fresh))
    # Educational content is still produced on quiet news days.
    package = create_editorial_package(fresh[:80], social)
    news_posts = package.get("news_posts", [])
    education_posts = package.get("educational_posts", [])
    if not news_posts and not education_posts:
        log.warning("Gemini produced no publishable posts; state remains unchanged.")
        return

    # Publish first. Only mark source items as published after the full package succeeds.
    publish_package(package, len(fresh), len(social))
    state.setdefault("published", [])
    selected_urls = {post.get("source_url") for post in news_posts if post.get("source_url")}
    selected_items = [item for item in fresh if item.get("url") in selected_urls]
    state["published"].extend(item_key(item) for item in selected_items)
    save_state(state)
    persist_state()
    log.info(
        "CosmicPulse 2.0 completed: %d news posts, %d educational posts.",
        len(news_posts),
        len(education_posts),
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log.exception("CosmicPulse 2.0 failed.")
        sys.exit(1)
