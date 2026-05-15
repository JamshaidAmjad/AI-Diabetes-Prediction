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
2. **Random Forest** — ensemble with GridSearchCV hyperparameter tuning
3. **MLP (Neural Network)** — feed-forward network with early stopping and LR scheduling

## Results (Test Set — 15% held-out)

| Model | Accuracy | F1 Score | ROC-AUC |
|---|---|---|---|
| Logistic Regression | 0.776 | 0.683 | 0.866 |
| Random Forest | 0.767 | 0.649 | 0.841 |
| MLP | 0.767 | 0.667 | 0.875 |

Cross-validation F1 (5-fold on train+val):

| Model | CV F1 Mean | CV F1 Std |
|---|---|---|
| Logistic Regression | 0.718 | ±0.029 |
| Random Forest | 0.801 | ±0.042 |

Best RF hyperparameters (GridSearchCV): `max_depth=10, min_samples_leaf=1, min_samples_split=2, n_estimators=100`

Selected features (top-5 by ANOVA F-test + RF importance rank): **Glucose, BMI, Insulin, Age, Pregnancies**

## Repository Structure
```text
project-root/
|
|-- data/
|   |-- raw/
|   |   `-- diabetes.csv              ← source dataset
|   `-- processed/                    ← imputed, scaled, SMOTE-balanced splits (.npy)
|
|-- notebooks/
|   `-- eda.ipynb                     ← exploratory data analysis (7 sections)
|
|-- src/
|   |-- data/
|   |   `-- dataset.py                ← preprocessing pipeline (impute, scale, select, SMOTE)
|   |-- models/
|   |   `-- model.py                  ← LR, RF, and MLP definitions
|   |-- training/
|   |   `-- train.py                  ← training + CV + hyperparameter tuning entry point
|   |-- evaluation/
|   |   `-- evaluate.py               ← metrics, confusion matrices, ROC curves, JSON report
|   `-- utils/
|       `-- __init__.py               ← set_seed, plot_training_history, save_metrics
|
|-- outputs/
|   |-- models/                       ← logistic_regression.pkl, random_forest.pkl, mlp_best.pt
|   |-- figures/                      ← confusion matrices, ROC curves, model comparison,
|   |                                    training curves, feature importance, EDA plots
|   `-- reports/                      ← evaluation_results.json, cv_results.json
|
|-- config/
|   `-- config.yaml                   ← centralized configuration
|
|-- scripts/
|   |-- preprocess.py                 ← standalone preprocessing + EDA figures script
|   `-- run_pipeline.sh               ← end-to-end: train → evaluate → test
|
|-- tests/
|   |-- test_dataset.py               ← 6 tests for preprocessing pipeline
|   |-- test_models.py                ← 6 tests for model definitions
|   `-- test_evaluation.py            ← 5 tests for evaluation metrics
|
|-- README.md
|-- requirements.txt
`-- .gitignore
```

## Quick Start

**Option A — One command (recommended):**
```bash
pip install -r requirements.txt
bash scripts/run_pipeline.sh
```

**Option B — Step by step:**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train all models (includes CV + GridSearch for RF)
python -m src.training.train

# 3. Evaluate on held-out test set (generates all plots + JSON reports)
python -m src.evaluation.evaluate

# 4. Run test suite
pytest tests/ -v
```

## Data Pipeline
The preprocessing pipeline (`src/data/dataset.py`) applies these steps in order — all transformers fitted **only on training data** to prevent leakage:

1. Replace biologically impossible zeros with `NaN` (Glucose, BMI, Insulin, BloodPressure, SkinThickness)
2. Stratified 70 / 15 / 15 train-val-test split
3. Median imputation of missing values
4. StandardScaler normalization
5. Feature selection: top-5 features by averaged ANOVA F-test + Random Forest importance rank
6. SMOTE oversampling to address class imbalance (training set only)

## Training & Evaluation Features
- **Cross-validation**: 5-fold CV on combined train+val set for LR and RF
- **Hyperparameter tuning**: `GridSearchCV` over `n_estimators`, `max_depth`, `min_samples_split`, `min_samples_leaf` for Random Forest
- **Early stopping**: MLP training stops when val loss stops improving (patience=10)
- **Output plots**: confusion matrices per model, ROC curve comparison, grouped metric bar chart, feature importance, MLP training curves
- **Reports**: `evaluation_results.json` (test metrics), `cv_results.json` (CV fold scores)

## Tests
17 unit tests covering the full pipeline:
```bash
pytest tests/ -v   # all 17 pass
```
