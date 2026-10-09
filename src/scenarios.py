"""Run all pricing scenarios through demand response and DC-OPF; write results/tables/results.csv."""
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from src.data_loader import load_day
from src.demand_response import apply_dr_classes
from src.pricing import net_load, revenue_neutral, rtp_from_net_load, cpp_from_net_load
from src.network import build_network
from src.dispatch import run_day
from src.metrics import load_factor, par

logging.getLogger("pandapower").setLevel(logging.ERROR)
ROOT = Path(__file__).resolve().parents[1]

def _prices(L, NL, flat, pr):
    return {"S1_TOU": pr.TOU.values,
            "S2_RTP": revenue_neutral(pr.RTP.values, L, flat),
            "S3_CPP": revenue_neutral(pr.CPP.values, L, flat),
            "S2b_RTP_net": rtp_from_net_load(NL, L, flat),
            "S3b_CPP_net": cpp_from_net_load(NL, L, flat, flat.mean())}

def _run(cfg, day, scheme, part, pen, cache):
    ld, pr = load_day(day)
    L, flat = ld.load_MW.values, pr.flat.values
    sol, wnd = ld.solar_pu.values, ld.wind_pu.values
    re = L - net_load(L, sol, wnd, pen, cfg["peak_mw"], cfg.get("solar_share", 0.6))
    NL = L - re
    p = flat if scheme == "S0_flat" else _prices(L, NL, flat, pr)[scheme]
    N = L if scheme == "S0_flat" else apply_dr_classes(L, p, flat, cfg["customer_mix"], cfg["elasticity"],
                                                       cfg["cross_elasticity_ratio"], part)
    if pen not in cache:
        cache[pen] = build_network({**cfg, "renewable_penetration": pen})
    d = run_day(cache[pen], N, sol, wnd)
    return {"day": day, "scheme": scheme, "participation": part, "re_penetration": pen,
            "peak_MW": N.max(), "load_factor": load_factor(N), "PAR": par(N),
            "net_peak_MW": (N - re).max(), "daily_cost": d.cost.sum(),
            "bill": (N * p).sum(), "curtailed_MWh": d.curtailed_MW.sum(), "re_used_MWh": d.re_used_MW.sum(),
            "_base_peak": L.max(), "_base_net_peak": NL.max(), "_base_bill": (L * flat).sum()}

def run_all(cfg, out_file=None):
    cache, rows = {}, []
    base_pen = cfg["renewable_penetration"]; high_pen = cfg.get("high_re_penetration", 0.5)
    for day in cfg["days"]:
        rows.append(_run(cfg, day, "S0_flat", 0.0, base_pen, cache))
        for scheme in ["S1_TOU", "S2_RTP", "S3_CPP", "S2b_RTP_net", "S3b_CPP_net"]:
            for part in cfg["participation"]:
                rows.append(_run(cfg, day, scheme, part, base_pen, cache))
        rows.append(_run(cfg, day, "S0_flat", 0.0, high_pen, cache))             # S4: high renewables
        for scheme in ["S2_RTP", "S2b_RTP_net"]:
            rows.append(_run(cfg, day, scheme, 0.3, high_pen, cache))
        print("finished", day)
    df = pd.DataFrame(rows)
    base = df[(df.scheme == "S0_flat")].set_index(["day", "re_penetration"])
    key = list(zip(df.day, df.re_penetration))
    df["peak_reduction_pct"] = 100 * (df._base_peak - df.peak_MW) / df._base_peak
    df["net_peak_reduction_pct"] = 100 * (df._base_net_peak - df.net_peak_MW) / df._base_net_peak
    df["cost_change_pct"] = [100 * (c - base.loc[k, "daily_cost"]) / base.loc[k, "daily_cost"] for c, k in zip(df.daily_cost, key)]
    df["bill_change_pct"] = 100 * (df.bill - df._base_bill) / df._base_bill
    df = df.drop(columns=["_base_peak", "_base_net_peak", "_base_bill"]).round(3)
    target = Path(out_file) if out_file else ROOT / "results" / "tables" / "results.csv"
    target.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(target, index=False)
    show = ["day", "scheme", "participation", "re_penetration", "peak_reduction_pct", "net_peak_reduction_pct", "cost_change_pct", "bill_change_pct", "curtailed_MWh"]
    print(df[show].to_string(index=False))
    return df