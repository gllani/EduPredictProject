import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from xgboost import XGBRegressor
from loguru import logger

DATA_PATH = Path("data/processed/enrollment_ml_ready.csv")
MODEL_DIR = Path("src/models/saved")
MODEL_PATH = MODEL_DIR / "edupredict_v1.pkl"

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
TARGET = "enrollment_total"

TRAIN_END = 2018
VAL_END = 2021


def load_data() -> pd.DataFrame:
    logger.info(f"Loading data from {DATA_PATH}")
    return pd.read_csv(DATA_PATH)


def split(df: pd.DataFrame):
    train = df[df["year"] <= TRAIN_END]
    val = df[(df["year"] > TRAIN_END) & (df["year"] <= VAL_END)]
    test = df[df["year"] > VAL_END]
    logger.info(f"Train: {len(train):,} | Val: {len(val):,} | Test: {len(test):,}")
    return train, val, test


def train(train_df: pd.DataFrame) -> XGBRegressor:
    logger.info("Training XGBoost model...")
    model = XGBRegressor(
        n_estimators=400,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1,
    )
    X = train_df[FEATURES].fillna(0)
    y = train_df[TARGET]
    model.fit(X, y)
    logger.success("Training complete.")
    return model


def evaluate(model: XGBRegressor, df: pd.DataFrame, label: str) -> dict:
    X = df[FEATURES].fillna(0)
    y = df[TARGET]
    preds = model.predict(X)
    rmse = np.sqrt(mean_squared_error(y, preds))
    mae = mean_absolute_error(y, preds)
    r2 = r2_score(y, preds)
    logger.info(f"[{label}] RMSE={rmse:,.0f} | MAE={mae:,.0f} | R²={r2:.4f}")
    return {"split": label, "rmse": rmse, "mae": mae, "r2": r2}


def save_model(model: XGBRegressor) -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    logger.success(f"Model saved to {MODEL_PATH}")


def run():
    df = load_data()
    train_df, val_df, test_df = split(df)
    model = train(train_df)
    evaluate(model, val_df, "Validation")
    evaluate(model, test_df, "Test")
    save_model(model)


if __name__ == "__main__":
    run()
