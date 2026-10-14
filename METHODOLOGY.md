# Methodology

## Complete Workflow

```
1. Data Acquisition
       ↓
2. Data Validation
       ↓
3. Exploratory Data Analysis
       ↓
4. Feature Engineering & Preprocessing
       ↓
5. Train/Test Split (80/20)
       ↓
6. Model Training (training set only)
       ↓
7. Model Evaluation (test set only)
       ↓
8. Best Model Selection
       ↓
9. Interactive Prediction
       ↓
10. Visualisation & Interpretation
```

---

## Step-by-Step Explanation

### 1. Data Acquisition
- The application attempts to download `student-mat.csv` and `student-por.csv` from the UCI repository on first run.
- If the download fails, the user is shown clear instructions for manual download.
- Files are stored in `data/` and cached for offline use.

### 2. Data Validation
- Confirm the CSV uses semicolon (`;`) delimiters.
- Confirm the target column `G3` is present.
- Check minimum row count.
- Report any missing values.

### 3. Exploratory Data Analysis
- Grade distributions (histograms, violin plots)
- Correlation heatmaps (G1, G2 excluded to focus on non-grade features)
- Categorical breakdowns (grade by school, sex, address, etc.)
- Study time and absence patterns

### 4. Feature Engineering & Preprocessing

**Input features (30 total, G1/G2/G3 excluded):**

| Category | Columns |
|---|---|
| Numerical (13) | age, Medu, Fedu, traveltime, studytime, failures, famrel, freetime, goout, Dalc, Walc, health, absences |
| Categorical (17) | school, sex, address, famsize, Pstatus, Mjob, Fjob, reason, guardian, schoolsup, famsup, paid, activities, nursery, higher, internet, romantic |

**Numeric pipeline:**
1. `SimpleImputer(strategy="median")` — fill missing with column median
2. `StandardScaler()` — zero mean, unit variance

**Categorical pipeline:**
1. `SimpleImputer(strategy="constant", fill_value="missing")` — fill missing with literal "missing"
2. `OneHotEncoder(handle_unknown="ignore")` — encode categories; unseen categories at prediction time are silently ignored

**Combined using `ColumnTransformer`** — all transformations are fit only on the training set and applied to both train and test.

### 5. Train/Test Split
- `train_test_split(test_size=0.20, random_state=42)`
- Stratification is not applied (regression task)
- **Important:** The preprocessor is fit only on `X_train`, then applied to both `X_train` and `X_test` to prevent data leakage.

### 6. Model Training
Each model is wrapped in a `Pipeline` with the preprocessor:

```
Pipeline([
    ("preprocessor", ColumnTransformer(...)),
    ("model", <regressor>)
])
```

Models:
1. `LinearRegression()` — ordinary least squares baseline
2. `DecisionTreeRegressor(random_state=42)` — single decision tree
3. `RandomForestRegressor(n_estimators=100, random_state=42)` — bagged ensemble
4. `GradientBoostingRegressor(n_estimators=100, random_state=42)` — boosted ensemble

### 7. Evaluation
Metrics computed on the **held-out test set only**:

| Metric | Formula | Interpretation |
|---|---|---|
| MAE | mean(|y_true − y_pred|) | Average absolute error in grade points |
| RMSE | sqrt(mean((y_true − y_pred)²)) | Penalises large errors more than MAE |
| R² | 1 − SS_res/SS_tot | Proportion of variance explained (0–1) |

Training metrics are also computed and displayed to check for overfitting.

### 8. Best Model Selection
The model with the **lowest test-set RMSE** is selected as the best model.  
All four metrics (MAE, RMSE, R², train time) are displayed for transparency.

### 9. Interactive Prediction
- User fills in the 30 feature values via a form.
- Values are assembled into a single-row DataFrame.
- The same fitted pipeline applies preprocessing and produces a predicted G3.
- Output is clipped to [0, 20].
- A grade band and interpretation are displayed.
- A disclaimer is shown on every prediction.

### 10. Visualisation
- All charts use real calculated values — no hardcoded metrics.
- Plotly provides interactive zoom, hover, and export.
- Charts include: grade histograms, box plots, correlation heatmaps, actual-vs-predicted scatter, residual plots, feature importance bar charts.

---

## Design Decisions

**Why exclude G1 and G2?**
Including first and second period grades as input features would produce a much higher R² because those grades are highly correlated with G3. However, the more useful and challenging task is estimating the final grade from student characteristics available at the start of the year.

**Why use RMSE as the selection criterion?**
RMSE penalises large errors more than MAE, making it appropriate for academic grade prediction where large mistakes are particularly costly. All three metrics are shown for transparency.

**Why not tune hyperparameters?**
Hyperparameter tuning using cross-validation on the training set would be a valid extension but adds complexity. The default parameters of these well-established models are reasonable for a dataset of this size.

**Why not use classification?**
The target variable G3 is a continuous 0–20 scale, making regression the appropriate approach. Converting to pass/fail would lose information and introduce an arbitrary threshold.
