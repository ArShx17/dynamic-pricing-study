import yaml
from src.scenarios import run_all
if __name__ == "__main__":
    run_all(yaml.safe_load(open("config.yaml")))
