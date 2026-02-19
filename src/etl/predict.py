import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from loguru import logger

MODEL_PATH = Path("src/models/saved/edupredict_v1.pkl")
DATA_PATH = Path("data/processed/enrollment_ml_ready.csv")
EXPORT_PATH = Path("data/exports/forecast_output.csv")

FEATURES = [
    "year_index",
    "enrollment_lag1",
    "enrollment_lag3",
    "enrollment_rolling3",
    "gdp_per_capita_log",
    "edu_expenditure_lag1",
    "population_school_age",
    "region_encoded",
]

HORIZONS = [5, 10, 15]
BASE_YEAR = 2024

SCENARIOS = {
    "baseline":    {"gdp_growth": 0.0,   "edu_adj": 0.0},
    "optimistic":  {"gdp_growth": 0.015, "edu_adj": 0.005},
    "pessimistic": {"gdp_growth": -0.01, "edu_adj": -0.003},
}


def load_model():
    logger.info(f"Loading model from {MODEL_PATH}")
    return joblib.load(MODEL_PATH)


def load_base(base_year: int) -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    return df[df["year"] == base_year].copy()


def project(row: pd.Series, model, horizon: int, scenario: dict) -> list:
    results = []
    prev_enrollment = row["enrollment_total"]
    rolling_vals = [prev_enrollment] * 3
    gdp_log = row.get("gdp_per_capita_log", np.log1p(10000))
    edu_exp = row.get("edu_expenditure_lag1", 4.0)

    for step in range(1, horizon + 1):
        year = BASE_YEAR + step
        gdp_log += scenario["gdp_growth"]
        edu_exp += scenario["edu_adj"]

        feat = {
            "year_index": year - 1970,
            "enrollment_lag1": rolling_vals[-1],
            "enrollment_lag3": rolling_vals[-3] if len(rolling_vals) >= 3 else rolling_vals[0],
            "enrollment_rolling3": np.mean(rolling_vals[-3:]),
            "gdp_per_capita_log": gdp_log,
            "edu_expenditure_lag1": edu_exp,
            "population_school_age": row.get("population_school_age", 1e7),
            "region_encoded": row.get("region_encoded", 0),
        }
        X = pd.DataFrame([feat])[FEATURES]
        pred = float(model.predict(X)[0])
        rolling_vals.append(pred)

        # Simple residual-based confidence interval (±8%)
        results.append({
            "country_code": row["country_code"],
            "country_name": row.get("country_name", ""),
            "region": row.get("region", ""),
            "forecast_year": year,
            "horizon": horizon,
            "predicted_enrollment": round(pred),
            "lower_bound": round(pred * 0.92),
            "upper_bound": round(pred * 1.08),
            "model_version": "v1.2.0",
        })

    return results


def run():
    model = load_model()
    base_df = load_base(BASE_YEAR)

    if base_df.empty:
        logger.warning(f"No rows found for base year {BASE_YEAR}. Using most recent year per country.")
        df = pd.read_csv(DATA_PATH)
        base_df = df.sort_values("year").groupby("country_code").last().reset_index()

    all_records = []
    for _, row in base_df.iterrows():
        for scenario_name, scenario_params in SCENARIOS.items():
            for horizon in HORIZONS:
                records = project(row, model, horizon, scenario_params)
                for r in records:
                    r["scenario"] = scenario_name
                all_records.extend(records)

    output = pd.DataFrame(all_records)
    EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(EXPORT_PATH, index=False)
    logger.success(f"Forecasts written to {EXPORT_PATH} ({len(output):,} rows)")


if __name__ == "__main__":
    run()
