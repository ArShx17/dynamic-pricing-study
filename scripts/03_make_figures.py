import yaml
import pandas as pd
from pathlib import Path
from src import plotting

cfg = yaml.safe_load(open("config.yaml"))
df = pd.read_csv("results/tables/results.csv")
out = Path("paper/figures"); out.mkdir(parents=True, exist_ok=True)
plotting.fig_load_curves(cfg, out / "fig1_load_curves.png")
plotting.fig_net_load(cfg, out / "fig2_net_load.png")
plotting.fig_peak_bars(df, cfg, out / "fig3_net_peak_bars.png")
plotting.fig_participation(df, cfg, out / "fig4_participation_sweep.png")

s = df[(df.participation == 0.3) & (df.re_penetration == cfg["renewable_penetration"])]
cols = ["day", "scheme", "peak_MW", "load_factor", "PAR", "peak_reduction_pct", "net_peak_reduction_pct", "cost_change_pct", "bill_change_pct", "line_loading_max_pct", "v_min_pu", "v_max_pu"]
s[cols].to_csv("results/tables/summary_30pct.csv", index=False)
print("Saved 4 figures to paper/figures and results/tables/summary_30pct.csv")