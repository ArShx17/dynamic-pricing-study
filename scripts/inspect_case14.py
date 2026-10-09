import pandapower as pp
import pandapower.networks as pn

net = pn.case14()
print("Total load (MW):", net.load.p_mw.sum())
print("\nGenerators:\n", net.gen[["bus", "p_mw", "min_p_mw", "max_p_mw"]])
print("\nExternal grid limits:", net.ext_grid.min_p_mw.iloc[0], net.ext_grid.max_p_mw.iloc[0])
print("\nCost curves:\n", net.poly_cost[["element", "et", "cp1_eur_per_mw", "cp2_eur_per_mw2"]])

pp.runpp(net, numba=False)
print("\nVoltage range (pu):", net.res_bus.vm_pu.min().round(3), "to", net.res_bus.vm_pu.max().round(3))

pp.rundcopp(net)
print("DC-OPF cost at base load:", round(net.res_cost, 1))