import pandas as pd

class FeatureEngineer:
    def create_features(self, df: pd.DataFrame):
        df = df.copy()
        if 'study_hours' in df.columns and 'attendance' in df.columns:
            df['engagement_score'] = df['study_hours'] * 0.6 + df['attendance'] * 0.4
        return df