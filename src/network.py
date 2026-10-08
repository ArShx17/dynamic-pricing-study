"""IEEE 14-bus network via pandapower + generator cost curves.

TODO:
 - net = pandapower.networks.case14()
 - scale loads so total = config peak_mw (case14 total is 259 MW)
 - add quadratic costs (pandapower.create_poly_cost): literature or India coal/gas
 - add solar/wind as sgen at chosen buses, capacity = renewable_penetration * peak
"""
def build_network(cfg):
    raise NotImplementedError
