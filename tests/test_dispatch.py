import numpy as np
from src.network import build_network
from src.dispatch import run_day

CFG = {"peak_mw": 259.0, "renewable_penetration": 0.20}

def test_day_balances_and_costs_positive():
    net = build_network(CFG)
    load = 200 + 40*np.sin(np.linspace(0, 2*np.pi, 24))
    res = run_day(net, load, np.full(24, 0.5), np.full(24, 0.3))
    assert len(res) == 24 and (res.cost > 0).all()
    gen_cols = [c for c in res.columns if c.startswith("gen")]
    supply = res[gen_cols].sum(axis=1) + res.ext_grid_MW + res.re_used_MW
    assert np.allclose(supply, res.load_MW, atol=1e-2)

def test_more_renewables_lower_cost():
    net = build_network(CFG); load = np.full(24, 200.0)
    low = run_day(net, load, np.zeros(24), np.zeros(24)).cost.sum()
    high = run_day(net, load, np.ones(24), np.ones(24)).cost.sum()
    assert high < low