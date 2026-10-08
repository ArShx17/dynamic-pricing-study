"""Metrics: peak reduction %, load factor, PAR, bill. TODO: cost, curtailment, rebound peak."""
import numpy as np

def load_factor(l): return float(np.mean(l) / np.max(l))
def par(l): return float(np.max(l) / np.mean(l))
def peak_reduction_pct(base, new): return 100 * (np.max(base) - np.max(new)) / np.max(base)
def bill(load_mw, price_rs_per_mwh): return float(np.sum(np.asarray(load_mw) * np.asarray(price_rs_per_mwh)))
