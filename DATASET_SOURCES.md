# Dataset Sources & Attribution

## 1. UCI Student Performance Dataset

| Field | Details |
|---|---|
| **Name** | Student Performance |
| **Source** | UCI Machine Learning Repository |
| **URL** | https://archive.ics.uci.edu/dataset/320/student+performance |
| **Original Study** | Cortez, P. & Silva, A. (2008). *Using Data Mining to Predict Secondary School Student Performance.* In A. Brito and J. Teixeira Eds., Proceedings of 5th FUture BUsiness TEChnology Conference (FUBUTEC 2008) pp. 5-12, Porto, Portugal, April, 2008, EUROSIS, ISBN 978-9077381-39-7. |
| **License** | Creative Commons Attribution 4.0 International (CC BY 4.0) |
| **Files** | student-mat.csv (Mathematics), student-por.csv (Portuguese) |
| **Delimiter** | Semicolon (;) |
| **Records** | 395 (Math), 649 (Portuguese) |
| **Features** | 33 columns (30 input features + G1, G2, G3) |
| **Target** | G3 — Final period grade (0–20 scale) |
| **Collection period** | 2005–2006 academic year |
| **Schools** | Gabriel Pereira (GP) and Mousinho da Silveira (MS), Alentejo, Portugal |

### Features Description

| Column | Type | Description |
|---|---|---|
| school | Categorical | Student's school (GP or MS) |
| sex | Categorical | Student's sex (F/M) |
| age | Numerical | Student's age (15–22) |
| address | Categorical | Home address (U=Urban, R=Rural) |
| famsize | Categorical | Family size (LE3≤3, GT3>3) |
| Pstatus | Categorical | Parents' cohabitation (T=Together, A=Apart) |
| Medu | Numerical | Mother's education (0–4) |
| Fedu | Numerical | Father's education (0–4) |
| Mjob | Categorical | Mother's job |
| Fjob | Categorical | Father's job |
| reason | Categorical | Reason for choosing school |
| guardian | Categorical | Student's guardian |
| traveltime | Numerical | Home to school travel time (1–4) |
| studytime | Numerical | Weekly study time (1–4) |
| failures | Numerical | Past class failures (0–4) |
| schoolsup | Categorical | Extra educational support from school |
| famsup | Categorical | Family educational support |
| paid | Categorical | Extra paid classes |
| activities | Categorical | Extracurricular activities |
| nursery | Categorical | Attended nursery school |
| higher | Categorical | Wants higher education |
| internet | Categorical | Internet access at home |
| romantic | Categorical | In a romantic relationship |
| famrel | Numerical | Family relationship quality (1–5) |
| freetime | Numerical | Free time after school (1–5) |
| goout | Numerical | Going out with friends (1–5) |
| Dalc | Numerical | Workday alcohol consumption (1–5) |
| Walc | Numerical | Weekend alcohol consumption (1–5) |
| health | Numerical | Health status (1–5) |
| absences | Numerical | Number of school absences |
| G1 | Numerical | First period grade (0–20) — **excluded from inputs** |
| G2 | Numerical | Second period grade (0–20) — **excluded from inputs** |
| G3 | Numerical | Final period grade (0–20) — **target variable** |

### Limitations

- Covers only two Portuguese schools in one academic year
- Sample size is relatively small (395 and 649 records)
- No guarantee of representativeness beyond this context
- Collected ~2005–2006; social and educational contexts may have changed

---

## 2. OULAD — Open University Learning Analytics Dataset (Future Extension)

| Field | Details |
|---|---|
| **Name** | Open University Learning Analytics Dataset |
| **Source** | Knowledge Media Institute, Open University UK |
| **URL** | https://analyse.kmi.open.ac.uk/open_dataset |
| **License** | CC BY 4.0 |
| **Records** | ~22,000 students across multiple modules |
| **Status** | **Documented as future extension — not integrated in this version** |

OULAD requires a separate integration pipeline due to its multi-table structure and different outcome variable. It would require defining a separate prediction task (e.g., final result: Pass/Fail/Distinction/Withdrawn) incompatible with the UCI 0–20 scale.
