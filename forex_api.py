"""
Live currency data via https://www.frankfurter.app — free, ECB-backed,
no API key required. Good enough for v1; swap in a paid provider later
if you need intraday/tick-level data.
"""
import datetime as dt
import httpx

BASE_URL = "https://api.frankfurter.app"


def _split_pair(pair: str):
    base, quote = pair.upper().split("/")
    return base, quote


async def get_rate(pair: str) -> float | None:
    """Latest rate for a single pair like 'EUR/USD'."""
    base, quote = _split_pair(pair)
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{BASE_URL}/latest", params={"from": base, "to": quote})
        resp.raise_for_status()
        data = resp.json()
        return data.get("rates", {}).get(quote)


async def get_rates(pairs: list[str]) -> dict[str, float]:
    """Latest rates for multiple pairs. Groups requests by base currency."""
    from collections import defaultdict

    by_base: dict[str, list[str]] = defaultdict(list)
    for pair in pairs:
        base, quote = _split_pair(pair)
        by_base[base].append(quote)

    results: dict[str, float] = {}
    async with httpx.AsyncClient(timeout=10) as client:
        for base, quotes in by_base.items():
            resp = await client.get(
                f"{BASE_URL}/latest", params={"from": base, "to": ",".join(quotes)}
            )
            resp.raise_for_status()
            data = resp.json()
            for quote, rate in data.get("rates", {}).items():
                results[f"{base}/{quote}"] = rate
    return results


async def get_trending(pairs: list[str]) -> list[dict]:
    """
    Percent change of each pair vs. the previous trading day's close.
    Returns a list of dicts sorted by absolute % change, descending.
    """
    yesterday = (dt.date.today() - dt.timedelta(days=3)).isoformat()  # buffer for weekends
    current = await get_rates(pairs)

    from collections import defaultdict

    by_base: dict[str, list[str]] = defaultdict(list)
    for pair in pairs:
        base, quote = _split_pair(pair)
        by_base[base].append(quote)

    previous: dict[str, float] = {}
    async with httpx.AsyncClient(timeout=10) as client:
        for base, quotes in by_base.items():
            resp = await client.get(
                f"{BASE_URL}/{yesterday}", params={"from": base, "to": ",".join(quotes)}
            )
            resp.raise_for_status()
            data = resp.json()
            for quote, rate in data.get("rates", {}).items():
                previous[f"{base}/{quote}"] = rate

    trending = []
    for pair in pairs:
        now_rate = current.get(pair)
        prev_rate = previous.get(pair)
        if now_rate is None or prev_rate is None or prev_rate == 0:
            continue
        pct_change = ((now_rate - prev_rate) / prev_rate) * 100
        trending.append({
            "pair": pair,
            "rate": now_rate,
            "prev_rate": prev_rate,
            "pct_change": pct_change,
        })

    trending.sort(key=lambda x: abs(x["pct_change"]), reverse=True)
    return trending
