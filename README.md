# Market Making Engine

A market-making and execution simulation engine, built around the Avellaneda-Stoikov
optimal quoting model. Simulates a full trading loop: synthetic order flow, a
price-time-priority limit order book, an inventory-aware quoting agent, and a
backtester that ties them together and measures PnL/inventory risk.

## Components

- **`src/order_book.py`** — Limit order book with price-time priority matching,
  partial fills, and order cancellation.
- **`src/order_flow.py`** — Synthetic order flow generator (Poisson arrivals,
  random price/size distributions around a drifting mid price).
- **`src/market_maker.py`** — Avellaneda-Stoikov market-making agent. Computes a
  reservation price and optimal spread from inventory, volatility, and time
  horizon; tracks PnL and inventory.
- **`src/backtester.py`** — Wires the above together. Each step: mid price drifts,
  the agent quotes, a random aggressor order may fill one side of the quote
  (capped so inventory never exceeds the agent's limit), and PnL/inventory are
  recorded.

## Running it

```bash
source venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v                          # 24 tests, all passing
python notebooks/run_backtest.py          # single backtest run + PnL/inventory plot
python notebooks/gamma_sweep.py           # parameter sensitivity across gamma
```

## Key result: gamma sensitivity

Running the backtest across risk-aversion values (`gamma = 0.01, 0.1, 0.5, 1.0`)
shows PnL getting *worse* as gamma increases — the opposite of what
Avellaneda-Stoikov theory predicts, where higher risk aversion should protect
PnL by tightening inventory control.

The cause: the backtester's fill model treats each step as a fixed-probability
random aggressor, independent of spread width. In reality, a wider quote (higher
gamma) should get hit *less often*, since a rational market taker won't cross an
unfavorable spread. Here, fill probability doesn't fall as spread widens, so
higher gamma only pushes quotes further from mid whenever they do fill — worsening
execution price without the offsetting benefit of fewer bad fills.

This is a known simplification of the fill model, not a bug in the AS
implementation itself — the reservation price and spread formulas were tested
independently and match the theoretical behavior (spread widens with gamma,
reservation price shifts correctly with inventory). A natural next step would be
to make fill probability decrease with distance from mid, which should recover
the theoretical PnL/gamma relationship.

## Testing

All four