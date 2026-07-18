"""
Parameter sensitivity sweep (multi-seed): compares market maker performance
across different risk-aversion (gamma) values, averaged over multiple random
seeds, to give a statistically credible view of the gamma-PnL relationship.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
import matplotlib.pyplot as plt
from backtester import Backtester
from market_maker import AvellanedaStoikovMaker
from order_flow import OrderFlowGenerator


def run_single(gamma, seed):
    mm = AvellanedaStoikovMaker(gamma=gamma, sigma=2.0, k=1.5, T=1.0, inventory_limit=100)
    flow = OrderFlowGenerator(mid_price=100.0, tick_size=0.01, arrival_rate=10,
                               spread_ticks=5, size_mean=10, seed=seed)
    bt = Backtester(mm, flow, n_steps=5000, dt=0.0002, fill_prob=0.5,
                     spread_decay=2.0, seed=seed)
    results = bt.run()
    final_pnl = results["pnl"][-1] if results["pnl"] else 0.0
    final_inv = mm.inventory_history[-1] if mm.inventory_history else 0
    n_fills = len(mm.inventory_history)
    return final_pnl, final_inv, n_fills


def main():
    gammas = [0.01, 0.1, 0.5, 1.0]
    seeds = list(range(20))  # 20 seeds per gamma for a stable average

    print(f"{'gamma':>8} {'mean_pnl':>12} {'std_pnl':>10} {'mean_|inv|':>12} {'mean_fills':>12}")

    mean_pnls, std_pnls = [], []
    for gamma in gammas:
        pnls, invs, fills = [], [], []
        for seed in seeds:
            pnl, inv, n_fills = run_single(gamma, seed)
            pnls.append(pnl)
            invs.append(abs(inv))
            fills.append(n_fills)

        mean_pnl = np.mean(pnls)
        std_pnl = np.std(pnls)
        mean_pnls.append(mean_pnl)
        std_pnls.append(std_pnl)

        print(f"{gamma:>8} {mean_pnl:>12.2f} {std_pnl:>10.2f} {np.mean(invs):>12.2f} {np.mean(fills):>12.1f}")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.errorbar(gammas, mean_pnls, yerr=std_pnls, marker='o', capsize=4)
    ax.set_xscale('log')
    ax.set_xlabel("gamma (risk aversion, log scale)")
    ax.set_ylabel("Mean final PnL (± 1 std across 20 seeds)")
    ax.set_title("PnL vs Risk Aversion, averaged across seeds")
    ax.axhline(0, color='gray', linewidth=0.8, linestyle='--')
    plt.tight_layout()

    output_path = os.path.join(os.path.dirname(__file__), "gamma_sensitivity_multiseed.png")
    plt.savefig(output_path, dpi=150)
    print(f"\nSaved plot to {output_path}")


if __name__ == "__main__":
    main()