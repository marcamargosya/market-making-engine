"""
Backtester: wires order flow, order book, and market maker together.
Simulates a full trading session and records PnL/inventory/quote history.
"""

from order_book import OrderBook
from order_flow import OrderFlowGenerator
from market_maker import AvellanedaStoikovMaker


class Backtester:
    def __init__(self, market_maker: AvellanedaStoikovMaker,
                 flow_gen: OrderFlowGenerator, n_steps=1000, dt=0.001):
        """
        market_maker: the quoting agent under test
        flow_gen: synthetic order flow source (also drives mid price)
        n_steps: number of simulation steps
        dt: time increment per step (in same units as market_maker.T)
        """
        self.mm = market_maker
        self.flow_gen = flow_gen
        self.n_steps = n_steps
        self.dt = dt
        self.book = OrderBook()

        self.mid_price_history = []
        self.time_history = []

    def _check_fills(self, mm_bid, mm_ask, incoming_side, incoming_price, incoming_qty):
        """
        Simplified fill logic: the market maker's resting quote gets filled
        if an incoming market-taking order crosses it.
        """
        filled = None
        if incoming_side == "ask" and mm_bid is not None and incoming_price <= mm_bid:
            filled = ("bid", mm_bid, min(incoming_qty, 10))
        elif incoming_side == "bid" and mm_ask is not None and incoming_price >= mm_ask:
            filled = ("ask", mm_ask, min(incoming_qty, 10))
        return filled

    def run(self):
        t = 0.0
        for step in range(self.n_steps):
            # 1. drift the reference mid price
            self.flow_gen.drift_mid_price(volatility=0.02)
            mid = self.flow_gen.mid_price

            # 2. market maker quotes based on current mid price and time
            mm_bid, mm_ask = self.mm.get_quotes(mid_price=mid, t=t)

            # 3. generate one incoming synthetic order (market flow)
            side, price, qty = self.flow_gen.generate_batch(1)[0]

            # 4. check if it fills the market maker's quote
            fill = self._check_fills(mm_bid, mm_ask, side, price, qty)
            if fill:
                fill_side, fill_price, fill_qty = fill
                self.mm.on_fill(fill_side, fill_price, fill_qty)

            # 5. record state
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