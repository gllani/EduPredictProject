import pandas as pd
from pathlib import Path

class DataLoader:
    def __init__(self, raw_path="data/raw"):
        self.raw_path = Path(raw_path)

    def load_csv(self, filename):
        path = self.raw_path / filename
        return pd.read_csv(path)