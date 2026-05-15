# AI Diabetes Prediction

## Project Overview
A Master's-level **AI in Healthcare** project building a medical decision support system for early diabetes prediction using the Pima Indians Diabetes dataset.

## Problem Statement
Predict whether a patient has diabetes based on tabular clinical features:

| Feature | Description |
|---|---|
| Pregnancies | Number of pregnancies |
| Glucose | Plasma glucose concentration |
| BloodPressure | Diastolic blood pressure (mm Hg) |
| SkinThickness | Triceps skin fold thickness (mm) |
| Insulin | 2-hour serum insulin (mu U/ml) |
| BMI | Body mass index |
| DiabetesPedigreeFunction | Diabetes pedigree function |
| Age | Age in years |
| **Outcome** | **Target: 1 = Diabetes, 0 = No Diabetes** |

## Modeling Approach
Three complementary models are trained and compared:
1. **Logistic Regression** — interpretable linear baseline
2. **Random Forest** — ensemble, non-linear, handles feature interactions
3. **MLP (Neural Network)** — small feed-forward network with early stopping

## Repository Structure
```text
project-root/
|
|-- data/
|   |-- raw/
|   |   `-- diabetes.csv        ← source dataset
|   `-- processed/              ← imputed, scaled, SMOTE-balanced splits (.npy)
|
|-- notebooks/
|   `-- eda.ipynb               ← exploratory data analysis
|
|-- src/
|   |-- data/
|   |   `-- dataset.py          ← preprocessing pipeline (impute, scale, select, SMOTE)
|   |-- models/
|   |   `-- model.py            ← LR, RF, and MLP definitions
|   |-- training/
|   |   `-- train.py            ← training entry point for all models
|   |-- evaluation/
|   |   `-- evaluate.py         ← metrics, confusion matrices, JSON report
|   `-- utils/
|       `-- __init__.py         ← set_seed, plot_training_history, save_metrics
|
|-- outputs/
|   |-- models/                 ← saved model files (.pkl / .pt)
|   |-- figures/                ← confusion matrices, training curves, EDA plots
|   `-- reports/                ← evaluation_results.json
|
|-- config/
|   `-- config.yaml             ← centralized configuration
|
|-- tests/
|   |-- test_dataset.py
|   |-- test_models.py
|   `-- test_evaluation.py
|
|-- README.md
|-- requirements.txt
`-- .gitignore
```

## Quick Start
1. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Place `diabetes.csv` in `data/raw/` (already committed).
4. Train all models:
   ```bash
   python -m src.training.train
   ```
5. Evaluate on the held-out test set:
   ```bash
   python -m src.evaluation.evaluate
   ```
6. Run tests:
   ```bash
   pytest tests/
   ```

## Data Pipeline
The preprocessing pipeline (`src/data/dataset.py`) applies these steps in order — all fitted **only on training data** to prevent leakage:

1. Replace biologically impossible zeros with `NaN` (Glucose, BMI, Insulin, etc.)
2. Stratified 70 / 15 / 15 train-val-test split
3. Median imputation of missing values
4. StandardScaler normalization
5. Feature selection: top-5 features by averaged ANOVA F-test + Random Forest rank
6. SMOTE oversampling to address class imbalance (training set only)

## Team Notes
Keep changes modular. Each module (`dataset`, `model`, `train`, `evaluate`) is independently runnable. Configuration lives in `config/config.yaml`.
