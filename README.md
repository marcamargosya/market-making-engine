# Market Making Engine

A market-making and execution simulation engine built around the Avellaneda-Stoikov
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
  the agent quotes, a random aggressor order may fill one side of the quote with
  probability that decays as the quoted spread widens (capped so inventory never
  exceeds the agent's limit), and PnL/inventory are recorded.

## Running it

\`\`\`bash
source venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v                              # 24 tests, all passing
python notebooks/run_backtest.py               # single backtest run + PnL/inventory plot
python notebooks/gamma_sweep_multiseed.py      # gamma sensitivity, averaged over 20 seeds
\`\`\`

## Key result: risk aversion (gamma) sensitivity

![Backtest results](notebooks/backtest_results.png)
![Gamma sensitivity](notebooks/gamma_sensitivity_multiseed.png)

Backtest across `gamma = 0.01, 0.1, 0.5, 1.0`, averaged over 20 seeds each:

- **Fill rate falls as gamma rises** (664 → 581 → 346 → 226 avg fills) — higher
  risk aversion widens quotes, so they get hit less.
- **Mean PnL does not recover past gamma=0.01** (+3,749 → -956 → -7,316 → -5,255).
  Reservation price and spread formulas both check out against theory
  independently, so this isn't a bug — the simulated mid-price is a pure
  random walk with no mean reversion, and that noise dominates PnL more than
  inventory risk does. Adding mean reversion or trend to the price process
  would likely let the inventory-aversion benefit show through.

## Testing

All four components have independent unit tests (`tests/`), covering matching
logic, distributional properties of synthetic flow, reservation price and spread
formulas, inventory limit enforcement, and reproducibility under fixed seeds.
