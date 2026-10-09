import yaml
from src.sensitivity import run_sensitivity, SWEEPS, SCHEMES

def test_sensitivity_shape_and_base_case(tmp_path):
    cfg = yaml.safe_load(open("config.yaml")); cfg["days"] = ["winter"]
    df = run_sensitivity(cfg, tmp_path / "s.csv")
    assert len(df) == sum(len(v) for v in SWEEPS.values()) * len(SCHEMES)
    base = df[(df.sweep == "elasticity_scale") & (df.value == 1.0) & (df.scheme == "S2b_RTP_net")].net_peak_reduction_pct.iloc[0]
    assert abs(base - 1.027) < 0.01          # matches the main results table