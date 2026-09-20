import streamlit as st
import json
import os
from datetime import datetime
from news import fetch_all_feeds, parse_feed  # Import your existing functions

st.set_page_config(page_title="Nigerian News Aggregator", page_icon="📰", layout="wide")

st.title("📰 Latest Nigerian News Feed")
st.write("Real-time news aggregator pulling directly from top news outlets.")

# Refresh Button
col1, col2 = st.columns([1, 4])
with col1:
    if st.button("🔄 Fetch Latest News"):
        with st.spinner("Scraping latest feeds..."):
            import asyncio

            results = asyncio.run(fetch_all_feeds())
            all_articles = []
            for source_name, xml_content in results:
                articles = parse_feed(source_name, xml_content)
                all_articles.extend(articles)

            output = {
                "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_articles": len(all_articles),
                "articles": all_articles,
            }
            with open("nigerian_news_dataset.json", "w", encoding="utf-8") as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            st.success("Refreshed successfully!")

# Load stored dataset
if os.path.exists("nigerian_news_dataset.json"):
    with open("nigerian_news_dataset.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    st.caption(
        f"Last updated: **{data.get('collected_at', 'Unknown')}** | Total Articles: **{data.get('total_articles', 0)}**")

    # Source Filter Tabs/Radio
    sources = ["All", "Punch", "Vanguard", "Premium Times"]
    selected_source = st.radio("Filter Source:", sources, horizontal=True)

    articles = data.get("articles", [])
    if selected_source != "All":
        articles = [a for a in articles if a.get("source") == selected_source]

    st.markdown("---")

    # Render News Cards
    for article in articles:
        with st.container():
            st.subheader(article['headline'])
            st.caption(f"📍 **{article['source']}** | 🕒 {article.get('published', 'N/A')}")
            if article['summary']:
                st.write(article['summary'])
            st.markdown(f"[🔗 Read full article]({article['link']})")
            st.markdown("---")
else:
    st.info("No data found. Click 'Fetch Latest News' above to populate the feed!")
