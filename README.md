# Student Performance Analytics & Prediction System

**Data-driven insights into student achievement**

---

## Abstract

This application analyses real student performance data from Portuguese secondary schools, identifies patterns associated with academic outcomes, and estimates final grades using machine learning regression models. It is built as an educational internship project demonstrating a complete data science pipeline within a professional interactive dashboard.

---

## Problem Statement

Educational institutions collect rich data about student demographics, study habits, and social factors, but lack accessible tools to explore patterns in that data or estimate likely outcomes. This project builds an interactive analytics system that bridges raw data and actionable insight — while maintaining responsible, non-deterministic framing of predictions.

---

## Objectives

1. Acquire and validate real, publicly available student performance data
2. Perform exploratory data analysis and visualise findings
3. Build a preprocessing pipeline using scikit-learn
4. Train and compare four regression models
5. Evaluate models fairly on a held-out test set
6. Provide an interactive grade estimation interface
7. Present everything through a polished Streamlit dashboard

---

## Datasets

### UCI Student Performance (Mandatory)

| Property | Details |
|---|---|
| Source | UCI Machine Learning Repository |
| URL | https://archive.ics.uci.edu/dataset/320/student+performance |
| Citation | Cortez & Silva, FUBUTEC 2008 |
| License | CC BY 4.0 |
| Files | student-mat.csv (395 records), student-por.csv (649 records) |
| Target | G3 — Final grade (0–20 scale) |
| Delimiter | Semicolon (;) |

Both files are from the **same study** covering two Portuguese schools. They are not independent datasets.

---

## System Architecture

```
Public Dataset (UCI) 
    → data_loader.py (validate & load) 
    → preprocessing.py (ColumnTransformer pipeline) 
    → train_models.py (80/20 split, train 4 models) 
    → evaluation.py (MAE, RMSE, R² on test set) 
    → predictions.py (single-student inference) 
    → visualizations.py (Plotly charts) 
    → Streamlit pages (interactive dashboard)
```

---

## Technologies

- Python 3.11+
- Streamlit 1.35
- pandas 2.2, NumPy 1.26
- scikit-learn 1.4 (preprocessing + models)
- Plotly 5.22 (interactive charts)
- joblib 1.4 (model persistence)
- requests 2.32 (auto-download)

---

## Installation

```bash
cd student_performance_analytics
python -m pip install -r requirements.txt
```

---

## Running the Application

```bash
python -m streamlit run app.py
```

The app will attempt to download the UCI datasets automatically on first run.  
If automatic download fails, see `data/README.md` for manual instructions.

---

## Dataset Download (Manual)

1. Visit https://archive.ics.uci.edu/dataset/320/student+performance
2. Click **Download**
3. Extract the ZIP → extract the inner `student.zip`
4. Place `student-mat.csv` and `student-por.csv` in the `data/` folder
5. Restart the application

---

## Project Limitations

- Dataset covers two Portuguese schools circa 2005–2006; results may not generalise
- G1, G2 excluded from inputs by design (predicting without mid-year grades)
- No hyperparameter tuning applied
- OULAD is a future extension, not included in this version

---

## Responsible Use

This system is an educational demonstration tool. Predictions must not be used to make high-stakes decisions about individual students. See the **About** page in the application for the full responsible use statement.

---

## License

Dataset: CC BY 4.0 (Cortez & Silva, 2008)  
Application code: Academic use / internship project
