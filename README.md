# Cosmic Pulse | نبض کیهان — Gemini Edition

A scheduled Persian-language editorial briefing bot for a private Telegram group.

## What this MVP does
- Collects recent items from selected science, space, technology and AI RSS feeds.
- Collects a limited set of public Reddit hot-post signals when Reddit allows access.
- Sends the collected source data to Google Gemini for editorial triage and content drafting.
- Produces Persian topic summaries, hooks, short-form video scripts, voiceover text, English subtitles, and English image/video prompts.
- Posts the report to a Telegram group.
- Runs daily at 09:00 Asia/Tehran using GitHub Actions.

## 1. Create the GitHub repository
Create a repository named `cosmic-pulse` and upload all files from this project, preserving folder structure.

## 2. Add GitHub Actions secrets
Go to **Repository → Settings → Secrets and variables → Actions → New repository secret**.

Add:
- `GEMINI_API_KEY` — API key created in Google AI Studio.
- `TELEGRAM_BOT_TOKEN` — token from BotFather.
- `TELEGRAM_CHAT_ID` — numeric ID of the Telegram group, usually a negative number starting with `-100`.

Do not paste keys into source files, issues, commits, or chats.

## 3. Find the Telegram group ID
1. Add the bot to your group and allow it to send messages. Making it an administrator is a straightforward option.
2. Send a normal message in the group after the bot has been added.
3. Open this address in your browser, replacing `TOKEN` with your bot token:
   `https://api.telegram.org/botTOKEN/getUpdates`
4. In the JSON response, find `message` → `chat` → `id`.
5. Copy that numeric ID into the GitHub secret `TELEGRAM_CHAT_ID`.

Keep the bot token private. If it is exposed, revoke/regenerate it through BotFather. If `getUpdates` is empty, send another new group message and refresh. You may need to disable bot privacy using BotFather `/setprivacy` or make the bot an administrator so group messages appear in updates.

## 4. Run a test
1. Open the repository's **Actions** tab.
2. Select **Cosmic Pulse Daily Editorial Briefing**.
3. Click **Run workflow**.
4. Wait for the job to finish and check the Telegram group.
5. If it fails, open the workflow run and inspect the step logs. Never share logs containing secrets.

## Schedule
The workflow runs at 05:30 UTC, equivalent to 09:00 in Tehran (UTC+3:30). GitHub scheduled workflows can start a little later during periods of high load.

## Change Gemini model
The workflow currently sets `GEMINI_MODEL: gemini-2.5-flash`. If that model is unavailable for your API project, replace it with a model currently listed as available in your Google AI Studio/API account.

## Important limitations
- Gemini API billing/quotas are separate from a consumer Gemini subscription. Check the API project's quota and billing in Google AI Studio/Google Cloud.
- RSS coverage depends on each publisher's feed and availability.
- Reddit access is best-effort and can be throttled.
- This MVP does not have unrestricted Instagram, TikTok, YouTube, or X analytics access. It does not claim comprehensive platform-wide trend detection.
- Competitor analysis is only a placeholder until real competitor accounts and accessible data sources are configured.
- Scientific credibility scores are model-assisted editorial triage, not peer review. Verify important claims and original research before publication.
- The bot posts drafts to Telegram only. It does not automatically publish to Instagram.

## Add competitors
Edit `config/competitors.json` and replace the example entry with real public competitor accounts and URLs. The current MVP passes this list to Gemini as context; it does not scrape private account analytics.
