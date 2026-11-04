# CosmicPulse 2.0 | نبض کیهان

A Persian-language science, astronomy, space and technology editorial autopilot for Telegram.

## What it does
- Collects recent items from a configurable set of RSS feeds.
- Optionally reads public Reddit posts as conversation signals; Reddit failures never stop the pipeline.
- Filters already-published source URLs using a small JSON state file committed back to the repository after successful publication.
- Uses Gemini to prepare up to four news posts and one educational/science-fact post in Persian.
- Keeps source URLs tied to the exact feed items collected. Generated or unsupported URLs are discarded.
- Publishes each post to Telegram, including editorial notes, voiceover copy, English subtitle lines and visual prompts.
- Runs daily at 09:00 Tehran time (05:30 UTC), and can also be started manually from Actions.

## Required GitHub Actions secrets
In **Settings → Secrets and variables → Actions**, configure:

- `GEMINI_API_KEY`: Google AI Studio API key. A consumer Gemini subscription does not automatically include Gemini API quota.
- `TELEGRAM_BOT_TOKEN`: token from BotFather.
- `TELEGRAM_CHAT_ID`: destination group or channel ID. The bot must be allowed to post there.

The workflow uses the built-in `GITHUB_TOKEN` to persist the publication state. In **Settings → Actions → General → Workflow permissions**, allow read and write permissions if repository policy requires it.

Never place credentials in source files or commit them.

## Run a test
1. Open **Actions → CosmicPulse 2.0 Daily Autopilot**.
2. Select **Run workflow**.
3. Inspect the job logs and confirm the messages arrived in the Telegram destination.
4. If the workflow cannot commit `state/state.json`, check workflow write permissions.

## Configuration
Edit `config/feeds.json` to add or remove RSS sources. Each feed needs a descriptive `name` and an HTTPS `url`.

Environment variables:
- `GEMINI_MODEL`: defaults to `gemini-3.8-flash`; change it to a model actually available to your API project.
- `MAX_AGE_HOURS`: feed recency window, default 48.
- `MAX_NEWS_POSTS`: maximum news posts per run, default 4.
- `MAX_EDUCATIONAL_POSTS`: maximum educational posts per run, default 1.

## Reliability and editorial safeguards
- Feed failures and Reddit 403/429 responses are logged and skipped.
- Gemini retries temporary 408/429/5xx errors with exponential backoff.
- JSON output is validated before publishing.
- Only source URLs that match collected feed items are retained.
- Source links and evidence status are included in news posts.
- The model's confidence is editorial triage, not scientific peer review. Autopilot publication still requires occasional human review of quality and source coverage.

## Current boundaries
- This version publishes text-first Telegram posts. It does not generate image files, publish to Instagram, or provide authenticated social analytics.
- Visual prompts are included for later image/video production; they are not rendered automatically.
- Reddit is best-effort and is not treated as scientific evidence.
- The JSON publication ledger is suitable for a single scheduled workflow. Do not run multiple independent publishers against the same state file.
- If Telegram partially accepts a multi-message package and a later message fails, the next run may repeat part of that package. A future release can add per-message delivery receipts.
