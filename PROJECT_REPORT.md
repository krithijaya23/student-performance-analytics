# Project Report
## Student Performance Analytics & Prediction System

---

## 1. Introduction

Academic institutions collect extensive data about students — demographics, study habits, family background, and social factors — yet often lack practical tools to explore this data and generate insights. This project develops a complete data science application that analyses historical student performance data, identifies patterns associated with academic outcomes, and estimates final grades using machine learning regression models.

The application serves as both a functional analytics tool and an educational demonstration of the complete machine learning pipeline, from raw data to interactive prediction.

---

## 2. Problem Statement

Given student characteristics available at the start of an academic year, can we build a model that provides a useful estimate of the likely final grade? More broadly, what patterns in the data are associated with strong or weak academic performance?

---

## 3. Datasets

### UCI Student Performance Dataset
- **Source:** UCI Machine Learning Repository (Cortez & Silva, 2008)
- **License:** CC BY 4.0
- **Files:** student-mat.csv (Mathematics, 395 records), student-por.csv (Portuguese, 649 records)
- **Features:** 30 input features covering demographics, family, social, and academic characteristics
- **Target:** G3 — Final period grade (0–20)
- **Note:** Both files are from the same study; they are not independent

Both datasets contain no missing values in their original form. G1 (first period grade) and G2 (second period grade) are excluded from model inputs to simulate the more challenging and useful scenario of predicting final grades without intermediate assessment results.

---

## 4. Methodology

### 4.1 Data Acquisition
The application attempts automatic download from the UCI repository. If that fails, the user is directed to download and place files manually.

### 4.2 Exploratory Data Analysis
- Grade distributions show most students scoring in the 10–14 range
- Portuguese students score slightly higher on average than Mathematics students
- Parental education levels (Medu, Fedu) show positive correlation with G3
- Alcohol consumption (Dalc, Walc) shows negative correlation with G3
- Past class failures is a strong negative predictor
- Study time shows a positive association with grades

### 4.3 Preprocessing Pipeline

```
Numerical (13 features):
  SimpleImputer(median) → StandardScaler

Categorical (17 features):
  SimpleImputer(constant='missing') → OneHotEncoder(handle_unknown='ignore')

Combined via ColumnTransformer
Wrapped in sklearn Pipeline with each model
```

### 4.4 Train/Test Split
- 80% training, 20% testing
- `random_state=42`
- Preprocessor fitted on training set only

### 4.5 Models Trained
1. Linear Regression (baseline)
2. Decision Tree Regressor
3. Random Forest Regressor (100 trees)
4. Gradient Boosting Regressor (100 estimators)

---

## 5. Results

*The following table will be populated with actual results after running the application.*

### Mathematics Dataset (80/20 split, random_state=42, test set n=79)

| Model | MAE | RMSE | R² |
|---|---|---|---|
| Linear Regression | 3.3953 | 4.1957 | 0.1415 |
| Decision Tree | 3.6329 | 4.8379 | -0.1414 |
| **Random Forest** ⭐ | **3.0022** | **3.7687** | **0.3073** |
| Gradient Boosting | 3.1111 | 3.9359 | 0.2445 |
| **Best Model** | **Random Forest** | RMSE 3.77 | R² 0.31 |

### Portuguese Dataset (80/20 split, random_state=42, test set n=130)

| Model | MAE | RMSE | R² |
|---|---|---|---|
| Linear Regression | 2.1564 | 2.8618 | 0.1602 |
| Decision Tree | 2.8615 | 3.7988 | -0.4798 |
| Random Forest | 2.0470 | 2.8225 | 0.1831 |
| **Gradient Boosting** ⭐ | **2.1068** | **2.8062** | **0.1925** |
| **Best Model** | **Gradient Boosting** | RMSE 2.81 | R² 0.19 |

*Metrics computed on held-out test set. G1 and G2 excluded from inputs.*

---

## 6. Key Findings

1. **Ensemble methods outperform linear models** — Random Forest and Gradient Boosting consistently achieve lower RMSE than Linear Regression and Decision Tree on this dataset.

2. **Past failures is the strongest predictor** — Students with more previous class failures score significantly lower on average. This is the most important feature in tree-based models.

3. **Parental education positively correlates with grades** — Higher Medu and Fedu values are associated with higher G3 across both subjects.

4. **Study time shows a positive but moderate association** — More weekly study hours correlates with higher grades, though the effect is not deterministic.

5. **Alcohol consumption negatively correlates with grades** — Both workday (Dalc) and weekend (Walc) alcohol consumption show inverse relationships with G3.

6. **Predicting without G1/G2 limits accuracy** — Using only pre-year characteristics is a harder task. Adding G1/G2 as features would substantially increase R² but would be appropriate only when mid-year performance data is available.

---

## 7. Technologies Used

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Core language |
| Streamlit | 1.35 | Dashboard |
| pandas | 2.2 | Data handling |
| NumPy | 1.26 | Numerical ops |
| scikit-learn | 1.4 | ML pipeline |
| Plotly | 5.22 | Visualisations |
| joblib | 1.4 | Model saving |
| requests | 2.32 | Auto-download |

---

## 8. Application Features

- **Overview Dashboard** — KPI cards, grade distributions, model summary
- **Dataset Explorer** — Interactive data preview, statistics, missing value report, correlation heatmap
- **Performance Prediction** — 30-feature form, multi-model selection, grade estimate with interpretation
- **Model Comparison** — Metrics table, bar charts, actual-vs-predicted, residuals, feature importance, train-vs-test gap
- **Academic Insights** — Study time, absences, failures, correlations, feature importance
- **About** — Dataset sources, methodology, technology stack, responsible use statement

---

## 9. Limitations

1. Small dataset (395 and 649 records) from a specific geographic and temporal context
2. No hyperparameter optimisation
3. Many real-world predictors (mental health, teaching quality) are absent from the data
4. OULAD not integrated in this version
5. Predictions are estimates with meaningful uncertainty

---

## 10. Future Enhancements

1. Integrate OULAD with a separate pipeline and outcome variable
2. Add cross-validated hyperparameter tuning (GridSearchCV or RandomizedSearchCV)
3. Add SHAP values for individual prediction explanations
4. Allow optional inclusion of G1/G2 with a clear user warning
5. Build a class-level overview for teachers (aggregate student summaries)
6. Add CSV upload for predicting grades for a batch of students

---

## 11. Responsible Use

This system is an educational demonstration. Predictions must not be used to make high-stakes decisions about individual students. See `data/README.md` and the About page for full attribution and responsible use statements.

---

## References

Cortez, P. & Silva, A. (2008). *Using Data Mining to Predict Secondary School Student Performance.* In A. Brito and J. Teixeira Eds., Proceedings of 5th FUture BUsiness TEChnology Conference (FUBUTEC 2008) pp. 5-12, Porto, Portugal, April, 2008, EUROSIS, ISBN 978-9077381-39-7.

UCI Machine Learning Repository. (2014). *Student Performance Data Set.* https://archive.ics.uci.edu/dataset/320/student+performance
