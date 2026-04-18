from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import close_database
from app.routes import backtest, filing, health, leaderboard, macro, news, quote, score_history, social, stock


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await close_database()


settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.api_prefix, tags=["health"])
app.include_router(quote.router, prefix=settings.api_prefix, tags=["quote"])
app.include_router(stock.router, prefix=settings.api_prefix, tags=["stock"])
app.include_router(score_history.router, prefix=settings.api_prefix, tags=["score-history"])
app.include_router(leaderboard.router, prefix=settings.api_prefix, tags=["leaderboard"])
app.include_router(macro.router, prefix=settings.api_prefix, tags=["macro"])
app.include_router(backtest.router, prefix=settings.api_prefix, tags=["backtest"])
app.include_router(social.router, prefix=settings.api_prefix, tags=["social"])
app.include_router(news.router, prefix=settings.api_prefix, tags=["news"])
app.include_router(filing.router, prefix=settings.api_prefix, tags=["filing"])


@app.get("/")
async def root() -> dict[str, str]:
    return {"name": settings.app_name, "docs": "/docs"}
