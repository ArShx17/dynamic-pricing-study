"""Run all pricing scenarios through demand response, DC-OPF and AC checks; write results/tables/results.csv."""
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from src.data_loader import load_day
from src.demand_response import apply_dr_classes
from src.pricing import net_load, revenue_neutral, rtp_from_net_load, cpp_from_net_load
from src.network import build_network, set_line_ratings
from src.dispatch import run_day
from src.metrics import load_factor, par

logging.getLogger("pandapower").setLevel(logging.ERROR)
ROOT = Path(__file__).resolve().parents[1]
HEADROOM = 1.25      # line rating = 125% of the highest baseline current (assumption)

def _prices(L, NL, flat, pr):
    return {"S1_TOU": pr.TOU.values,
            "S2_RTP": revenue_neutral(pr.RTP.values, L, flat),
            "S3_CPP": revenue_neutral(pr.CPP.values, L, flat),
            "S2b_RTP_net": rtp_from_net_load(NL, L, flat),
            "S3b_CPP_net": cpp_from_net_load(NL, L, flat, flat.mean())}

def _calibrate_ratings(cfg):
    """Line ratings = HEADROOM x the highest current seen in the flat-tariff baseline (both days)."""
    net = build_network(cfg); imax = np.zeros(len(net.line))
    for day in cfg["days"]:
        ld, pr = load_day(day)
        d = run_day(net, ld.load_MW.values, ld.solar_pu.values, ld.wind_pu.values)
        imax = np.maximum(imax, d.attrs["line_i_ka_max"])
    return HEADROOM * imax

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
        net = build_network({**cfg, "renewable_penetration": pen})
        set_line_ratings(net, cache["ratings"])
        cache[pen] = net
    d = run_day(cache[pen], N, sol, wnd)
    return {"day": day, "scheme": scheme, "participation": part, "re_penetration": pen,
            "peak_MW": N.max(), "load_factor": load_factor(N), "PAR": par(N),
            "net_peak_MW": (N - re).max(), "daily_cost": d.cost.sum(),
            "bill": (N * p).sum(), "curtailed_MWh": d.curtailed_MW.sum(), "re_used_MWh": d.re_used_MW.sum(),
            "v_min_pu": d.v_min_pu.min(), "v_max_pu": d.v_max_pu.max(),
            "line_loading_max_pct": d.line_loading_max_pct.max(),
            "_base_peak": L.max(), "_base_net_peak": NL.max(), "_base_bill": (L * flat).sum()}

def run_all(cfg, out_file=None):
    cache = {"ratings": _calibrate_ratings(cfg)}; rows = []
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
    show = ["day", "scheme", "participation", "re_penetration", "net_peak_reduction_pct", "v_min_pu", "v_max_pu", "line_loading_max_pct"]
    print(df[show].to_string(index=False))
    return df