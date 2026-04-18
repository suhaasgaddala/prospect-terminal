import {
  BacktestResponse,
  LeaderboardResponse,
  MacroResponse,
  NewsResponse,
  ScoreHistoryResponse,
  SocialResponse,
  StockResponse
} from "@/types/generated-api";
import { apiFetch } from "@/lib/api-client";

export const api = {
  getLeaderboard: () => apiFetch<LeaderboardResponse>("/leaderboard"),
  getMacro: () => apiFetch<MacroResponse>("/macro"),
  getStock: (ticker: string) => apiFetch<StockResponse>(`/stock?ticker=${ticker}`),
  getScoreHistory: (ticker: string, range = "3M") =>
    apiFetch<ScoreHistoryResponse>(`/score-history?ticker=${ticker}&range=${range}`),
  getBacktest: (params: {
    ticker: string;
    start: string;
    end: string;
    strategy: string;
    threshold?: number;
    exit_threshold?: number;
    momentum_window?: number;
    momentum_delta?: number;
  }) => {
    const query = new URLSearchParams(
      Object.entries(params).map(([key, value]) => [key, String(value)])
    );
    return apiFetch<BacktestResponse>(`/backtest?${query.toString()}`);
  },
  getSocial: (ticker: string) => apiFetch<SocialResponse>(`/social?ticker=${ticker}`),
  getNews: (ticker: string) => apiFetch<NewsResponse>(`/news?ticker=${ticker}`)
};
