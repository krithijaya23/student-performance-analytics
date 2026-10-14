# Viva Questions & Answers

## Dataset & Problem

**Q1. What dataset did you use and where did you get it?**
The UCI Student Performance Dataset from the UCI Machine Learning Repository (https://archive.ics.uci.edu/dataset/320/student+performance). Collected by Cortez & Silva (2008) from two Portuguese secondary schools. Two CSV files: student-mat.csv (395 Mathematics students) and student-por.csv (649 Portuguese language students) — both from the same study.

**Q2. What is the target variable?**
G3 — the final period grade on a 0–20 scale.

**Q3. Why did you exclude G1 and G2 from the inputs?**
G1 and G2 are first and second period grades. Including them would make the model trivially accurate since earlier grades are strongly correlated with the final grade. Excluding them creates the more realistic and useful task of estimating final performance from characteristics available at the start of the year.

**Q4. Are the Mathematics and Portuguese files two independent studies?**
No. Both files come from the same study (Cortez & Silva, 2008) covering the same two Portuguese schools. They differ only in subject.

---

## Data Preprocessing

**Q5. What preprocessing did you apply?**
A scikit-learn ColumnTransformer pipeline: (1) numerical features — median imputation then StandardScaler; (2) categorical features — constant imputation with "missing" then OneHotEncoder with handle_unknown="ignore". The preprocessor is fit only on the training set.

**Q6. Why median imputation for numerical features?**
Median is more robust to outliers than mean. Features like absences can have extreme values that would distort mean-based imputation.

**Q7. What does handle_unknown="ignore" do in OneHotEncoder?**
If a categorical value appears at prediction time that wasn't in the training data, it is encoded as all zeros rather than raising an error — making the model more robust to new inputs.

**Q8. Why fit the preprocessor only on training data?**
To prevent data leakage. Fitting on the full dataset before splitting would allow test set information to influence preprocessing, producing an optimistic and unrealistic performance estimate.

---

## Machine Learning

**Q9. What models did you compare?**
Linear Regression, Decision Tree Regressor, Random Forest Regressor (100 trees), and Gradient Boosting Regressor (100 estimators) — all from scikit-learn.

**Q10. What is the difference between Decision Tree and Random Forest?**
A Decision Tree makes a single recursive set of splits. A Random Forest trains hundreds of trees on random subsets of data and features, then averages predictions. This averaging reduces variance and overfitting.

**Q11. How does Gradient Boosting differ from Random Forest?**
Random Forest builds trees independently in parallel. Gradient Boosting builds trees sequentially — each tree corrects the errors of the previous one. Boosting typically achieves lower bias but can overfit more if not tuned.

**Q12. What train/test split did you use?**
80% training, 20% testing, with random_state=42 for reproducibility.

---

## Evaluation

**Q13. What metrics did you use?**
MAE, RMSE, and R² — all computed on the held-out test set only.

**Q14. What does RMSE measure vs MAE?**
Both measure average prediction error. RMSE squares errors before averaging, penalising large mistakes more heavily. MAE treats all errors equally.

**Q15. What does R² mean in this project?**
The proportion of variance in final grades that the model explains. R² values of 0.19–0.31 without G1/G2 are expected — demographic features alone are moderate predictors.

**Q16. How did you select the best model?**
By the lowest test-set RMSE. RMSE was preferred because penalising large grade-prediction errors more strongly is appropriate in education.

---

## Actual Results (Mathematics, test n=79)

| Model | MAE | RMSE | R² |
|---|---|---|---|
| Linear Regression | 3.3953 | 4.1957 | 0.1415 |
| Decision Tree | 3.6329 | 4.8379 | -0.1414 |
| **Random Forest** ⭐ | **3.0022** | **3.7687** | **0.3073** |
| Gradient Boosting | 3.1111 | 3.9359 | 0.2445 |

## Actual Results (Portuguese, test n=130)

| Model | MAE | RMSE | R² |
|---|---|---|---|
| Linear Regression | 2.1564 | 2.8618 | 0.1602 |
| Decision Tree | 2.8615 | 3.7988 | -0.4798 |
| Random Forest | 2.0470 | 2.8225 | 0.1831 |
| **Gradient Boosting** ⭐ | **2.1068** | **2.8062** | **0.1925** |

---

## Application Design

**Q17. Why Streamlit?**
Streamlit allows rapid development of interactive data dashboards in pure Python, with no web development expertise required. It runs locally, is easy to demo, and supports all required chart types via Plotly.

**Q18. How does the prediction form work?**
The user fills in 30 student characteristics. These are assembled into a single-row DataFrame and passed through the same sklearn Pipeline used for training — applying identical preprocessing before the model predicts.

**Q19. What caching did you use?**
@st.cache_data for dataset loading and @st.cache_resource for model training. This means expensive operations run only once per session, not every time the user navigates between pages.

---

## Limitations & Ethics

**Q20. What are the main limitations?**
Small dataset (395/649 records) from specific Portuguese schools in 2005–2006; many real predictors (mental health, teaching quality) are absent; no hyperparameter tuning; predicting without G1/G2 limits accuracy; not validated for real-world deployment.

**Q21. Can this system be used to make real decisions about students?**
No. The application includes a responsible use disclaimer on every prediction. It is an educational demonstration only.

**Q22. What would you add with more time?**
OULAD integration, cross-validated hyperparameter tuning, SHAP explanations for individual predictions, optional G1/G2 toggle with clear warnings, batch prediction via CSV upload, and a class-level teacher dashboard.
