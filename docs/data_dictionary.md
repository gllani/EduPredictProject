# EduPredict — Data Dictionary

> Last updated: 2026  
> Maintained by: Data Engineering Team

---

## Overview

This document describes all datasets used in EduPredict, including field names, data types, descriptions, valid ranges, and source metadata.

---

## 1. Raw Dataset — `data/raw/enrollment_raw.csv`

Primary source data ingested from public education databases (e.g., UNESCO, World Bank EdStats).

| Field Name | Data Type | Description | Example | Valid Range / Notes |
|---|---|---|---|---|
| `country_code` | string | ISO 3166-1 alpha-3 country code | `USA`, `BRA` | Must be valid ISO code |
| `country_name` | string | Full country name | `United States` | — |
| `region` | string | World Bank geographic region | `North America` | See Region Codes below |
| `year` | integer | Academic year (start year) | `2015` | 1970–2024 |
| `enrollment_total` | float | Total student enrollment (all levels) | `54200000.0` | > 0 |
| `enrollment_primary` | float | Primary school enrollment | `21000000.0` | > 0, ≤ enrollment_total |
| `enrollment_secondary` | float | Secondary school enrollment | `18500000.0` | > 0, ≤ enrollment_total |
| `enrollment_tertiary` | float | Tertiary/higher education enrollment | `14700000.0` | > 0, ≤ enrollment_total |
| `population_total` | float | Total national population | `331000000.0` | > 0 |
| `population_school_age` | float | Population aged 5–24 | `72000000.0` | > 0 |
| `gdp_per_capita_usd` | float | GDP per capita (current USD) | `63500.0` | > 0 |
| `literacy_rate` | float | Adult literacy rate (%) | `99.0` | 0–100 |
| `gov_edu_expenditure_pct` | float | Government expenditure on education (% of GDP) | `5.2` | 0–20 |
| `source` | string | Data source identifier | `UNESCO_2023` | — |

---

## 2. Processed Dataset — `data/processed/enrollment_ml_ready.csv`

Output of the ETL pipeline. Cleaned, imputed, and feature-engineered for model input.

| Field Name | Data Type | Description | Notes |
|---|---|---|---|
| `country_code` | string | ISO country code | Unchanged from raw |
| `region` | string | Geographic region | Encoded for modeling |
| `year` | integer | Academic year | — |
| `enrollment_total` | float | Cleaned total enrollment | Outliers capped at 99th percentile |
| `enrollment_rate` | float | Enrollment as % of school-age population | Derived: `enrollment_total / population_school_age` |
| `gdp_per_capita_log` | float | Log-transformed GDP per capita | Natural log applied to reduce skew |
| `edu_expenditure_lag1` | float | Education expenditure lagged 1 year | Created in feature engineering |
| `enrollment_lag1` | float | Enrollment lagged 1 year | Created in feature engineering |
| `enrollment_lag3` | float | Enrollment lagged 3 years | Created in feature engineering |
| `enrollment_rolling3` | float | 3-year rolling mean of enrollment | Smoothed trend feature |
| `year_index` | integer | Years since 1970 (0-based) | For time-series indexing |
| `region_encoded` | integer | Label-encoded region | For model input |

---

## 3. Export Dataset — `data/exports/forecast_output.csv`

Final forecast results written by the model. Used by the dashboard.

| Field Name | Data Type | Description | Notes |
|---|---|---|---|
| `country_code` | string | ISO country code | — |
| `country_name` | string | Full country name | — |
| `region` | string | Geographic region | — |
| `forecast_year` | integer | Projected year | 2025–2040 |
| `scenario` | string | Forecast scenario | `baseline`, `optimistic`, `pessimistic` |
| `horizon` | integer | Years from base year | 5, 10, or 15 |
| `predicted_enrollment` | float | Forecasted enrollment total | — |
| `lower_bound` | float | Lower confidence bound | 95% CI |
| `upper_bound` | float | Upper confidence bound | 95% CI |
| `model_version` | string | Model version used | e.g., `v1.2.0` |

---

## Region Codes

| Code | Region Name |
|---|---|
| `NAM` | North America |
| `LAC` | Latin America & Caribbean |
| `ECA` | Europe & Central Asia |
| `MENA` | Middle East & North Africa |
| `SSA` | Sub-Saharan Africa |
| `SAS` | South Asia |
| `EAP` | East Asia & Pacific |

---

## Missing Data Policy

| Field | Missing Rate Threshold | Imputation Strategy |
|---|---|---|
| `enrollment_total` | < 5% → impute | Linear interpolation by country |
| `gdp_per_capita_usd` | < 10% → impute | Regional median imputation |
| `literacy_rate` | < 20% → impute | Forward-fill per country |
| Any field | > 30% missing | Row excluded from training |

---

## Data Sources

| Source | URL | Access Date |
|---|---|---|
| UNESCO UIS | https://uis.unesco.org | 2025 |
| World Bank EdStats | https://datatopics.worldbank.org/education | 2025 |
| World Bank Open Data | https://data.worldbank.org | 2025 |

---

## Change Log

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-01 | Initial data dictionary |
| 1.1 | 2026-03 | Added export schema and region codes |
