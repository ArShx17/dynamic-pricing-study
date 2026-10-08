"""Load processed 24 h data for a given day type ('summer' | 'winter')."""
import pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def load_day(day):
    ld = pd.read_csv(ROOT / f"data/processed/{day}/load_renewables_{day}.csv")
    pr = pd.read_csv(ROOT / f"data/processed/{day}/price_signals_{day}.csv")
    return ld, pr
