"""24 h DC optimal power flow, plus an AC power-flow check of voltages and line loading."""
import numpy as np
import pandas as pd
import pandapower as pp
from src.network import set_hour

def run_day(net, load_mw, solar_pu, wind_pu, ac_check=True):
    """DC-OPF each hour (cost, schedule, curtailment); optional AC power flow on that dispatch."""
    rows, line_i = [], np.zeros(len(net.line))
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
        if ac_check:                                    # AC power flow on the OPF dispatch
            net.gen["p_mw"] = net.res_gen.p_mw.values
            net.sgen["p_mw"] = net.res_sgen.p_mw.values
            pp.runpp(net, numba=False)
            row.update(v_min_pu=float(net.res_bus.vm_pu.min()), v_max_pu=float(net.res_bus.vm_pu.max()),
                       line_loading_max_pct=float(net.res_line.loading_percent.max()))
            line_i = np.maximum(line_i, net.res_line.i_ka.values)
        rows.append(row)
    df = pd.DataFrame(rows)
    df.attrs["line_i_ka_max"] = line_i
    return df