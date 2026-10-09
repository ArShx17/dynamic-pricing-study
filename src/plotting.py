"""Figures for the paper (saved as PNG). Uses results/tables/results.csv and recomputed load curves."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.data_loader import load_day
from src.demand_response import apply_dr_classes
from src.pricing import net_load
from src.scenarios import _prices

LABEL = {"S1_TOU": "TOU", "S2_RTP": "RTP (market)", "S3_CPP": "CPP", "S2b_RTP_net": "RTP-net", "S3b_CPP_net": "CPP-net"}
COLOR = {"S1_TOU": "tab:orange", "S2_RTP": "tab:green", "S3_CPP": "tab:red", "S2b_RTP_net": "tab:blue", "S3b_CPP_net": "tab:purple"}

def _curves(cfg, day, part=0.3):
    ld, pr = load_day(day); L, flat = ld.load_MW.values, pr.flat.values
    re = L - net_load(L, ld.solar_pu, ld.wind_pu, cfg["renewable_penetration"], cfg["peak_mw"], cfg.get("solar_share", 0.6))
    prices = _prices(L, L - re, flat, pr)
    new = {k: apply_dr_classes(L, p, flat, cfg["customer_mix"], cfg["elasticity"], cfg["cross_elasticity_ratio"], part)
           for k, p in prices.items()}
    return L, re, new

def fig_load_curves(cfg, path):
    fig, ax = plt.subplots(1, 2, figsize=(12, 4), sharey=False)
    for a, day in zip(ax, cfg["days"]):
        L, re, new = _curves(cfg, day)
        a.plot(L, "k", lw=2.5, label="Baseline (flat)")
        for k, n in new.items(): a.plot(n, color=COLOR[k], lw=1.3, label=LABEL[k])
        a.set(title=f"{day.capitalize()} day, 30% participation", xlabel="Hour", ylabel="Load (MW)"); a.grid(alpha=.3)
    ax[0].legend(fontsize=8); fig.tight_layout(); fig.savefig(path, dpi=200); plt.close(fig)

def fig_net_load(cfg, path):
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    for a, day in zip(ax, cfg["days"]):
        L, re, new = _curves(cfg, day)
        a.plot(L - re, "k", lw=2.5, label="Baseline net load")
        for k in ["S1_TOU", "S3_CPP", "S2b_RTP_net"]: a.plot(new[k] - re, color=COLOR[k], lw=1.5, label=LABEL[k])
        a.set(title=f"{day.capitalize()}: net load (demand - solar - wind)", xlabel="Hour", ylabel="Net load (MW)"); a.grid(alpha=.3)
    ax[0].legend(fontsize=8); fig.tight_layout(); fig.savefig(path, dpi=200); plt.close(fig)

def fig_peak_bars(df, cfg, path):
    d = df[(df.participation == 0.3) & (df.re_penetration == cfg["renewable_penetration"])]
    fig, ax = plt.subplots(figsize=(8, 4)); w = 0.38; x = np.arange(len(LABEL))
    for i, day in enumerate(cfg["days"]):
        v = [d[(d.day == day) & (d.scheme == s)].net_peak_reduction_pct.iloc[0] for s in LABEL]
        ax.bar(x + (i - .5) * w, v, w, label=day.capitalize())
    ax.axhline(0, color="k", lw=.8); ax.set_xticks(x); ax.set_xticklabels(LABEL.values())
    ax.set(ylabel="Net peak reduction (%)", title="Net peak reduction at 30% participation (positive = lower peak)")
    ax.legend(); ax.grid(axis="y", alpha=.3); fig.tight_layout(); fig.savefig(path, dpi=200); plt.close(fig)

def fig_participation(df, cfg, path):
    d = df[df.re_penetration == cfg["renewable_penetration"]]
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    for a, day in zip(ax, cfg["days"]):
        for s in LABEL:
            t = d[(d.day == day) & (d.scheme == s)].sort_values("participation")
            a.plot(t.participation * 100, t.net_peak_reduction_pct, "o-", color=COLOR[s], label=LABEL[s])
        a.axhline(0, color="k", lw=.8); a.set(title=day.capitalize(), xlabel="Participation (%)", ylabel="Net peak reduction (%)"); a.grid(alpha=.3)
    ax[0].legend(fontsize=8); fig.tight_layout(); fig.savefig(path, dpi=200); plt.close(fig)