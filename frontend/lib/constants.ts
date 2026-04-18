export const demoTickers = ["NVDA", "PLTR", "MSFT", "AMD", "AAPL", "TSLA"];
export const scoreRanges = ["1M", "3M", "6M", "1Y"] as const;
export const strategies = [
  {
    key: "threshold_cross",
    label: "Threshold Cross",
    description: "Buy when score clears a threshold and exit when it breaks down."
  },
  {
    key: "score_momentum",
    label: "Score Momentum",
    description: "Buy when the score accelerates across recent sessions."
  }
] as const;
