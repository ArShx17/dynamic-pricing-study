"""Price-elasticity demand response (Phase 4, step 1).

Model (per customer class c, participating share a):
    delta_d(t) = a * d_c(t) * sum_k E[t,k] * (p(k) - p0(k)) / p0(k)
    E[t,t]  = self-elasticity (< 0)
    E[t,k]  = cross-elasticity (> 0) for hours within +-window of t
Daily energy is conserved by proportional rescaling.
"""
import numpy as np

def elasticity_matrix(self_e, cross_ratio=0.3, window=3, n=24):
    E = np.zeros((n, n))
    for t in range(n):
        ks = [k for k in range(n) if k != t and abs(k - t) <= window]
        w = np.array([1.0 / abs(k - t) for k in ks]); w /= w.sum()
        for k, wk in zip(ks, w):
            E[t, k] = cross_ratio * abs(self_e) * wk
        E[t, t] = self_e
    return E

def apply_dr(load_mw, price, base_price, self_e, cross_ratio=0.3, participation=0.3, window=3):
    d0 = np.asarray(load_mw, float); p = np.asarray(price, float)
    p0 = np.broadcast_to(np.asarray(base_price, float), p.shape)
    E = elasticity_matrix(self_e, cross_ratio, window, len(d0))
    delta = participation * d0 * (E @ ((p - p0) / p0))
    new = d0 + delta
    return new * d0.sum() / new.sum()

def apply_dr_classes(load_mw, price, base_price, mix, elasticity, cross_ratio=0.3, participation=0.3, window=3):
    d0 = np.asarray(load_mw, float)
    return sum(apply_dr(d0 * share, price, base_price, elasticity[c], cross_ratio, participation, window)
               for c, share in mix.items())