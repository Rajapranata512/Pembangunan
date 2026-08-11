"""
news_scraper.py — Lightweight news scraper via Google News RSS.
Tidak memerlukan API key tambahan. Menggunakan RSS feed publik.
Hasil di-cache di database selama 24 jam.
"""
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import html
import re
from typing import Optional


def fetch_news_headlines(
    region_name: str,
    province: str = "",
    max_results: int = 10,
    lang: str = "id",
) -> list[dict]:
    """
    Fetch news headlines from Google News RSS for a given region.

    Returns list of dicts: [{"title": "...", "link": "...", "pub_date": "..."}]
    """
    # Build search query
    keywords = [region_name]
    if province:
        keywords.append(province)
    keywords.append("investasi OR ekonomi OR pembangunan OR properti")

    query = " ".join(keywords)
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl={lang}&gl=ID&ceid=ID:{lang}"

    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()

        root = ET.fromstring(xml_data)
        items = []

        for item in root.findall('.//item')[:max_results]:
            title_el = item.find('title')
            link_el = item.find('link')
            pubdate_el = item.find('pubDate')

            title = html.unescape(title_el.text) if title_el is not None and title_el.text else ""
            link = link_el.text if link_el is not None and link_el.text else ""
            pub_date = pubdate_el.text if pubdate_el is not None and pubdate_el.text else ""

            # Clean title — remove source suffix like "- Kompas.com"
            title = re.sub(r'\s*-\s*[^-]+$', '', title).strip()

            if title:
                items.append({
                    "title": title,
                    "link": link,
                    "pub_date": pub_date,
                })

        return items

    except Exception as e:
        print(f"[News] Failed to fetch for '{region_name}': {e}")
        return []


def get_headlines_text(region_name: str, province: str = "", max_results: int = 10) -> list[str]:
    """Get just the headline titles as a list of strings."""
    items = fetch_news_headlines(region_name, province, max_results)
    return [item["title"] for item in items]
