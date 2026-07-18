"""
Limit Order Book (LOB) simulator.
Supports adding, canceling, and matching limit orders with price-time priority.
"""

from collections import deque
from dataclasses import dataclass, field
import itertools

_order_id_counter = itertools.count(1)


@dataclass
class Order:
    side: str          # "bid" or "ask"
    price: float
    quantity: int
    order_id: int = field(default_factory=lambda: next(_order_id_counter))

    def __repr__(self):
        return f"Order(id={self.order_id}, {self.side}, px={self.price}, qty={self.quantity})"


class OrderBook:
    def __init__(self):
        # price -> deque of Orders (time priority within each price level)
        self.bids: dict[float, deque[Order]] = {}
        self.asks: dict[float, deque[Order]] = {}
        self.trades: list[dict] = []

    def best_bid(self):
        return max(self.bids) if self.bids else None

    def best_ask(self):
        return min(self.asks) if self.asks else None

    def mid_price(self):
        bb, ba = self.best_bid(), self.best_ask()
        if bb is None or ba is None:
            return None
        return (bb + ba) / 2

    def add_order(self, side: str, price: float, quantity: int) -> Order:
        order = Order(side=side, price=price, quantity=quantity)
        book = self.bids if side == "bid" else self.asks
        book.setdefault(price, deque()).append(order)
        self._match()
        return order

    def cancel_order(self, order_id: int) -> bool:
        for book in (self.bids, self.asks):
            for price, level in list(book.items()):
                for o in list(level):
                    if o.order_id == order_id:
                        level.remove(o)
                        if not level:
                            del book[price]
                        return True
        return False

    def _match(self):
        while True:
            bb, ba = self.best_bid(), self.best_ask()
            if bb is None or ba is None or bb < ba:
                break

            bid_level = self.bids[bb]
            ask_level = self.asks[ba]
            bid_order = bid_level[0]
            ask_order = ask_level[0]

            fill_qty = min(bid_order.quantity, ask_order.quantity)
            trade_price = ask_order.price  # convention: resting order sets price

            self.trades.append({
                "price": trade_price,
                "quantity": fill_qty,
                "bid_id": bid_order.order_id,
                "ask_id": ask_order.order_id,
            })

            bid_order.quantity -= fill_qty
            ask_order.quantity -= fill_qty

            if bid_order.quantity == 0:
                bid_level.popleft()
                if not bid_level:
                    del self.bids[bb]
            if ask_order.quantity == 0:
                ask_level.popleft()
                if not ask_level:
                    del self.asks[ba]

    def snapshot(self, depth: int = 5):
        bid_levels = sorted(self.bids.items(), key=lambda x: -x[0])[:depth]
        ask_levels = sorted(self.asks.items(), key=lambda x: x[0])[:depth]
        return {
            "bids": [(p, sum(o.quantity for o in q)) for p, q in bid_levels],
            "asks": [(p, sum(o.quantity for o in q)) for p, q in ask_levels],
        }