
# 📰 News-Aggregator

A real-time Nigerian news aggregator that scrapes RSS feeds from major news outlets, parses them, and displays them in a clean, filterable Streamlit dashboard.

**🔗 Live demo:** [news-aggregator-v1.streamlit.app](https://news-aggregator-v1.streamlit.app/)

---

## Overview

News-Aggregator concurrently pulls RSS feeds from top Nigerian news sources, parses the raw XML into structured articles, caches the result as a local JSON dataset, and renders it through an interactive Streamlit UI with source filtering.

**Current sources:**
- [Punch](https://punchng.com/feed/)
- [Vanguard](https://www.vanguardngr.com/feed/)
- [Premium Times](https://www.premiumtimesng.com/feed)

## Features

- ⚡ **Async scraping** — fetches all RSS feeds concurrently with `aiohttp` instead of one at a time
- 🧹 **Clean parsing** — strips HTML tags and decodes HTML entities from raw feed content
- 💾 **Local caching** — stores the latest pull in `nigerian_news_dataset.json` so the app has data on load, not just after a manual refresh
- 🔍 **Source filtering** — toggle between "All", "Punch", "Vanguard", and "Premium Times" via radio buttons
- 🔄 **One-click refresh** — re-scrape all sources on demand from the UI
- 🛡️ **Fault-tolerant** — a failed or slow feed (timeout, non-200 response, malformed XML) is skipped without crashing the whole run

## Tech Stack

| Layer | Tool |
|---|---|
| UI | Streamlit |
| Async HTTP | aiohttp |
| XML parsing | `xml.etree.ElementTree` (stdlib) |
| Data storage | JSON (flat file) |

## Project Structure

```
News-Aggregator/
├── app.py                       # Streamlit UI — renders articles, handles refresh + filtering
├── news.py                      # Scraping logic — async fetch, parse, clean, save
├── requirements.txt             # streamlit, requests, aiohttp
└── nigerian_news_dataset.json   # Generated on first run/refresh (not committed)
```

## How It Works

1. `news.py` defines `NEWS_SOURCES`, a dict of outlet name → RSS feed URL.
2. `fetch_all_feeds()` opens a single `aiohttp` session and fires off a `fetch_feed()` request per source concurrently via `asyncio.gather`.
3. `parse_feed()` walks the returned XML for `<item>` elements and extracts headline, summary, link, and publish date, running `clean_text()` to strip tags/entities from the summary.
4. Results are combined into a single JSON payload with a timestamp and article count, then written to `nigerian_news_dataset.json`.
5. `app.py` loads that JSON on page load (or after you click **Fetch Latest News**) and renders each article as a card, with a radio filter to narrow by source.

## Running Locally

**Requirements:** Python 3.9+

```bash
# Clone the repo
git clone https://github.com/Emeks30219/News-Aggregator.git
cd News-Aggregator

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app opens at `http://localhost:8501`. Click **🔄 Fetch Latest News** to run the first scrape — the dataset file doesn't exist until then.

You can also run the scraper standalone, without the UI:

```bash
python news.py
```

This populates `nigerian_news_dataset.json` directly from the command line.

## Deployment

Deployed on [Streamlit Community Cloud](https://streamlit.io/cloud), pointed at `app.py` on the `main` branch. To deploy your own fork:

1. Push the repo to your GitHub account.
2. Go to [share.streamlit.io](https://share.streamlit.io), connect your GitHub, and select the repo.
3. Set the main file path to `app.py`.
4. Deploy — Streamlit installs `requirements.txt` automatically.

## Known Limitations / Roadmap

- No scheduled/background refresh yet — data only updates when a user clicks the button, so the dataset can go stale between visits.
- No deduplication across refreshes — re-fetching overwrites rather than merges/dedupes against the previous dataset.
- No persistent database — JSON file storage means data doesn't survive a Streamlit Cloud container restart.
- Feed list is hardcoded — adding a new source currently means editing `NEWS_SOURCES` in `news.py` directly.

Planned improvements: swap flat JSON for a lightweight DB (SQLite), add a scheduled refresh (cron / GitHub Actions), and add keyword search across headlines.

## License

No license specified yet — add one (e.g. MIT) if you intend this to be reused by others.
