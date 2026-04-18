#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.config import get_settings
from app.db import close_database, get_database
from app.services.demo_data import (
    generate_filing,
    generate_macro_history,
    generate_news_items,
    generate_score_history,
    generate_social_items,
    generate_thesis,
    latest_quote_from_scores,
)


async def main() -> None:
    settings = get_settings()
    db = get_database()
    await db["quotes"].delete_many({})
    await db["price_bars"].delete_many({})
    await db["content_items"].delete_many({})
    await db["filings"].delete_many({})
    await db["macro_snapshots"].delete_many({})
    await db["daily_scores"].delete_many({})
    await db["theses"].delete_many({})

    macro_history = generate_macro_history(365)
    for snapshot in macro_history:
        await db["macro_snapshots"].update_one(
            {"as_of": snapshot.as_of.isoformat()},
            {"$set": snapshot.model_dump(mode="json")},
            upsert=True,
        )

    for ticker in settings.demo_tickers:
        scores = generate_score_history(ticker, 365)
        quote = latest_quote_from_scores(ticker, scores)
        social_items = generate_social_items(ticker, scores)
        news_items = generate_news_items(ticker, scores)
        filing = generate_filing(ticker, scores)
        thesis = generate_thesis(ticker, scores)

        await db["quotes"].update_one({"ticker": ticker}, {"$set": quote.model_dump(mode="json")}, upsert=True)
        await db["filings"].update_one({"ticker": ticker}, {"$set": filing.model_dump(mode="json")}, upsert=True)
        await db["theses"].update_one({"ticker": ticker}, {"$set": thesis.model_dump(mode="json")}, upsert=True)

        for score in scores:
            await db["daily_scores"].update_one(
                {"ticker": ticker, "date": score.date.isoformat()},
                {"$set": score.model_dump(mode="json")},
                upsert=True,
            )
            await db["price_bars"].update_one(
                {"ticker": ticker, "date": score.date.isoformat()},
                {
                    "$set": {
                        "ticker": ticker,
                        "date": score.date.isoformat(),
                        "close": score.price_close,
                        "open": round(score.price_close * 0.997, 2),
                    }
                },
                upsert=True,
            )

        for item in social_items + news_items:
            await db["content_items"].update_one(
                {"source": item.source, "ticker": item.ticker, "url": item.url},
                {"$set": item.model_dump(mode="json")},
                upsert=True,
            )

    print(f"Seeded Prospect Terminal demo dataset for {len(settings.demo_tickers)} tickers.")
    await close_database()


if __name__ == "__main__":
    asyncio.run(main())
