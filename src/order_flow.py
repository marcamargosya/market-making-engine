"""
Synthetic order flow generator.
Simulates arriving limit orders around a reference price using
Poisson arrival times and random price/size distributions.
"""

import random
import numpy as np


class OrderFlowGenerator:
    def __init__(self, mid_price=100.0, tick_size=0.01, arrival_rate=10,
                 spread_ticks=5, size_mean=10, seed=None):
        """
        mid_price: starting reference price
        tick_size: minimum price increment
        arrival_rate: average number of orders per unit time (Poisson lambda)
        spread_ticks: how many ticks around mid orders are placed
        size_mean: mean order size (Poisson-distributed)
        """
        self.mid_price = mid_price
        self.tick_size = tick_size
        self.arrival_rate = arrival_rate
        self.spread_ticks = spread_ticks
        self.size_mean = size_mean
        self.rng = np.random.default_rng(seed)

    def _next_price(self, side: str) -> float:
        offset_ticks = self.rng.integers(1, self.spread_ticks + 1)
        offset = offset_ticks * self.tick_size
        if side == "bid":
            return round(self.mid_price - offset, 2)
        else:
            return round(self.mid_price + offset, 2)

    def _next_size(self) -> int:
        return max(1, int(self.rng.poisson(self.size_mean)))

    def generate_batch(self, n_orders: int):
        """Generate a batch of n synthetic orders (side, price, quantity)."""
        orders = []
        for _ in range(n_orders):
            side = "bid" if self.rng.random() < 0.5 else "ask"
            price = self._next_price(side)
            qty = self._next_size()
            orders.append((side, price, qty))
        return orders

    def generate_arrival_times(self, n_orders: int):
        """Generate n inter-arrival times (seconds) from a Poisson process."""
        return self.rng.exponential(1.0 / self.arrival_rate, size=n_orders)

    def drift_mid_price(self, volatility=0.05):
        """Randomly walk the reference mid price (for multi-batch simulations)."""
        shock = self.rng.normal(0, volatility)
        self.mid_price = round(max(0.01, self.mid_price + shock), 2)