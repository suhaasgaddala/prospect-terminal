# Prospect Terminal

Prospect Terminal is a demo-ready market intelligence MVP for a fintech hackathon. It ingests sentiment and market context from X, Reddit, news, SEC filings, and macro signals, turns them into an explainable stock score, generates an AI thesis, and supports simple daily backtesting against historical scores.

## Stack

- Frontend: Next.js, TypeScript, Tailwind, shadcn-style UI primitives, Recharts
- Backend: FastAPI, Python
- Database: MongoDB
- Data adapters: yfinance, Finnhub, Reddit, Apify, SEC, FRED
- Thesis generation: OpenAI with deterministic fallback

## Repo tree

```text
prospect-terminal/
├── README.md
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   ├── app/
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── main.py
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   └── utils/
│   └── tests/
├── frontend/
│   ├── .env.example
│   ├── app/
│   ├── components/
│   ├── hooks/
│   ├── lib/
│   ├── services/
│   ├── types/
│   └── package.json
└── scripts/
    ├── generate_frontend_types.sh
    ├── recompute_scores.py
    ├── refresh_data.py
    └── seed_demo_data.py
```

## Local setup

### 1. Start MongoDB

```bash
docker run --name prospect-mongo -p 27017:27017 -d mongo:7
```

### 2. Start the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### 3. Start the frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### 4. Seed demo data

```bash
cd /path/to/prospect-terminal
backend/.venv/bin/python scripts/seed_demo_data.py
```

Open the app at [http://localhost:3000](http://localhost:3000) and the API at [http://localhost:8000/docs](http://localhost:8000/docs).

## Environment variables

### Backend

Defined in [backend/.env.example](/Users/suhaasgaddala/prospect-terminal/backend/.env.example).

- `DEMO_MODE=true` keeps the full product working with deterministic demo data.
- `USE_CACHED_DATA=true` prefers Mongo-cached content when live providers are flaky.
- `OPENAI_API_KEY` enables live thesis generation.
- `FINNHUB_API_KEY`, `FRED_API_KEY`, `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, and `APIFY_TOKEN` enable richer live ingestion.

### Frontend

Defined in [frontend/.env.example](/Users/suhaasgaddala/prospect-terminal/frontend/.env.example).

- `API_BASE_URL` and `NEXT_PUBLIC_API_BASE_URL` should point to the FastAPI server.

## Demo flow

1. Seed the demo data.
2. Open the home page and click a demo ticker like `NVDA` or `PLTR`.
3. Review the score, thesis, social/news/filing cards, and the score-vs-price chart.
4. Open `/backtest?ticker=NVDA` to compare the score strategy with buy-and-hold.

## Useful commands

```bash
# Refresh all tracked tickers from live providers or cache
backend/.venv/bin/python scripts/refresh_data.py

# Recompute stored daily scores
backend/.venv/bin/python scripts/recompute_scores.py

# Regenerate frontend API types from FastAPI OpenAPI
bash scripts/generate_frontend_types.sh

# Run backend tests
cd backend && .venv/bin/pytest

# Typecheck and build the frontend
cd frontend && npm run typecheck && npm run build
```

## Product notes

- The scoring pipeline is deterministic and explainable so historical backtests do not depend on repeated LLM calls.
- Social sources are normalized into one canonical schema and stored with source tags and timestamps.
- Expensive fetches are cached in Mongo, and the app falls back to cached/demo data for resilient demos.
- Backtesting is intentionally daily, single-ticker, and strategy-limited to stay mathematically clean for a hackathon MVP.
