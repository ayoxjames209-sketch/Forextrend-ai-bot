"""
Forex news via https://newsapi.org (free tier: 100 requests/day).
Get a key at https://newsapi.org/register and set NEWS_API_KEY in your env.
Swap this module out if you'd rather use a dedicated Forex news provider
(e.g. Finnhub, Marketaux, ForexLive RSS).
"""
import httpx
import config

BASE_URL = "https://newsapi.org/v2/everything"


async def get_forex_news(limit: int = 5) -> list[dict]:
    if not config.NEWS_API_KEY:
        return []

    params = {
        "q": "forex OR \"currency market\" OR \"exchange rate\"",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": limit,
        "apiKey": config.NEWS_API_KEY,
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(BASE_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    articles = []
    for a in data.get("articles", [])[:limit]:
        articles.append({
            "title": a.get("title"),
            "source": (a.get("source") or {}).get("name"),
            "url": a.get("url"),
            "published_at": a.get("publishedAt"),
        })
    return articles
