import yaml
from pathlib import Path
from src.sensitivity import run_sensitivity
from src import plotting

cfg = yaml.safe_load(open("config.yaml"))
sens = run_sensitivity(cfg)
out = Path("paper/figures")
plotting.fig_sensitivity(sens, cfg, "elasticity_scale", "Elasticity multiplier (1 = base case)", out / "fig5_sens_elasticity.png")
plotting.fig_sensitivity(sens, cfg, "re_penetration", "Renewable capacity / peak load", out / "fig6_sens_renewables.png")
plotting.fig_sensitivity(sens, cfg, "cross_ratio", "Cross-elasticity ratio", out / "fig7_sens_cross.png")
for sweep in ["elasticity_scale", "re_penetration", "cross_ratio"]:
    t = sens[sens.sweep == sweep].pivot_table(index=["day", "value"], columns="scheme", values="net_peak_reduction_pct")
    print(f"\n{sweep} (net peak reduction %, positive = lower):\n", t.round(2).to_string())
    best = t.idxmax(axis=1); print("best scheme:", dict(best))