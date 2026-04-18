from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Prospect Terminal API", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    api_prefix: str = Field(default="/api", alias="API_PREFIX")
    port: int = Field(default=8000, alias="PORT")

    mongodb_uri: str = Field(default="mongodb://localhost:27017", alias="MONGODB_URI")
    mongodb_db: str = Field(default="prospect_terminal", alias="MONGODB_DB")

    demo_mode: bool = Field(default=True, alias="DEMO_MODE")
    use_cached_data: bool = Field(default=True, alias="USE_CACHED_DATA")

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL")

    finnhub_api_key: str = Field(default="", alias="FINNHUB_API_KEY")
    fred_api_key: str = Field(default="", alias="FRED_API_KEY")
    reddit_client_id: str = Field(default="", alias="REDDIT_CLIENT_ID")
    reddit_client_secret: str = Field(default="", alias="REDDIT_CLIENT_SECRET")
    reddit_user_agent: str = Field(default="prospect-terminal", alias="REDDIT_USER_AGENT")
    apify_token: str = Field(default="", alias="APIFY_TOKEN")
    apify_twitter_actor_id: str = Field(default="61RPP7dywgiy0JPD0", alias="APIFY_TWITTER_ACTOR_ID")
    sec_user_agent: str = Field(default="Prospect Terminal team@example.com", alias="SEC_USER_AGENT")

    demo_tickers: List[str] = [
        "AAPL",
        "MSFT",
        "NVDA",
        "TSLA",
        "AMD",
        "META",
        "AMZN",
        "GOOGL",
        "PLTR",
        "NFLX",
        "JPM",
        "SMCI",
    ]

    def provider_flags(self) -> dict[str, bool]:
        return {
            "finnhub": bool(self.finnhub_api_key),
            "fred": bool(self.fred_api_key),
            "reddit": bool(self.reddit_client_id and self.reddit_client_secret),
            "apify": bool(self.apify_token),
            "openai": bool(self.openai_api_key),
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
