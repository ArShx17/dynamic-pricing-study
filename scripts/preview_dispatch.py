import yaml
from src.data_loader import load_day
from src.network import build_network
from src.dispatch import run_day

cfg = yaml.safe_load(open("config.yaml"))
for day in cfg["days"]:
    ld, pr = load_day(day)
    net = build_network(cfg)
    solar = ld.solar_pu.values; wind = ld.wind_pu.values
    res = run_day(net, ld.load_MW.values, solar, wind)
    print(f"\n{day}: daily cost {res.cost.sum():.0f} | peak-hour cost {res.cost.max():.0f} (h{res.cost.idxmax()}) "
          f"| curtailed {res.curtailed_MW.sum():.1f} MWh | RE used {res.re_used_MW.sum():.0f} MWh")
    print(res[["hour", "load_MW", "cost", "ext_grid_MW", "re_used_MW"]].round(1).iloc[::4].to_string(index=False))