import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from backtester import Backtester
from market_maker import AvellanedaStoikovMaker
from order_flow import OrderFlowGenerator


def test_backtester_runs_without_error():
    mm = AvellanedaStoikovMaker(gamma=0.1, sigma=2.0, k=1.5, T=1.0)
    flow = OrderFlowGenerator(mid_price=100.0, seed=42)
    bt = Backtester(mm, flow, n_steps=200, dt=0.005)
    results = bt.run()
    assert len(results["mid_price"]) == 200
    assert len(results["time"]) == 200


def test_backtester_produces_pnl_history():
    mm = AvellanedaStoikovMaker()
    flow = OrderFlowGenerator(mid_price=100.0, seed=1)
    bt = Backtester(mm, flow, n_steps=500, dt=0.002)
    results = bt.run()
    assert len(results["pnl"]) > 0
    assert all(isinstance(x, float) for x in results["pnl"])


def test_backtester_inventory_stays_within_limit():
    mm = AvellanedaStoikovMaker(inventory_limit=50)
    flow = OrderFlowGenerator(mid_price=100.0, seed=7)
    bt = Backtester(mm, flow, n_steps=1000, dt=0.001)
    bt.run()
    assert all(abs(inv) <= 50 for inv in mm.inventory_history)


def test_backtester_mid_price_stays_positive():
    mm = AvellanedaStoikovMaker()
    flow = OrderFlowGenerator(mid_price=100.0, seed=99)
    bt = Backtester(mm, flow, n_steps=1000, dt=0.001)
    results = bt.run()
    assert all(p > 0 for p in results["mid_price"])


def test_backtester_reproducible_with_same_seed():
    mm1 = AvellanedaStoikovMaker()
    flow1 = OrderFlowGenerator(mid_price=100.0, seed=123)
    bt1 = Backtester(mm1, flow1, n_steps=300, dt=0.002, seed=5)
    results1 = bt1.run()

    mm2 = AvellanedaStoikovMaker()
    flow2 = OrderFlowGenerator(mid_price=100.0, seed=123)
    bt2 = Backtester(mm2, flow2, n_steps=300, dt=0.002, seed=5)
    results2 = bt2.run()

    assert results1["mid_price"] == results2["mid_price"]


if __name__ == "__main__":
    test_backtester_runs_without_error()
    test_backtester_produces_pnl_history()
    test_backtester_inventory_stays_within_limit()
    test_backtester_mid_price_stays_positive()
    test_backtester_reproducible_with_same_seed()
    print("All tests passed.")