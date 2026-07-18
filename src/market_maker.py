"""
Avellaneda-Stoikov market-making agent.
Computes optimal bid/ask quotes based on inventory risk and time horizon.
"""

import numpy as np


class AvellanedaStoikovMaker:
    def __init__(self, gamma=0.1, sigma=2.0, k=1.5, T=1.0, inventory_limit=100):
        """
        gamma: risk aversion coefficient
        sigma: volatility of the mid price
        k: order book liquidity parameter (higher = tighter spreads needed to get filled)
        T: total trading horizon (in same units as t)
        inventory_limit: max absolute inventory before agent stops quoting on that side
        """
        self.gamma = gamma
        self.sigma = sigma
        self.k = k
        self.T = T
        self.inventory_limit = inventory_limit

        self.inventory = 0
        self.cash = 0.0
        self.pnl_history = []
        self.inventory_history = []
        self.quote_history = []

    def reservation_price(self, mid_price: float, t: float) -> float:
        """Indifference price adjusted for inventory risk."""
        time_left = max(self.T - t, 1e-6)
        return mid_price - self.inventory * self.gamma * (self.sigma ** 2) * time_left

    def optimal_spread(self, t: float) -> float:
        """Total bid-ask spread width around the reservation price."""
        time_left = max(self.T - t, 1e-6)
        return self.gamma * (self.sigma ** 2) * time_left + (2 / self.gamma) * np.log(1 + self.gamma / self.k)

    def get_quotes(self, mid_price: float, t: float):
        """Returns (bid_price, ask_price) for the current state."""
        r = self.reservation_price(mid_price, t)
        spread = self.optimal_spread(t)

        bid = r - spread / 2
        ask = r + spread / 2

        # Skip quoting on a side if inventory limit reached
        if self.inventory >= self.inventory_limit:
            bid = None
        if self.inventory <= -self.inventory_limit:
            ask = None

        self.quote_history.append({"t": t, "bid": bid, "ask": ask, "mid": mid_price})
        return bid, ask

    def on_fill(self, side: str, price: float, quantity: int):
        """Update inventory and cash when a quote gets filled."""
        if side == "bid":
            self.inventory += quantity
            self.cash -= price * quantity
        elif side == "ask":
            self.inventory -= quantity
            self.cash += price * quantity

        self.inventory_history.append(self.inventory)

    def mark_to_market_pnl(self, mid_price: float) -> float:
        """Current PnL = cash + inventory valued at mid price."""
        pnl = self.cash + self.inventory * mid_price
        self.pnl_history.append(pnl)
        return pnl