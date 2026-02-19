import pandas as pd

class Preprocessor:
    def clean(self, df: pd.DataFrame):
        df = df.copy()
        df.drop_duplicates(inplace=True)
        df.fillna(0, inplace=True)
        return df