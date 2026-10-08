"""24 h DC-OPF (pandapower rundcopp per hour, or Pyomo) and AC power-flow checks.

TODO:
 - per hour: set bus loads, renewable injection, run OPF
 - collect: generation cost, generator output, curtailment, line loading
 - AC power flow at peak hour for voltage profile
"""
def run_day(net, load_mw, solar_pu, wind_pu):
    raise NotImplementedError
