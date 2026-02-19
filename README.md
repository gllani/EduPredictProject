# EduPredict 🎓📊

> A machine learning forecasting system for global education enrollment trends — delivering 5, 10, and 15-year projections with optimistic, baseline, and pessimistic scenario modeling.

---

## Project Overview

EduPredict is a capstone data science product that forecasts student enrollment numbers across regions and countries. It combines a clean ETL pipeline, an interpretable ML model, and an interactive Streamlit dashboard — all deployed via a secure FastAPI endpoint.

**Final Delivery Deadline:** May 4, 2026

---

## Repository Structure

```
EduPredict/
│
├── data/
│   ├── raw/                  # Original, unmodified source data
│   ├── processed/            # Cleaned, ML-ready datasets
│   └── exports/              # Dashboard-ready output files
│
├── notebooks/
│   ├── eda/                  # Exploratory data analysis
│   ├── modeling/             # Model training & evaluation
│   └── feature_engineering/  # Feature construction experiments
│
├── src/
│   ├── etl/                  # Data ingestion & transformation scripts
│   ├── models/               # Model training, evaluation, serialization
│   └── dashboard/            # Streamlit app logic
│
├── docs/
│   ├── data_dictionary.md    # Field definitions & source metadata
│   ├── model_documentation.md # Model architecture, metrics, assumptions
│   └── user_guide.md         # How to run and use EduPredict
│   └── deployment_guide.md   # How to deploy and use EduPredict
│
├── app/                      # FastAPI deployment files
│   ├── app.py  
│   ├── main.py
├
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## Quickstart

### 1. Clone the Repository
```bash
git clone https://github.com/gllani/EduPredictProject.git
cd EduPredict
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the ETL Pipeline
```bash
python src/etl/pipeline.py
```

### 4. Train the Model
```bash
python src/models/train.py
```

### 5. Launch the Dashboard
```bash
streamlit run app/app.py
```

### 6. Start the API (local)
```bash
uvicorn app.main:app --reload
```

---

## Features

- **Forecast Engine** — 5, 10, and 15-year enrollment projections
- **Scenario Modeling** — Baseline, Optimistic, and Pessimistic scenarios
- **Region & Country Filters** — Drill down by geography
- **Interactive Dashboard** — Streamlit UI with charts, tables, and exports
- **REST API** — `/predict` endpoint for programmatic access
- **HTTPS Deployed** — Secure public endpoint via Nginx + Let's Encrypt

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| ML Framework | scikit-learn |
| Dashboard | Streamlit |
| API | FastAPI + Uvicorn |
| Server | Ubuntu + Nginx + Gunicorn |
| Infrastructure | AWS EC2 (or equivalent) |
| SSL | Let's Encrypt |

---

## Team

| Role | Responsibility |
|---|---|
| Research Team | Assumptions, scenario logic, domain validation |
| Data Engineering | ETL pipeline, data quality, data dictionary |
| ML Engineers | Model training, evaluation, API layer |
| Visualization Lead | Dashboard UI, integration, user guide |

---

## Evaluation Metrics

Models are evaluated using:
- **RMSE** — Root Mean Squared Error
- **MAE** — Mean Absolute Error
- **R²** — Coefficient of Determination

---

## Documentation

Full documentation is available in the `/docs` folder:
- [`data_dictionary.md`](docs/data_dictionary.md)
- [`model_documentation.md`](docs/model_documentation.md)
- [`user_guide.md`](docs/user_guide.md)

---

## License

This project is developed for academic capstone purposes. See `LICENSE` for details.
