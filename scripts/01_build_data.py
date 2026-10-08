"""Phase 3 - REAL India dataset for the dynamic-pricing study (IEEE 14-bus, 24 h).
Sources
  Demand (hourly, Northern Region, 2019-01..2024-04), solar/wind (15-min SCADA, 2024-11..2026-09),
  Rajasthan daily supply position : Grid-India / NLDC daily PSP reports, as compiled in
      github.com/HalcyonVector/Grid-Sentinel (Dataset/, CC BY-SA 4.0).
  TOU tariff : Prayas (Energy Group) study for RERC, July 2024, Annexure 2 Table 7 (2025-26, 4-season, 5-slot).
  Base energy charge : Rs 6.50/kWh (RERC FY2026, large industry; Mercom 8 Oct 2025).
  Market price shape : IEX ACP weighted by Rajasthan purchases 2022-23, values reported in Prayas Sec. 5.2 (approximate).
Run:  git clone --depth 1 https://github.com/HalcyonVector/Grid-Sentinel.git gs ; python build_india_dataset.py gs/Dataset
"""
import sys, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
D = sys.argv[1] if len(sys.argv) > 1 else "gs/Dataset"
PEAK_MW, BASE = 259.0, 6500.0            # IEEE-14 total load; Rs/MWh

# ---------- demand: Northern Region hourly ----------
h = pd.read_csv(f"{D}/study1_hourly.csv", usecols=["datetime","National Hourly Demand","Northern Region Hourly Demand"],
                parse_dates=["datetime"]).set_index("datetime")
h.columns = ["national_MW","northern_region_MW"]; h.round(2).to_csv("nr_hourly_2019_2024.csv")
nr = h.northern_region_MW
d_sum, d_win = nr["2023"].idxmax().date(), nr["2023-11-01":"2024-02-29"].idxmax().date()
scale = PEAK_MW / nr[str(d_sum)].max()

# ---------- solar / wind: SCADA 15-min -> hourly, monthly-mean profile (p.u. of observed max) ----------
s = pd.read_csv(f"{D}/study2_scada.csv", usecols=["date","time","demand_met_mw","wind_mw","solar_mw"])
s["ts"] = pd.to_datetime(s.date.astype(str)+" "+s.time.astype(str)); s = s.set_index("ts")
hr = s[["demand_met_mw","wind_mw","solar_mw"]].resample("h").mean()
hr["solar_mw"] = hr.solar_mw.clip(lower=0)
hr.round(1).to_csv("scada_national_hourly_2024_2026.csv")
smax, wmax = hr.solar_mw.quantile(.999), hr.wind_mw.quantile(.999)
def prof(month_str):
    m = hr.loc[month_str]; g = m.groupby(m.index.hour).mean()
    return (g.solar_mw/smax).clip(0,1).values, (g.wind_mw/wmax).clip(0,1).values
RE = {"summer":"2025-09", "winter":"2026-01"}

# ---------- Prayas Table 7 (2025-26), % of energy charge: [06-09, 09-18, 18-22, 22-04, 04-06] ----------
TOD = {"summer":[0,-20,15,0,0],         # Sep-Oct column
       "winter":[5,-15,5,-5,0]}         # Nov-Feb column
slot = lambda x: 0 if 6<=x<9 else 1 if 9<=x<18 else 2 if 18<=x<22 else 4 if 4<=x<6 else 3
def mkt(season):
    p = np.zeros(24)
    for x in range(24):
        if season=="summer": p[x] = 8000 if (x>=18 or x<4) else 4500 if x<6 else 5000 if x<9 else 3800 if x<17 else 6000
        else: p[x] = {18:8000,19:7000,20:5500,21:4000}.get(x, 3000 if (x>=22 or x<6) else 7500 if x<11 else 5500)
    return p

days = {"summer":d_sum, "winter":d_win}; out = {}
for k, d in days.items():
    L = (nr[str(d)] * scale).values; x = np.arange(24)
    sol, wnd = prof(RE[k])
    tou = np.array([BASE*(1+TOD[k][slot(i)]/100) for i in x])
    flat = np.full(24, (tou*L).sum()/L.sum())                       # revenue-neutral flat tariff
    cpp = tou.copy(); cpp[18:22] = BASE*3.0                         # CPP event (scenario parameter)
    pd.DataFrame({"hour":x,"load_MW":L.round(2),"solar_pu":sol.round(3),"wind_pu":wnd.round(3)}).to_csv(f"load_renewables_{k}.csv",index=False)
    pd.DataFrame({"hour":x,"flat":flat,"TOU":tou,"RTP":mkt(k),"CPP":cpp}).round(0).to_csv(f"price_signals_{k}.csv",index=False)
    out[k] = (L, sol, wnd, tou, flat, mkt(k), cpp)
    print(f"{k}: load day {d}  peak {L.max():.0f} MW @h{L.argmax()}  LF {L.mean()/L.max():.3f}  PAR {L.max()/L.mean():.3f}")

# ---------- Rajasthan daily supply position ----------
st = pd.read_csv(f"{D}/study3_states.csv"); r = st[st.state.str.contains("Rajasthan",case=False,na=False)]
r.to_csv("rajasthan_daily_2018_2026.csv", index=False)

fig, ax = plt.subplots(2,3,figsize=(15,7)); x = np.arange(24)
for i,(k,(L,sol,wnd,tou,flat,rtp,cpp)) in enumerate(out.items()):
    ax[i,0].plot(x,L,"k"); ax[i,0].set_title(f"{k}: NR load scaled to IEEE-14, {days[k]}")
    for n,v in [("flat",flat),("TOU",tou),("RTP",rtp),("CPP",cpp)]: ax[i,1].step(x,v/1000,where="mid",label=n)
    ax[i,1].set_title(f"{k}: prices (Rs/kWh)"); ax[i,1].legend(fontsize=7)
    ax[i,2].plot(x,sol,label="solar"); ax[i,2].plot(x,wnd,label="wind"); ax[i,2].legend(); ax[i,2].set_title(f"{k}: SCADA solar/wind (p.u.) {RE[k]}")
plt.tight_layout(); plt.savefig("phase3_india_overview.png",dpi=140)
