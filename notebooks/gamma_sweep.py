"""
Parameter sensitivity sweep: compares market maker performance across
different risk-aversion (gamma) values to show the inventory-risk tradeoff.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import matplotlib.pyplot as plt
from backtester import Backtester
from market_maker import AvellanedaStoikovMaker
from order_flow import OrderFlowGenerator


def run_single(gamma, seed=42):
    mm = AvellanedaStoikovMaker(gamma=gamma, sigma=2.0, k=1.5, T=1.0, inventory_limit=100)
    flow = OrderFlowGenerator(mid_price=100.0, tick_size=0.01, arrival_rate=10,
                               spread_ticks=5, size_mean=10, seed=seed)
    bt = Backtester(mm, flow, n_steps=5000, dt=0.0002, fill_prob=0.5, seed=seed)
    results = bt.run()
    return mm, results


def main():
    gammas = [0.01, 0.1, 0.5, 1.0]
    fig, axes = plt.subplots(2, 1, figsize=(10, 8))

    print(f"{'gamma':>8} {'final_pnl':>12} {'final_inventory':>16} {'n_fills':>10}")
    for gamma in gammas:
        mm, results = run_single(gamma)
        final_pnl = results["pnl"][-1] if results["pnl"] else 0.0
        final_inv = mm.inventory_history[-1] if mm.inventory_history else 0
        n_fills = len(mm.inventory_history)

        print(f"{gamma:>8} {final_pnl:>12.2f} {final_inv:>16} {n_fills:>10}")

        axes[0].plot(range(len(results["pnl"])), results["pnl"], label=f"gamma={gamma}")
        axes[1].plot(range(len(mm.inventory_history)), mm.inventory_history, label=f"gamma={gamma}")

    axes[0].set_title("PnL Across Risk Aversion (gamma) Values")
    axes[0].set_ylabel("PnL")
    axes[0].legend()

    axes[1].set_title("Inventory Across Risk Aversion (gamma) Values")
    axes[1].set_ylabel("Inventory")
    axes[1].set_xlabel("Fill #")
    axes[1].legend()

    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(__file__), "gamma_sensitivity.png")
    plt.savefig(output_path, dpi=150)
    print(f"\nSaved plot to {output_path}")


if __name__ == "__main__":
    main()