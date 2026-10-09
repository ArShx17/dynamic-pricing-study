"""24 h DC optimal power flow: cost, generator schedule and renewable curtailment."""
import numpy as np
import pandas as pd
import pandapower as pp
from src.network import set_hour

def run_day(net, load_mw, solar_pu, wind_pu):
    """Run DC-OPF for each of 24 hours. Returns one row per hour."""
    rows = []
    for h in range(24):
        set_hour(net, float(load_mw[h]), float(solar_pu[h]), float(wind_pu[h]))
        pp.rundcopp(net)
        avail = float(net.sgen.max_p_mw.sum())
        used = float(net.res_sgen.p_mw.sum())
        row = {"hour": h, "load_MW": float(load_mw[h]), "cost": float(net.res_cost),
               "ext_grid_MW": float(net.res_ext_grid.p_mw.iloc[0]),
               "re_avail_MW": avail, "re_used_MW": used, "curtailed_MW": max(avail - used, 0.0)}
        for i, p in enumerate(net.res_gen.p_mw.values):
            row[f"gen{i+1}_MW"] = float(p)
        rows.append(row)
    return pd.DataFrame(rows)