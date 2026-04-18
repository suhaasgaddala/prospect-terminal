export type SentimentLabel = "bullish" | "bearish" | "neutral";
export type ThesisRating = "bullish" | "neutral" | "bearish";

export interface Engagement {
  likes: number;
  comments: number;
  shares: number;
  score: number;
}

export interface Sentiment {
  label: SentimentLabel;
  score: number;
}

export interface ContentItem {
  source: "x" | "reddit" | "news";
  ticker: string;
  text: string;
  author: string;
  url: string;
  created_at: string;
  engagement: Engagement;
  sentiment: Sentiment;
  title?: string | null;
  published_at?: string | null;
}

export interface Quote {
  ticker: string;
  company_name: string;
  price: number;
  previous_close: number;
  daily_change: number;
  daily_change_percent: number;
  currency: string;
  market_state: string;
  as_of: string;
  source: string;
  is_stale: boolean;
}

export interface MacroFactor {
  name: string;
  value: number;
  delta: number;
  signal: SentimentLabel;
  summary: string;
}

export interface MacroSnapshot {
  as_of: string;
  score: number;
  regime: string;
  summary: string;
  factors: MacroFactor[];
  is_stale: boolean;
}

export interface FilingSummary {
  ticker: string;
  form_type: string;
  filed_at: string;
  filing_url: string;
  summary: string;
  signal_score: number;
  highlights: string[];
  risks: string[];
  source: string;
  is_stale: boolean;
}

export interface ScoreComponents {
  news: number;
  x: number;
  reddit: number;
  filings: number;
  macro: number;
}

export interface Thesis {
  ticker: string;
  generated_at: string;
  rating: ThesisRating;
  catalysts: string[];
  risks: string[];
  summary: string;
  model: string;
  is_fallback: boolean;
}

export interface ScoreHistoryPoint {
  date: string;
  overall_score: number;
  price_close: number;
  components: ScoreComponents;
}

export interface LeaderboardEntry {
  ticker: string;
  company_name: string;
  price: number;
  daily_change_percent: number;
  overall_score: number;
  thesis_rating: ThesisRating;
}

export interface QuoteResponse {
  quote: Quote;
}

export interface StockResponse {
  quote: Quote;
  score: number;
  components: ScoreComponents;
  thesis: Thesis;
  filing: FilingSummary;
  social_items: ContentItem[];
  headlines: ContentItem[];
  macro: MacroSnapshot;
  updated_at: string;
}

export interface ScoreHistoryResponse {
  ticker: string;
  range: string;
  points: ScoreHistoryPoint[];
}

export interface LeaderboardResponse {
  bullish: LeaderboardEntry[];
  bearish: LeaderboardEntry[];
  updated_at: string;
}

export interface MacroResponse {
  snapshot: MacroSnapshot;
}

export interface SocialResponse {
  ticker: string;
  items: ContentItem[];
}

export interface NewsResponse {
  ticker: string;
  items: ContentItem[];
}

export interface FilingResponse {
  ticker: string;
  filing: FilingSummary;
}

export interface BacktestMetrics {
  total_return: number;
  benchmark_return: number;
  trade_count: number;
  win_rate: number;
  max_drawdown: number;
}

export interface EquityPoint {
  date: string;
  strategy_equity: number;
  benchmark_equity: number;
  score: number;
  price: number;
  signal: "buy" | "sell" | "hold";
}

export interface BacktestTrade {
  entry_date: string;
  exit_date?: string | null;
  entry_price: number;
  exit_price?: number | null;
  return_pct?: number | null;
  outcome?: "win" | "loss" | "open" | null;
}

export interface BacktestResponse {
  ticker: string;
  strategy: string;
  start: string;
  end: string;
  metrics: BacktestMetrics;
  equity_curve: EquityPoint[];
  trades: BacktestTrade[];
}
