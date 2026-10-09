"""Sensitivity of the main result (net peak reduction) to the assumed parameters. Demand response only (no OPF), so it is fast."""
import pandas as pd
from pathlib import Path
from src.data_loader import load_day
from src.demand_response import apply_dr_classes
from src.pricing import net_load
from src.scenarios import _prices

ROOT = Path(__file__).resolve().parents[1]
SWEEPS = {"elasticity_scale": [0.5, 1.0, 2.0, 3.0],      # multiplies every class self-elasticity
          "re_penetration": [0.1, 0.2, 0.3, 0.5],         # solar+wind capacity / peak load
          "cross_ratio": [0.1, 0.3, 0.5]}                 # cross-elasticity as share of self-elasticity
SCHEMES = ["S1_TOU", "S2_RTP", "S3_CPP", "S2b_RTP_net", "S3b_CPP_net"]

def run_sensitivity(cfg, out_file=None, participation=0.3):
    rows = []
    for day in cfg["days"]:
        ld, pr = load_day(day); L, flat = ld.load_MW.values, pr.flat.values
        sol, wnd = ld.solar_pu.values, ld.wind_pu.values
        for sweep, values in SWEEPS.items():
            for v in values:
                scale = v if sweep == "elasticity_scale" else 1.0
                pen = v if sweep == "re_penetration" else cfg["renewable_penetration"]
                cross = v if sweep == "cross_ratio" else cfg["cross_elasticity_ratio"]
                re = L - net_load(L, sol, wnd, pen, cfg["peak_mw"], cfg.get("solar_share", 0.6)); NL = L - re
                prices = _prices(L, NL, flat, pr)
                el = {c: e * scale for c, e in cfg["elasticity"].items()}
                for s in SCHEMES:
                    N = apply_dr_classes(L, prices[s], flat, cfg["customer_mix"], el, cross, participation)
                    rows.append({"day": day, "sweep": sweep, "value": v, "scheme": s,
                                 "peak_reduction_pct": 100 * (L.max() - N.max()) / L.max(),
                                 "net_peak_reduction_pct": 100 * (NL.max() - (N - re).max()) / NL.max()})
    df = pd.DataFrame(rows).round(3)
    target = Path(out_file) if out_file else ROOT / "results" / "tables" / "sensitivity.csv"
    target.parent.mkdir(parents=True, exist_ok=True); df.to_csv(target, index=False)
    return df