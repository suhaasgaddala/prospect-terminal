from __future__ import annotations

from datetime import datetime, timezone

from apify_client import ApifyClient

from app.config import get_settings
from app.db import get_database
from app.models.domain import ContentItem, Engagement
from app.services.cache_service import CacheService
from app.services.demo_data import generate_score_history, generate_social_items
from app.services.sentiment_service import SentimentService
from app.utils.text import truncate


class XService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.cache = CacheService()
        self.db = get_database()
        self.sentiment = SentimentService()

    async def get_posts(self, ticker: str) -> list[ContentItem]:
        ticker = ticker.upper()
        if self.settings.demo_mode or not self.settings.apify_token:
            return [item for item in generate_social_items(ticker, generate_score_history(ticker)) if item.source == "x"]

        try:
            client = ApifyClient(self.settings.apify_token)
            run_input = {
                "searchTerms": [f"${ticker} OR {ticker} stock"],
                "maxTweets": 8,
                "sort": "Latest",
                "includeSearchTerms": False,
            }
            run = client.actor(self.settings.apify_twitter_actor_id).call(run_input=run_input)
            items = []
            for row in client.dataset(run["defaultDatasetId"]).iterate_items():
                text = truncate(row.get("full_text") or row.get("text") or "", 260)
                if not text:
                    continue
                created_at = row.get("created_at")
                items.append(
                    ContentItem(
                        source="x",
                        ticker=ticker,
                        text=text,
                        author=row.get("author", {}).get("userName", "x"),
                        url=row.get("url") or "",
                        created_at=datetime.fromisoformat(created_at.replace("Z", "+00:00")) if created_at else datetime.now(timezone.utc),
                        engagement=Engagement(
                            likes=row.get("favorite_count", 0),
                            comments=row.get("reply_count", 0),
                            shares=row.get("retweet_count", 0),
                            score=row.get("favorite_count", 0) + row.get("reply_count", 0) + row.get("retweet_count", 0),
                        ),
                        sentiment=self.sentiment.score_text(text),
                    )
                )
            if items:
                serialized = [item.model_dump(mode="json") for item in items]
                await self.cache.set_cached_document("content_cache", f"x:{ticker}", {"items": serialized}, "x", ttl_minutes=30)
                await self._persist_items(items)
                return items
        except Exception:
            pass

        cached, _ = await self.cache.stale_or_none("content_cache", f"x:{ticker}")
        if cached:
            return [ContentItem.model_validate(item) for item in cached.get("items", [])]
        return [item for item in generate_social_items(ticker, generate_score_history(ticker)) if item.source == "x"]

    async def _persist_items(self, items: list[ContentItem]) -> None:
        if not items:
            return
        collection = self.db["content_items"]
        for item in items:
            await collection.update_one(
                {"source": item.source, "ticker": item.ticker, "url": item.url},
                {"$set": item.model_dump(mode="json")},
                upsert=True,
            )
