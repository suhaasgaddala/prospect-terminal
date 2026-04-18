from __future__ import annotations

from datetime import timedelta
from typing import Any, Optional

from app.db import get_database
from app.utils.dates import utc_now


class CacheService:
    def __init__(self) -> None:
        self.db = get_database()

    async def get_cached_document(self, collection: str, key: str) -> Optional[dict[str, Any]]:
        return await self.db[collection].find_one({"key": key}, {"_id": 0})

    async def set_cached_document(
        self,
        collection: str,
        key: str,
        payload: dict[str, Any],
        source: str,
        ttl_minutes: int = 60,
    ) -> dict[str, Any]:
        now = utc_now()
        document = {
            "key": key,
            "source": source,
            "payload": payload,
            "fetched_at": now,
            "expires_at": now + timedelta(minutes=ttl_minutes),
        }
        await self.db[collection].update_one({"key": key}, {"$set": document}, upsert=True)
        return document

    async def get_payload(self, collection: str, key: str) -> Optional[dict[str, Any]]:
        cached = await self.get_cached_document(collection, key)
        if not cached:
            return None
        return cached.get("payload")

    async def stale_or_none(self, collection: str, key: str) -> tuple[Optional[dict[str, Any]], bool]:
        cached = await self.get_cached_document(collection, key)
        if not cached:
            return None, False
        expires_at = cached.get("expires_at")
        is_stale = bool(expires_at and expires_at < utc_now())
        return cached.get("payload"), is_stale
