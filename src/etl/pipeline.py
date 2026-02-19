import pandas as pd
import numpy as np
from pathlib import Path
from loguru import logger

RAW_PATH = Path("data/raw/enrollment_raw.csv")
PROCESSED_PATH = Path("data/processed/enrollment_ml_ready.csv")

REGION_MAP = {
    "North America": "NAM",
    "Latin America & Caribbean": "LAC",
    "Europe & Central Asia": "ECA",
    "Middle East & North Africa": "MENA",
    "Sub-Saharan Africa": "SSA",
    "South Asia": "SAS",
    "East Asia & Pacific": "EAP",
}

REGION_ENCODE = {v: i for i, v in enumerate(REGION_MAP.values())}


def load_raw(path: Path) -> pd.DataFrame:
    logger.info(f"Loading raw data from {path}")
    df = pd.read_csv(path)
    logger.info(f"Loaded {len(df):,} rows, {df.shape[1]} columns")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Cleaning data...")

    # Standardise column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Drop rows missing the target
    before = len(df)
    df = df.dropna(subset=["enrollment_total"])
    logger.info(f"Dropped {before - len(df)} rows missing enrollment_total")

    # Cap enrollment outliers at 99th percentile
    cap = df["enrollment_total"].quantile(0.99)
    df["enrollment_total"] = df["enrollment_total"].clip(upper=cap)

    # Impute GDP per capita with regional median
    df["gdp_per_capita_usd"] = df.groupby("region")["gdp_per_capita_usd"].transform(
        lambda x: x.fillna(x.median())
    )

    # Forward-fill literacy rate per country
    df = df.sort_values(["country_code", "year"])
    df["literacy_rate"] = df.groupby("country_code")["literacy_rate"].ffill()

    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Engineering features...")

    df = df.sort_values(["country_code", "year"]).copy()

    # Derived features
    df["enrollment_rate"] = df["enrollment_total"] / df["population_school_age"].replace(0, np.nan)
    df["gdp_per_capita_log"] = np.log1p(df["gdp_per_capita_usd"])
    df["year_index"] = df["year"] - 1970

    # Lag features
    grp = df.groupby("country_code")["enrollment_total"]
    df["enrollment_lag1"] = grp.shift(1)
    df["enrollment_lag3"] = grp.shift(3)
    df["enrollment_rolling3"] = grp.transform(lambda x: x.rolling(3, min_periods=1).mean()).shift(1)

    # Expenditure lag
    df["edu_expenditure_lag1"] = df.groupby("country_code")["gov_edu_expenditure_pct"].shift(1)

    # Encode region
    df["region_code"] = df["region"].map(REGION_MAP).fillna("UNK")
    df["region_encoded"] = df["region_code"].map(REGION_ENCODE).fillna(-1).astype(int)

    # Drop rows that still can't be used for training
    df = df.dropna(subset=["enrollment_lag1", "gdp_per_capita_log"])

    logger.info(f"Feature engineering complete. Final shape: {df.shape}")
    return df


def save(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    logger.success(f"Saved processed data to {path}")


def run():
    df = load_raw(RAW_PATH)
    df = clean(df)
    df = engineer_features(df)
    save(df, PROCESSED_PATH)
    logger.success("ETL pipeline complete.")


if __name__ == "__main__":
    run()
