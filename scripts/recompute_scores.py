#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.config import get_settings
from app.db import close_database
from app.services.scoring_service import ScoringService


async def main() -> None:
    settings = get_settings()
    scoring = ScoringService()
    for ticker in settings.demo_tickers:
        scores = await scoring.ensure_score_history(ticker, 365)
        print(f"recomputed {ticker}: {len(scores)} rows")
    await close_database()


if __name__ == "__main__":
    asyncio.run(main())
