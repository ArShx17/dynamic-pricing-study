import numpy as np
from src.metrics import load_factor, par, peak_reduction_pct

def test_flat_load():
    l = np.ones(24)
    assert load_factor(l) == 1.0 and par(l) == 1.0

def test_peak_reduction():
    assert round(peak_reduction_pct(np.array([100, 50]), np.array([90, 60])), 1) == 10.0
