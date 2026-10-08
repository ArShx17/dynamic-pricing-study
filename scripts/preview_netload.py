import yaml, numpy as np
from src.data_loader import load_day
from src.demand_response import apply_dr_classes
from src.pricing import net_load, revenue_neutral, rtp_from_net_load, cpp_from_net_load

cfg = yaml.safe_load(open("config.yaml"))
for day in cfg["days"]:
    ld, pr = load_day(day); L = ld.load_MW.values; flat = pr.flat.values
    re = L - net_load(L, ld.solar_pu, ld.wind_pu, cfg["renewable_penetration"], cfg["peak_mw"])
    NL = L - re
    prices = {"TOU": pr.TOU.values,
              "RTP (market shape, RN)": revenue_neutral(pr.RTP.values, L, flat),
              "CPP (RN)": revenue_neutral(pr.CPP.values, L, flat),
              "RTP-net": rtp_from_net_load(NL, L, flat),
              "CPP-net": cpp_from_net_load(NL, L, flat, flat.mean())}
    print(f"\n{day}: gross peak {L.max():.0f} MW @h{L.argmax()} | NET peak {NL.max():.0f} MW @h{NL.argmax()}")
    for name, p in prices.items():
        N = apply_dr_classes(L, p, flat, cfg["customer_mix"], cfg["elasticity"], cfg["cross_elasticity_ratio"], 0.3)
        NN = N - re
        print(f"  {name:24s} gross peak {100*(L.max()-N.max())/L.max():+6.2f}% | net peak {100*(NL.max()-NN.max())/NL.max():+6.2f}% (hr {NN.argmax():2d}) | bill {100*((N*p).sum()-(L*flat).sum())/(L*flat).sum():+5.1f}%")