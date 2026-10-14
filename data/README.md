# Dataset Directory

## UCI Student Performance Dataset (MANDATORY)

**Source:** https://archive.ics.uci.edu/dataset/320/student+performance  
**License:** Creative Commons Attribution 4.0 International (CC BY 4.0)  
**Citation:** P. Cortez and A. Silva. Using Data Mining to Predict Secondary School Student Performance. In A. Brito and J. Teixeira Eds., Proceedings of 5th FUture BUsiness TEChnology Conference (FUBUTEC 2008) pp. 5-12, Porto, Portugal, April, 2008, EUROSIS, ISBN 978-9077381-39-7.

### Files Required
Place these files in this directory:
- `student-mat.csv` — Mathematics students (395 records)
- `student-por.csv` — Portuguese language students (649 records)

Both files use **semicolons (;)** as delimiters.

### How to Download

**Option 1 — Automatic (the app will attempt this on first run)**

**Option 2 — Manual:**
1. Visit https://archive.ics.uci.edu/dataset/320/student+performance
2. Click "Download" to get the ZIP file
3. Extract `student.zip` inside the ZIP
4. Extract `student.zip` → you will find `student-mat.csv` and `student-por.csv`
5. Place both files in this `data/` folder

### Target Variable
- `G3` — Final period grade (0–20 scale)
- G1 and G2 (first and second period grades) are **excluded** from input features by default to avoid data leakage

---

## OULAD (Optional — Future Extension)

**Source:** https://analyse.kmi.open.ac.uk/open_dataset  
This dataset is large (~200MB+) and requires separate integration.  
It is documented as a future enhancement.
