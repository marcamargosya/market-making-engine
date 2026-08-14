import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from order_book import OrderBook


def test_add_order_no_match():
    book = OrderBook()
    book.add_order("bid", 99.5, 10)
    assert book.best_bid() == 99.5
    assert book.best_ask() is None
    assert len(book.trades) == 0


def test_simple_match():
    book = OrderBook()
    book.add_order("bid", 100.0, 10)
    book.add_order("ask", 100.0, 10)
    assert len(book.trades) == 1
    assert book.trades[0]["quantity"] == 10
    assert book.best_bid() is None
    assert book.best_ask() is None


def test_partial_fill():
    book = OrderBook()
    book.add_order("bid", 100.0, 10)
    book.add_order("ask", 100.0, 4)
    assert len(book.trades) == 1
    assert book.trades[0]["quantity"] == 4
    assert book.best_bid() == 100.0
    # remaining bid quantity should be 6
    remaining = sum(o.quantity for o in book.bids[100.0])
    assert remaining == 6


def test_price_time_priority():
    book = OrderBook()
    o1 = book.add_order("bid", 100.0, 5)
    o2 = book.add_order("bid", 100.0, 5)
    book.add_order("ask", 100.0, 5)
    # o1 (earlier) should be filled first, fully
    assert len(book.trades) == 1
    assert book.trades[0]["bid_id"] == o1.order_id


def test_cancel_order():
    book = OrderBook()
    o = book.add_order("bid", 99.0, 10)
    assert book.cancel_order(o.order_id) is True
    assert book.best_bid() is None
    assert book.cancel_order(9999) is False


def test_mid_price():
    book = OrderBook()
    book.add_order("bid", 99.0, 10)
    book.add_order("ask", 101.0, 10)
    assert book.mid_price() == 100.0


