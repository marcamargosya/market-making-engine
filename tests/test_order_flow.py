import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from order_flow import OrderFlowGenerator
from order_book import OrderBook


def test_generate_batch_shape():
    gen = OrderFlowGenerator(seed=42)
    orders = gen.generate_batch(20)
    assert len(orders) == 20
    for side, price, qty in orders:
        assert side in ("bid", "ask")
        assert price > 0
        assert qty >= 1


def test_bid_below_mid_ask_above_mid():
    gen = OrderFlowGenerator(mid_price=100.0, tick_size=0.01, spread_ticks=5, seed=1)
    orders = gen.generate_batch(50)
    for side, price, qty in orders:
        if side == "bid":
            assert price < 100.0
        else:
            assert price > 100.0


def test_arrival_times_positive():
    gen = OrderFlowGenerator(arrival_rate=10, seed=7)
    times = gen.generate_arrival_times(30)
    assert len(times) == 30
    assert all(t >= 0 for t in times)


def test_drift_mid_price_changes():
    gen = OrderFlowGenerator(mid_price=100.0, seed=3)
    original = gen.mid_price
    gen.drift_mid_price(volatility=0.1)
    assert gen.mid_price != original
    assert gen.mid_price > 0


def test_feeds_into_order_book():
    gen = OrderFlowGenerator(mid_price=100.0, seed=99)
    book = OrderBook()
    orders = gen.generate_batch(100)
    for side, price, qty in orders:
        book.add_order(side, price, qty)
    # book should have processed all orders without error
    snap = book.snapshot()
    assert isinstance(snap["bids"], list)
    assert isinstance(snap["asks"], list)


