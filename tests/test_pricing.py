import numpy as np
from src.pricing import net_load, revenue_neutral, rtp_from_net_load, cpp_from_net_load

L = 200 + 50*np.sin(np.linspace(0, 2*np.pi, 24)); FLAT = np.full(24, 6000.0)

def test_revenue_neutral():
    p = revenue_neutral(np.linspace(3000, 9000, 24), L, FLAT)
    assert np.isclose((p*L).sum(), (FLAT*L).sum())

def test_rtp_follows_net_load():
    net = L - 30*np.clip(np.sin(np.linspace(0, np.pi, 24)), 0, None)
    p = rtp_from_net_load(net, L, FLAT)
    assert p.argmax() == net.argmax() and np.isclose((p*L).sum(), (FLAT*L).sum())

def test_cpp_hits_top_hours():
    net = np.arange(24.0); p = cpp_from_net_load(net, L, FLAT, 6000.0)
    assert (p[-4:] > p[:-4].max()).all()

def test_net_load_lower():
    assert (net_load(L, np.ones(24), np.ones(24)) < L).all()