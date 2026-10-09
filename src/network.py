"""IEEE 14-bus network (pandapower case14) with scalable load and renewable injections."""
import pandapower as pp
import pandapower.networks as pn

SOLAR_BUS, WIND_BUS = 8, 13          # 0-indexed bus numbers where renewables connect (assumption)

def build_network(cfg):
    net = pn.case14()
    scale = cfg["peak_mw"] / net.load.p_mw.sum()
    net.load["p_mw"] = net.load.p_mw * scale
    net.load["q_mvar"] = net.load.q_mvar * scale
    net.load["p_share"] = net.load.p_mw / net.load.p_mw.sum()      # each bus's share of system load
    net.load["q_ratio"] = net.load.q_mvar / net.load.p_mw          # keeps power factor constant

    cap = cfg["renewable_penetration"] * cfg["peak_mw"]
    share = cfg.get("solar_share", 0.6)
    net["re_cap"] = {"solar": cap * share, "wind": cap * (1 - share)}
    for name, bus, c in [("solar", SOLAR_BUS, cap * share), ("wind", WIND_BUS, cap * (1 - share))]:
        i = pp.create_sgen(net, bus, p_mw=0.0, name=name, controllable=True, min_p_mw=0.0, max_p_mw=c)
        pp.create_poly_cost(net, i, "sgen", cp1_eur_per_mw=0.0)    # zero cost: used first, curtailed only if needed
    return net

def set_hour(net, total_load_mw, solar_pu, wind_pu):
    """Set load for one hour (split by bus share) and the available renewable output."""
    net.load["p_mw"] = net.load.p_share * total_load_mw
    net.load["q_mvar"] = net.load.p_mw * net.load.q_ratio
    avail = {"solar": net["re_cap"]["solar"] * solar_pu, "wind": net["re_cap"]["wind"] * wind_pu}
    for name, a in avail.items():
        net.sgen.loc[net.sgen.name == name, "max_p_mw"] = a