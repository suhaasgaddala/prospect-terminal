#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.config import get_settings
from app.db import close_database
from app.services.macro_service import MacroService
from app.services.market_data_service import MarketDataService
from app.services.news_service import NewsService
from app.services.reddit_service import RedditService
from app.services.scoring_service import ScoringService
from app.services.sec_service import SECService
from app.services.thesis_service import ThesisService
from app.services.x_service import XService


async def main() -> None:
    settings = get_settings()
    market = MarketDataService()
    news = NewsService()
    reddit = RedditService()
    x_service = XService()
    sec = SECService()
    macro = MacroService()
    scoring = ScoringService()
    thesis = ThesisService()

    macro_snapshot = await macro.get_snapshot()
    print(f"macro {macro_snapshot.regime} {macro_snapshot.score}")

    for ticker in settings.demo_tickers:
        await market.get_quote(ticker)
        await market.get_price_history(ticker, "1y")
        headlines = await news.get_news(ticker)
        social = await x_service.get_posts(ticker) + await reddit.get_posts(ticker)
        filing = await sec.get_filing(ticker)
        history = await scoring.ensure_score_history(ticker, 365)
        await thesis.get_thesis(ticker, history[-1], headlines, social[:6], filing, macro_snapshot, history)
        print(f"refreshed {ticker}")

    await close_database()


if __name__ == "__main__":
    asyncio.run(main())
