import yaml
from src.scenarios import run_all

def test_s0_is_baseline_and_rows_exist():
    cfg = yaml.safe_load(open("config.yaml")); cfg["days"] = ["winter"]; cfg["participation"] = [0.3]
    df = run_all(cfg)
    s0 = df[(df.scheme == "S0_flat") & (df.re_penetration == cfg["renewable_penetration"])].iloc[0]
    assert s0.peak_reduction_pct == 0 and s0.cost_change_pct == 0 and s0.bill_change_pct == 0
    assert len(df) == 1 + 5 + 1 + 2