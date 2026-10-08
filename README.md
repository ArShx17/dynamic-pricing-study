# Estimating Impact of Dynamic Electricity Pricing on Power System Operation

IEEE 14-bus study of flat, TOU, RTP and CPP tariffs with elasticity-based demand response, using real
Indian grid data (Grid-India/NLDC via Grid-Sentinel, CC BY-SA 4.0) and the Rajasthan TOU tariff
(Prayas study for RERC, 2024).

## Setup
    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    pytest

## Workflow
    python -m scripts.02_run_scenarios
    python -m scripts.03_make_figures
(scripts/01_build_data.py regenerates data/processed; needs the Grid-Sentinel repo cloned.)

## Data caveats
Load = Northern Region (not Rajasthan alone); solar/wind = national per-unit shapes; RTP shape approximate;
TOU values are Prayas recommendations.

## Build order (Phase 4)
1 src/demand_response.py -> 2 src/network.py -> 3 src/dispatch.py -> 4 src/scenarios.py -> 5 figures
