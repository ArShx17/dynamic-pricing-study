import pandapower as pp
from src.network import build_network, set_hour

CFG = {"peak_mw": 259.0, "renewable_penetration": 0.20}

def test_total_load():
    assert abs(build_network(CFG).load.p_mw.sum() - 259.0) < 1e-6

def test_set_hour_scales_load():
    net = build_network(CFG); set_hour(net, 200.0, 0.5, 0.5)
    assert abs(net.load.p_mw.sum() - 200.0) < 1e-6

def test_opf_runs_and_balances():
    net = build_network(CFG); set_hour(net, 200.0, 0.5, 0.5)
    pp.rundcopp(net)
    supply = net.res_gen.p_mw.sum() + net.res_ext_grid.p_mw.sum() + net.res_sgen.p_mw.sum()
    assert abs(supply - 200.0) < 1e-3