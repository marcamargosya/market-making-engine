"""
Backtester: wires order flow, order book, and market maker together.
Simulates a full trading session and records PnL/inventory/quote history.
"""

import numpy as np
from order_book import OrderBook
from order_flow import OrderFlowGenerator
from market_maker import AvellanedaStoikovMaker


class Backtester:
    def __init__(self, market_maker: AvellanedaStoikovMaker,
                 flow_gen: OrderFlowGenerator, n_steps=1000, dt=0.001,
                 fill_prob=0.5, seed=None):
        """
        market_maker: the quoting agent under test
        flow_gen: synthetic order flow source (also drives mid price)
        n_steps: number of simulation steps
        dt: time increment per step (in same units as market_maker.T)
        fill_prob: probability an aggressive market order arrives each step
        """
        self.mm = market_maker
        self.flow_gen = flow_gen
        self.n_steps = n_steps
        self.dt = dt
        self.fill_prob = fill_prob
        self.book = OrderBook()
        self.rng = np.random.default_rng(seed)

        self.mid_price_history = []
        self.time_history = []

    def _maybe_fill(self, mm_bid, mm_ask):
        """
        Random-aggressor fill model: each step, with probability fill_prob,
        a market order (buy or sell, 50/50) arrives and takes out whichever
        side of the market maker's quote is currently active. Fill size is
        capped so it can never push inventory past the agent's limit.
        """
        if self.rng.random() >= self.fill_prob:
            return None

        aggressor_side = "buy" if self.rng.random() < 0.5 else "sell"
        qty = self.flow_gen._next_size()

        if aggressor_side == "buy" and mm_ask is not None:
            max_qty = self.mm.inventory_limit + self.mm.inventory  # room to sell
            qty = min(qty, max(max_qty, 0))
            if qty > 0:
                return ("ask", mm_ask, qty)
        elif aggressor_side == "sell" and mm_bid is not None:
            max_qty = self.mm.inventory_limit - self.mm.inventory  # room to buy
            qty = min(qty, max(max_qty, 0))
            if qty > 0:
                return ("bid", mm_bid, qty)
        return None

    def run(self):
        t = 0.0
        for step in range(self.n_steps):
            # 1. drift the reference mid price
            self.flow_gen.drift_mid_price(volatility=0.02)
            mid = self.flow_gen.mid_price

            # 2. market maker quotes based on current mid price and time
            mm_bid, mm_ask = self.mm.get_quotes(mid_price=mid, t=t)

            # 3. random aggressor may hit one of the quotes
            fill = self._maybe_fill(mm_bid, mm_ask)
            if fill:
                fill_side, fill_price, fill_qty = fill
                self.mm.on_fill(fill_side, fill_price, fill_qty)

            # 4. record state
            self.mm.mark_to_market_pnl(mid_price=mid)
            self.mid_price_history.append(mid)
            self.time_history.append(t)

            t += self.dt

        return {
            "pnl": self.mm.pnl_history,
            "inventory": self.mm.inventory_history,
            "mid_price": self.mid_price_history,
            "time": self.time_history,
        }