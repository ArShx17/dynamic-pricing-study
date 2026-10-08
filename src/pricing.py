"""Pricing helpers: net load, revenue-neutral scaling, net-load-based RTP and CPP."""
import numpy as np

def net_load(load_mw, solar_pu, wind_pu, penetration=0.20, peak_mw=259.0, solar_share=0.6):
    """Net load = demand - renewable output. RE capacity = penetration * peak_mw, split solar/wind."""
    cap = penetration * peak_mw
    re = cap * (solar_share * np.asarray(solar_pu) + (1 - solar_share) * np.asarray(wind_pu))
    return np.asarray(load_mw, float) - re

def revenue_neutral(price, load_mw, flat_price):
    """Scale price so revenue on the baseline load equals the flat-tariff revenue."""
    price, load_mw = np.asarray(price, float), np.asarray(load_mw, float)
    target = (np.asarray(flat_price, float) * load_mw).sum()
    return price * target / (price * load_mw).sum()

def rtp_from_net_load(net, load_mw, flat_price, pmin=3000.0, pmax=9000.0, k=2):
    """Scarcity-style RTP that follows net load (Rs/MWh), then scaled to revenue neutrality."""
    x = (net - net.min()) / (net.max() - net.min())
    return revenue_neutral(pmin + (pmax - pmin) * x ** k, load_mw, flat_price)

def cpp_from_net_load(net, load_mw, flat_price, base_price, n_hours=4, multiplier=3.0):
    """Critical peak: the n_hours with highest net load priced at multiplier x base; revenue-neutral."""
    p = np.full(len(net), float(base_price))
    p[np.argsort(net)[-n_hours:]] *= multiplier
    return revenue_neutral(p, load_mw, flat_price)