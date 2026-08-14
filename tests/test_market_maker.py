import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from market_maker import AvellanedaStoikovMaker


def test_reservation_price_at_zero_inventory():
    mm = AvellanedaStoikovMaker(gamma=0.1, sigma=2.0, k=1.5, T=1.0)
    r = mm.reservation_price(mid_price=100.0, t=0.0)
    # with zero inventory, reservation price should equal mid price
    assert abs(r - 100.0) < 1e-9


def test_reservation_price_shifts_with_long_inventory():
    mm = AvellanedaStoikovMaker(gamma=0.1, sigma=2.0, k=1.5, T=1.0)
    mm.inventory = 10  # long position
    r = mm.reservation_price(mid_price=100.0, t=0.0)
    # long inventory should push reservation price BELOW mid (agent wants to sell)
    assert r < 100.0


def test_reservation_price_shifts_with_short_inventory():
    mm = AvellanedaStoikovMaker(gamma=0.1, sigma=2.0, k=1.5, T=1.0)
    mm.inventory = -10  # short position
    r = mm.reservation_price(mid_price=100.0, t=0.0)
    # short inventory should push reservation price ABOVE mid (agent wants to buy)
    assert r > 100.0


def test_spread_widens_near_horizon_end():
    mm = AvellanedaStoikovMaker(gamma=0.1, sigma=2.0, k=1.5, T=1.0)
    spread_early = mm.optimal_spread(t=0.0)
    spread_late = mm.optimal_spread(t=0.99)
    # spread should shrink as time_left shrinks (less inventory risk to hedge against)
    assert spread_late < spread_early


def test_get_quotes_returns_valid_bid_ask():
    mm = AvellanedaStoikovMaker(gamma=0.1, sigma=2.0, k=1.5, T=1.0)
    bid, ask = mm.get_quotes(mid_price=100.0, t=0.0)
    assert bid < 100.0 < ask


def test_inventory_limit_stops_quoting():
    mm = AvellanedaStoikovMaker(gamma=0.1, sigma=2.0, k=1.5, T=1.0, inventory_limit=5)
    mm.inventory = 5
    bid, ask = mm.get_quotes(mid_price=100.0, t=0.0)
    assert bid is None
    assert ask is not None

    mm.inventory = -5
    bid, ask = mm.get_quotes(mid_price=100.0, t=0.0)
    assert ask is None
    assert bid is not None


def test_on_fill_updates_inventory_and_cash():
    mm = AvellanedaStoikovMaker()
    mm.on_fill("bid", price=100.0, quantity=5)
    assert mm.inventory == 5
    assert mm.cash == -500.0

    mm.on_fill("ask", price=101.0, quantity=3)
    assert mm.inventory == 2
    assert mm.cash == -500.0 + 303.0


def test_mark_to_market_pnl():
    mm = AvellanedaStoikovMaker()
    mm.on_fill("bid", price=100.0, quantity=10)
    pnl = mm.mark_to_market_pnl(mid_price=105.0)
    # bought 10 @ 100 (cash -1000), now worth 10*105=1050 -> pnl = 50
    assert abs(pnl - 50.0) < 1e-9

