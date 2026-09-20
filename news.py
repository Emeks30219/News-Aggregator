import asyncio
import aiohttp
import xml.etree.ElementTree as ET
import json
import re
from datetime import datetime

NEWS_SOURCES = {
    "Punch": "https://punchng.com/feed/",
    "Vanguard": "https://www.vanguardngr.com/feed/",
    "Premium Times": "https://www.premiumtimesng.com/feed",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


async def fetch_feed(session, name, url):
    try:
        async with session.get(url) as response:
            if response.status != 200:
                print(f"[{name}] returned status {response.status}, skipping")
                return name, None
            content = await response.text()
            return name, content
    except Exception as e:
        print(f"[{name}] failed: {type(e).__name__} - {e}")
        return name, None


async def fetch_all_feeds():
    # Set timeout and headers globally on the session
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(headers=HEADERS, timeout=timeout) as session:
        tasks = [fetch_feed(session, name, url) for name, url in NEWS_SOURCES.items()]
        results = await asyncio.gather(*tasks)
        return results


def clean_text(raw_text):
    if raw_text is None:
        return ""
    text = re.sub(r'<[^>]+>', '', raw_text)
    text = text.replace('&amp;', '&').replace('&quot;', '"').replace('&#039;', "'")
    return text.strip()


def parse_feed(source_name, xml_content):
    articles = []
    if xml_content is None:
        return articles

    try:
        root = ET.fromstring(xml_content)

        # Look for items regardless of namespace structure
        for item in root.findall(".//item"):
            title_el = item.find("title")
            link_el = item.find("link")
            desc_el = item.find("description")
            date_el = item.find("pubDate")

            title = clean_text(title_el.text) if title_el is not None else ""
            link = link_el.text.strip() if link_el is not None and link_el.text else ""
            summary = clean_text(desc_el.text) if desc_el is not None else ""
            published = date_el.text.strip() if date_el is not None and date_el.text else ""

            if title:
                articles.append({
                    "source": source_name,
                    "headline": title,
                    "summary": summary,
                    "link": link,
                    "published": published,
                })
    except ET.ParseError as e:
        print(f"[{source_name}] XML Parse Error: {e}")

    return articles


def main():
    print("Fetching feeds concurrently...")
    results = asyncio.run(fetch_all_feeds())

    all_articles = []
    for source_name, xml_content in results:
        articles = parse_feed(source_name, xml_content)
        print(f"[{source_name}] collected {len(articles)} articles")
        all_articles.extend(articles)

    output = {
        "collected_at": datetime.now().isoformat(),
        "total_articles": len(all_articles),
        "articles": all_articles,
    }

    with open("nigerian_news_dataset.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(all_articles)} articles to nigerian_news_dataset.json")


if __name__ == "__main__":
    main()
