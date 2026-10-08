import numpy as np
from src.demand_response import apply_dr, apply_dr_classes, elasticity_matrix

LOAD = 200 + 50*np.sin(np.linspace(0, 2*np.pi, 24))
FLAT = np.full(24, 6000.0)
TOU = np.where((np.arange(24) >= 18) & (np.arange(24) < 22), 9000.0, 5000.0)

def test_zero_participation_unchanged():
    assert np.allclose(apply_dr(LOAD, TOU, FLAT, -0.2, participation=0.0), LOAD)

def test_flat_price_unchanged():
    assert np.allclose(apply_dr(LOAD, FLAT, FLAT, -0.2), LOAD)

def test_energy_conserved():
    assert np.isclose(apply_dr(LOAD, TOU, FLAT, -0.2).sum(), LOAD.sum())

def test_high_price_hours_reduce():
    new = apply_dr(LOAD, TOU, FLAT, -0.2, participation=0.5)
    assert new[19] < LOAD[19]

def test_more_participation_more_shift():
    a = abs(apply_dr(LOAD, TOU, FLAT, -0.2, participation=0.1) - LOAD).sum()
    b = abs(apply_dr(LOAD, TOU, FLAT, -0.2, participation=0.5) - LOAD).sum()
    assert b > a

def test_matrix_signs():
    E = elasticity_matrix(-0.2)
    assert (np.diag(E) < 0).all() and (E[~np.eye(24, dtype=bool)] >= 0).all()

def test_classes_sum():
    mix = {"r": .4, "c": .35, "i": .25}; el = {"r": -.15, "c": -.1, "i": -.05}
    assert np.isclose(apply_dr_classes(LOAD, TOU, FLAT, mix, el).sum(), LOAD.sum())