from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, List
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from loguru import logger

MODEL_PATH = Path("src/models/saved/edupredict_v1.pkl")
DATA_PATH = Path("data/processed/enrollment_ml_ready.csv")

BASE_YEAR = 2024
FEATURES = [
    "year_index", "enrollment_lag1", "enrollment_lag3", "enrollment_rolling3",
    "gdp_per_capita_log", "edu_expenditure_lag1", "population_school_age", "region_encoded",
]
SCENARIOS = {
    "baseline":    {"gdp_growth": 0.0,   "edu_adj": 0.0},
    "optimistic":  {"gdp_growth": 0.015, "edu_adj": 0.005},
    "pessimistic": {"gdp_growth": -0.01, "edu_adj": -0.003},
}

app = FastAPI(
    title="EduPredict API",
    description="ML-powered global education enrollment forecasting.",
    version="1.2.0",
)

# ── Load resources at startup ──────────────────────────────────────────────────

model = None
base_df = None


@app.on_event("startup")
def load_resources():
    global model, base_df
    try:
        model = joblib.load(MODEL_PATH)
        df = pd.read_csv(DATA_PATH)
        base_df = df.sort_values("year").groupby("country_code").last().reset_index()
        logger.success("Model and data loaded successfully.")
    except Exception as e:
        logger.error(f"Startup error: {e}")


# ── Schemas ────────────────────────────────────────────────────────────────────

class PredictRequest(BaseModel):
    country_code: str = Field(..., example="USA", description="ISO 3166-1 alpha-3 code")
    horizon: Literal[5, 10, 15] = Field(10, description="Forecast horizon in years")
    scenario: Literal["baseline", "optimistic", "pessimistic"] = "baseline"


class ForecastPoint(BaseModel):
    forecast_year: int
    predicted_enrollment: float
    lower_bound: float
    upper_bound: float


class PredictResponse(BaseModel):
    country_code: str
    country_name: str
    region: str
    scenario: str
    horizon: int
    forecasts: List[ForecastPoint]
    model_version: str = "v1.2.0"


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    if model is None or base_df is None:
        raise HTTPException(status_code=503, detail="Model not loaded.")

    row = base_df[base_df["country_code"] == req.country_code.upper()]
    if row.empty:
        raise HTTPException(status_code=404, detail=f"Country '{req.country_code}' not found.")

    row = row.iloc[0]
    scenario_params = SCENARIOS[req.scenario]

    prev_enrollment = row["enrollment_total"]
    rolling_vals = [prev_enrollment] * 3
    gdp_log = float(row.get("gdp_per_capita_log", np.log1p(10000)))
    edu_exp = float(row.get("edu_expenditure_lag1", 4.0))

    forecasts = []
    for step in range(1, req.horizon + 1):
        year = BASE_YEAR + step
        gdp_log += scenario_params["gdp_growth"]
        edu_exp += scenario_params["edu_adj"]

        feat = {
            "year_index": year - 1970,
            "enrollment_lag1": rolling_vals[-1],
            "enrollment_lag3": rolling_vals[-3],
            "enrollment_rolling3": np.mean(rolling_vals[-3:]),
            "gdp_per_capita_log": gdp_log,
            "edu_expenditure_lag1": edu_exp,
            "population_school_age": float(row.get("population_school_age", 1e7)),
            "region_encoded": int(row.get("region_encoded", 0)),
        }
        X = pd.DataFrame([feat])[FEATURES]
        pred = float(model.predict(X)[0])
        rolling_vals.append(pred)

        forecasts.append(ForecastPoint(
            forecast_year=year,
            predicted_enrollment=round(pred),
            lower_bound=round(pred * 0.92),
            upper_bound=round(pred * 1.08),
        ))

    return PredictResponse(
        country_code=row["country_code"],
        country_name=str(row.get("country_name", "")),
        region=str(row.get("region", "")),
        scenario=req.scenario,
        horizon=req.horizon,
        forecasts=forecasts,
    )
