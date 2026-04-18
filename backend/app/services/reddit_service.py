from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import praw

from app.config import get_settings
from app.db import get_database
from app.models.domain import ContentItem, Engagement
from app.services.cache_service import CacheService
from app.services.demo_data import generate_score_history, generate_social_items
from app.services.sentiment_service import SentimentService
from app.utils.text import truncate


class RedditService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.cache = CacheService()
        self.db = get_database()
        self.sentiment = SentimentService()

    async def get_posts(self, ticker: str) -> list[ContentItem]:
        ticker = ticker.upper()
        if self.settings.demo_mode or not (self.settings.reddit_client_id and self.settings.reddit_client_secret):
            return [item for item in generate_social_items(ticker, generate_score_history(ticker)) if item.source == "reddit"]

        try:
            items = await asyncio.to_thread(self._fetch_live_posts, ticker)
            if items:
                serialized = [item.model_dump(mode="json") for item in items]
                await self.cache.set_cached_document("content_cache", f"reddit:{ticker}", {"items": serialized}, "reddit", ttl_minutes=30)
                await self._persist_items(items)
                return items
        except Exception:
            pass

        cached, _ = await self.cache.stale_or_none("content_cache", f"reddit:{ticker}")
        if cached:
            return [ContentItem.model_validate(item) for item in cached.get("items", [])]
        return [item for item in generate_social_items(ticker, generate_score_history(ticker)) if item.source == "reddit"]

    def _fetch_live_posts(self, ticker: str) -> list[ContentItem]:
        reddit = praw.Reddit(
            client_id=self.settings.reddit_client_id,
            client_secret=self.settings.reddit_client_secret,
            user_agent=self.settings.reddit_user_agent,
        )
        subreddit = reddit.subreddit("stocks+wallstreetbets+investing")
        items = []
        for submission in subreddit.search(ticker, sort="new", limit=6):
            text = truncate(f"{submission.title} {submission.selftext}", 260)
            items.append(
                ContentItem(
                    source="reddit",
                    ticker=ticker,
                    text=text,
                    author=str(submission.author or "reddit"),
                    url=f"https://reddit.com{submission.permalink}",
                    created_at=datetime.fromtimestamp(submission.created_utc, tz=timezone.utc),
                    engagement=Engagement(
                        likes=max(submission.score, 0),
                        comments=submission.num_comments,
                        shares=0,
                        score=submission.score,
                    ),
                    sentiment=self.sentiment.score_text(text),
                )
            )
        return items

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
