# EduPredict — User Guide

> Last updated: 2026  
> Maintained by: Visualization / Dashboard Team

---

## What is EduPredict?

EduPredict is an interactive dashboard that lets you explore forecasted student enrollment trends for countries worldwide. You can filter by region, select a scenario, and view 5, 10, or 15-year projections — all in under 60 seconds.

---

## Getting Started

### Requirements

- Python 3.10 or higher
- Dependencies installed via `pip install -r requirements.txt`

### Launch the Dashboard

```bash
streamlit run src/dashboard/app.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`.

---

## Dashboard Layout

### Left Panel — Controls

| Control | Description |
|---|---|
| **Region Filter** | Select one or more world regions to focus on |
| **Country Filter** | Narrow down to specific countries within selected regions |
| **Scenario Selector** | Choose Baseline, Optimistic, or Pessimistic |
| **Horizon Selector** | Select forecast length: 5, 10, or 15 years |

> Tip: Start by selecting a Region first — the Country dropdown will update automatically.

### Main Panel — Visualizations

**Forecast Line Chart**
The primary chart shows projected enrollment over the selected horizon. The shaded band represents the 95% confidence interval.

**Scenario Comparison Chart**
When "All Scenarios" is selected, three lines are shown side-by-side for easy comparison.

### Bottom Panel — Data & Export

**Summary Table**
Shows year-by-year forecast values including lower and upper bounds.

**Export Button**
Click "Download CSV" to export the current forecast results for the selected filters.

---

## Using the API

EduPredict also exposes a REST API for programmatic access.

### Base URL (deployed)
```
https://your-server-domain.com
```

### Health Check
```
GET /health
```
Returns `{"status": "ok"}` if the API is running.

### Forecast Endpoint
```
POST /predict
Content-Type: application/json

{
  "country_code": "BRA",
  "horizon": 10,
  "scenario": "optimistic"
}
```

**Response:**
```json
{
  "country_code": "BRA",
  "country_name": "Brazil",
  "scenario": "optimistic",
  "horizon": 10,
  "forecasts": [
    {
      "forecast_year": 2026,
      "predicted_enrollment": 52400000,
      "lower_bound": 49100000,
      "upper_bound": 55700000
    }
  ]
}
```

### Valid Parameters

| Parameter | Type | Options |
|---|---|---|
| `country_code` | string | Any valid ISO 3166-1 alpha-3 code |
| `horizon` | integer | `5`, `10`, or `15` |
| `scenario` | string | `"baseline"`, `"optimistic"`, `"pessimistic"` |

---

## Interpreting Forecasts

| Scenario | What It Assumes |
|---|---|
| **Baseline** | GDP and education spending follow historical trends |
| **Optimistic** | Stronger economic growth + increased education investment |
| **Pessimistic** | Economic slowdown + reduced education funding |

The shaded confidence band in the chart shows the 95% interval — forecasts outside that range are statistically unlikely under the chosen scenario.

**Important:** Forecasts beyond 10 years are long-range projections. Treat them as directional guidance, not precise predictions.

---

## Frequently Asked Questions

**Q: Why does my country not appear in the dropdown?**  
Countries with more than 30% missing data in the source dataset were excluded from the model. Check the data dictionary for coverage details.

**Q: How often is the model updated?**  
The current model was trained on data through 2024. Future updates will incorporate new UNESCO/World Bank releases.

**Q: Can I use the API without the dashboard?**  
Yes. The `/predict` endpoint works independently. See the API section above.

**Q: Where does the underlying data come from?**  
UNESCO Institute for Statistics and World Bank EdStats. See the data dictionary for full source details.

---

## Troubleshooting

| Issue | Solution |
|---|---|
| Dashboard won't start | Confirm `streamlit` is installed: `pip install streamlit` |
| "Model file not found" error | Run `python src/models/train.py` first to generate the model file |
| Empty chart / no data | Check that `data/exports/forecast_output.csv` exists; re-run `python src/models/predict_all.py` |
| API returns 422 error | Verify your JSON payload matches the required schema above |

---

## Contact & Feedback

For issues or questions, open a GitHub Issue in the EduPredict repository or contact the team lead.
