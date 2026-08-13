import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import matplotlib.pyplot as plt
from backtester import Backtester
from market_maker import AvellanedaStoikovMaker
from order_flow import OrderFlowGenerator


def main():
    mm = AvellanedaStoikovMaker(gamma=0.1, sigma=2.0, k=1.5, T=1.0, inventory_limit=100)
    flow = OrderFlowGenerator(mid_price=100.0, tick_size=0.01, arrival_rate=10,
                               spread_ticks=5, size_mean=10, seed=42)
    bt = Backtester(mm, flow, n_steps=5000, dt=0.0002)

    results = bt.run()

    fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=False)

    axes[0].plot(results["time"], results["mid_price"], color="steelblue")
    axes[0].set_title("Mid Price Path")
    axes[0].set_ylabel("Price")

    axes[1].plot(range(len(results["pnl"])), results["pnl"], color="darkgreen")
    axes[1].set_title("Mark-to-Market PnL")
    axes[1].set_ylabel("PnL")

    axes[2].plot(range(len(mm.inventory_history)), mm.inventory_history, color="firebrick")
    axes[2].set_title("Inventory Over Time")
    axes[2].set_ylabel("Inventory")
    axes[2].set_xlabel("Step")

    plt.tight_layout()

    output_path = os.path.join(os.path.dirname(__file__), "backtest_results.png")
    plt.savefig(output_path, dpi=150)
    print(f"Saved plot to {output_path}")

    print(f"Final PnL: {results['pnl'][-1]:.2f}")
    print(f"Final Inventory: {mm.inventory_history[-1] if mm.inventory_history else 0}")
    print(f"Number of fills: {len(mm.inventory_history)}")


if __name__ == "__main__":
    main()
