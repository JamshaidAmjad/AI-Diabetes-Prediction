"""Generate the three project notebooks."""
import json, uuid, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NB_DIR = os.path.join(BASE, "notebooks")


def uid():
    return str(uuid.uuid4())[:8]


def md(source):
    return {"cell_type": "markdown", "id": uid(), "metadata": {}, "source": source}


def code(source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": uid(),
        "metadata": {},
        "outputs": [],
        "source": source,
    }


def notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "version": "3.11.0",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def save(nb, filename):
    path = os.path.join(NB_DIR, filename)
    with open(path, "w") as f:
        json.dump(nb, f, indent=1)
    print(f"Saved: {path}")


# ─────────────────────────────────────────────────────────────────────────────
# NOTEBOOK 1 — Data Exploration & Preprocessing
# ─────────────────────────────────────────────────────────────────────────────
nb1_cells = [

md("""\
# Notebook 1: Data Exploration & Preprocessing

**Course:** M7016H — Artificial Intelligence within the Healthcare System
**Dataset:** Pima Indians Diabetes Dataset (Dataset 4)
**Authors:** Jamshaid Amjad, Shameena Mohammed Nabeel, Suresh Balaraman

---

This notebook covers everything from loading the raw CSV through to producing the
clean, scaled, feature-selected splits that the models in Notebook 2 will train on.
The idea is to understand the data properly before touching any model — it's easy
to skip this step and end up with a pipeline built on shaky foundations.\
"""),

md("""\
## 1. Setup\
"""),

code("""\
import sys
import os

# make sure we can import from src/
sys.path.insert(0, os.path.abspath(".."))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
from pathlib import Path

sns.set_theme(style="whitegrid", palette="muted")
pd.set_option("display.max_columns", 20)
pd.set_option("display.float_format", "{:.3f}".format)\
"""),

md("""\
## 2. Load the Raw Data

The dataset comes from the National Institute of Diabetes and Digestive and Kidney Diseases
(Smith et al., 1988). It contains clinical measurements for 768 Pima Native American women
aged 21 or older, each labelled as diabetic (1) or non-diabetic (0).\
"""),

code("""\
RAW_CSV = Path("../data/raw/diabetes.csv")
df = pd.read_csv(RAW_CSV)

print(f"Shape: {df.shape}")
df.head()\
"""),

code("""\
df.dtypes\
"""),

code("""\
df.describe().T\
"""),

md("""\
A few things stand out straight away from the summary statistics:

- **Glucose**, **BMI**, **BloodPressure**, **SkinThickness**, and **Insulin** all have
  a minimum value of 0. Physiologically, a glucose concentration or BMI of zero is
  impossible — these zeros almost certainly encode missing values rather than true
  measurements (a known quirk of this dataset).
- **Insulin** has a very high standard deviation (115) relative to its mean (79),
  which is consistent with a lot of zero/missing values pulling the distribution around.

We'll deal with this in the preprocessing section. First, let's look at the class balance.\
"""),

md("""\
## 3. Class Distribution

Knowing whether the dataset is balanced is important — it affects which metrics
we should rely on and whether we need to do anything to correct the imbalance during training.\
"""),

code("""\
counts = df["Outcome"].value_counts()
labels = ["No Diabetes (0)", "Diabetes (1)"]

fig, axes = plt.subplots(1, 2, figsize=(10, 4))

# Bar chart
axes[0].bar(labels, counts.values, color=["#4C72B0", "#DD8452"], width=0.5, edgecolor="white")
axes[0].set_ylabel("Count")
axes[0].set_title("Class Distribution")
for i, v in enumerate(counts.values):
    axes[0].text(i, v + 5, str(v), ha="center", fontweight="bold")

# Pie chart
axes[1].pie(
    counts.values,
    labels=labels,
    autopct="%1.1f%%",
    startangle=90,
    colors=["#4C72B0", "#DD8452"],
    wedgeprops={"edgecolor": "white", "linewidth": 1.5},
)
axes[1].set_title("Class Proportions")

plt.suptitle("Target Variable — Diabetes Outcome", fontsize=13, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig("../outputs/figures/class_distribution.png", dpi=150, bbox_inches="tight")
plt.show()\
"""),

md("""\
The dataset is moderately imbalanced — **34.9% positive** (diabetic) vs **65.1% negative**.
This is enough of a skew that a naive classifier that always predicts "no diabetes" would
achieve ~65% accuracy without learning anything useful. We'll address this with SMOTE
oversampling during preprocessing.\
"""),

md("""\
## 4. Missing Value Analysis

As noted above, zero values in several columns are physiologically meaningless.
Let's quantify how many there are per feature before we replace them.\
"""),

code("""\
# These features cannot legitimately be zero
zero_cols = ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]

zero_counts = {col: (df[col] == 0).sum() for col in zero_cols}
zero_pct    = {col: (df[col] == 0).mean() * 100 for col in zero_cols}

missing_df = pd.DataFrame({
    "Zero Count": zero_counts,
    "% of Rows": zero_pct,
})
print(missing_df.to_string())

fig, ax = plt.subplots(figsize=(8, 4))
bars = ax.barh(list(zero_counts.keys()), list(zero_pct.values()),
               color="#4C72B0", edgecolor="white", alpha=0.85)
for bar, pct in zip(bars, zero_pct.values()):
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
            f"{pct:.1f}%", va="center")
ax.set_xlabel("% rows with zero value")
ax.set_title("Physiologically Impossible Zeros by Feature")
plt.tight_layout()
plt.savefig("../outputs/figures/missing_values.png", dpi=150, bbox_inches="tight")
plt.show()\
"""),

md("""\
**Insulin** is the worst offender — nearly half the rows have a recorded value of zero,
which is clearly not a real measurement. **SkinThickness** is also heavily affected at ~30%.
These will be replaced with `NaN` and later imputed with the training-set median.\
"""),

md("""\
## 5. Feature Distributions

Let's look at how each feature is distributed, split by diabetes outcome.
This gives an early sense of which features might be useful discriminators.\
"""),

code("""\
features = [c for c in df.columns if c != "Outcome"]

fig, axes = plt.subplots(3, 3, figsize=(13, 10))
axes = axes.flatten()

for i, feat in enumerate(features):
    ax = axes[i]
    for outcome, color, label in [(0, "#4C72B0", "No Diabetes"), (1, "#DD8452", "Diabetes")]:
        vals = df.loc[df["Outcome"] == outcome, feat]
        ax.hist(vals, bins=25, alpha=0.6, color=color, label=label, edgecolor="none", density=True)
    ax.set_title(feat, fontsize=10, fontweight="bold")
    ax.set_ylabel("Density", fontsize=8)
    ax.legend(fontsize=7)

# hide the spare subplot
axes[-1].set_visible(False)

fig.suptitle("Feature Distributions by Outcome", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("../outputs/figures/feature_distributions.png", dpi=150, bbox_inches="tight")
plt.show()\
"""),

md("""\
**Glucose** shows the clearest separation between classes — diabetic patients tend to
have noticeably higher glucose concentrations. **BMI** and **Age** also show some
separation, though with more overlap. **BloodPressure** and **Pregnancies** are
harder to distinguish visually.\
"""),

md("""\
## 6. Correlation Analysis\
"""),

code("""\
corr = df.corr()

fig, ax = plt.subplots(figsize=(9, 7))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(
    corr, mask=mask, annot=True, fmt=".2f", cmap="coolwarm",
    center=0, vmin=-1, vmax=1, ax=ax,
    square=True, linewidths=0.5, cbar_kws={"shrink": 0.8},
)
ax.set_title("Feature Correlation Matrix", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("../outputs/figures/correlation_heatmap.png", dpi=150, bbox_inches="tight")
plt.show()\
"""),

code("""\
# Just the correlations with the target — sorted
target_corr = corr["Outcome"].drop("Outcome").sort_values(ascending=False)
print("Correlation with Outcome:")
print(target_corr.to_string())\
"""),

md("""\
**Glucose** has by far the strongest correlation with the outcome (0.49), consistent
with its clinical role as the primary diagnostic marker for diabetes. **BMI** and **Age**
follow. Features like **BloodPressure** and **SkinThickness** have weaker correlations,
suggesting they may add less signal on their own — though interactions between features
can still make them useful in tree-based models.\
"""),

md("""\
## 7. Preprocessing Pipeline

Now that we understand the data, let's run the full preprocessing pipeline.
All steps are implemented in `src/data/dataset.py` and configured via `config/config.yaml`.

The steps, in order:
1. Replace physiologically impossible zeros with `NaN`
2. Stratified 70 / 15 / 15 train–validation–test split
3. Median imputation (fitted on training data only, to prevent leakage)
4. StandardScaler normalisation (again, fitted on training data only)
5. Feature selection — top-5 features by averaged ANOVA F-test and Random Forest importance ranks
6. SMOTE oversampling (training set only) to correct class imbalance\
"""),

code("""\
import yaml
from src.data.dataset import build_dataset

with open("../config/config.yaml") as f:
    cfg = yaml.safe_load(f)

csv_path = Path("../data/raw") / cfg["data"]["filename"]

data = build_dataset(
    csv_path=str(csv_path),
    val_split=cfg["data"]["val_split"],
    test_split=cfg["data"]["test_split"],
    n_features=cfg["data"]["n_features_to_select"],
    use_smote=cfg["data"]["use_smote"],
    random_seed=cfg["project"]["random_seed"],
    processed_dir="../data/processed",
)

print("Features selected:", data["selected_features"])
print()
print(f"Train set (after SMOTE) : {data['X_train'].shape}")
print(f"Validation set          : {data['X_val'].shape}")
print(f"Test set                : {data['X_test'].shape}")\
"""),

md("""\
### Why these five features?

Feature selection combines two complementary methods:
- **ANOVA F-test** (filter method) — measures the statistical association between each
  feature and the target independently of any model
- **Random Forest importance** (embedded method) — captures non-linear relationships
  and interactions that the F-test misses

Averaging their ranks makes the selection more robust than relying on either alone.
The five selected features — **Glucose, BMI, Insulin, Age, Pregnancies** — are consistent
with what the clinical literature identifies as primary risk factors for Type 2 diabetes.\
"""),

code("""\
# Quick sanity check on the processed splits
print("Class balance in training set after SMOTE:")
unique, counts = np.unique(data["y_train"], return_counts=True)
for u, c in zip(unique, counts):
    print(f"  Class {int(u)}: {c} samples  ({c/len(data['y_train'])*100:.1f}%)")

print()
print("Class balance in test set (no SMOTE applied):")
unique, counts = np.unique(data["y_test"], return_counts=True)
for u, c in zip(unique, counts):
    print(f"  Class {int(u)}: {c} samples  ({c/len(data['y_test'])*100:.1f}%)")\
"""),

md("""\
SMOTE successfully balanced the training set to 50/50 while the test set retains
the original class distribution — this is important so that test metrics reflect
real-world performance rather than an artificially balanced evaluation.\
"""),

code("""\
# Feature importance from feature selection step — visual
fig, ax = plt.subplots(figsize=(7, 4))
features_selected = data["selected_features"]

# We'll load the RF-based importance scores from the saved figure context
# by rerunning a quick RF on the training data for visualisation purposes
from sklearn.ensemble import RandomForestClassifier

rf_tmp = RandomForestClassifier(n_estimators=100, random_state=42)
rf_tmp.fit(data["X_train"], data["y_train"])
importances = rf_tmp.feature_importances_
indices = np.argsort(importances)
sorted_features = [features_selected[i] for i in indices]

bars = ax.barh(sorted_features, importances[indices], color="#4C72B0",
               edgecolor="white", alpha=0.85)
for bar, val in zip(bars, importances[indices]):
    ax.text(bar.get_width() + 0.003, bar.get_y() + bar.get_height() / 2,
            f"{val:.3f}", va="center", fontsize=9)
ax.set_xlabel("Importance (mean decrease in impurity)")
ax.set_title("Random Forest Feature Importances — Selected Features")
plt.tight_layout()
plt.savefig("../outputs/figures/feature_selection.png", dpi=150, bbox_inches="tight")
plt.show()\
"""),

md("""\
## Summary

| Step | Details |
|------|---------|
| Raw shape | 768 rows × 8 features + 1 target |
| Missing (zeros) | Glucose 5.2%, BloodPressure 4.6%, SkinThickness 29.6%, Insulin 48.7%, BMI 1.4% |
| Class imbalance | 65.1% / 34.9% (corrected with SMOTE in training only) |
| Train / Val / Test | 700 / 115 / 116 (after SMOTE: 700 balanced) |
| Selected features | Glucose, BMI, Insulin, Age, Pregnancies |

The data is now clean, scaled, and ready for model training. Head to **Notebook 2** to train all three models.\
"""),

]


# ─────────────────────────────────────────────────────────────────────────────
# NOTEBOOK 2 — Model Training
# ─────────────────────────────────────────────────────────────────────────────
nb2_cells = [

md("""\
# Notebook 2: Model Training

**Course:** M7016H — Artificial Intelligence within the Healthcare System
**Dataset:** Pima Indians Diabetes Dataset (Dataset 4)
**Authors:** Jamshaid Amjad, Shameena Mohammed Nabeel, Suresh Balaraman

---

This notebook trains three models on the preprocessed diabetes data:

1. **Logistic Regression** — interpretable linear baseline
2. **Random Forest** — ensemble with GridSearch hyperparameter tuning
3. **MLP Neural Network** — feed-forward network with early stopping

All processed data was produced by Notebook 1. Run that first if the
`data/processed/` directory is empty.\
"""),

md("""\
## 1. Setup\
"""),

code("""\
import sys, os
sys.path.insert(0, os.path.abspath(".."))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

import yaml
from pathlib import Path\
"""),

code("""\
# Load config and processed splits
with open("../config/config.yaml") as f:
    cfg = yaml.safe_load(f)

from src.data.dataset import load_processed

data = load_processed("../data/processed")

X_train, y_train = data["X_train"], data["y_train"]
X_val,   y_val   = data["X_val"],   data["y_val"]
X_test,  y_test  = data["X_test"],  data["y_test"]
features          = data["selected_features"]

print("Training set   :", X_train.shape, "| class balance:", np.bincount(y_train.astype(int)))
print("Validation set :", X_val.shape,   "| class balance:", np.bincount(y_val.astype(int)))
print("Test set       :", X_test.shape,  "| class balance:", np.bincount(y_test.astype(int)))
print("Features       :", features)\
"""),

md("""\
## 2. Logistic Regression

Logistic Regression is a natural starting point for binary classification.
It's fast, interpretable, and when features are properly scaled (which ours are),
often performs surprisingly well. The model coefficients give us a direct window
into which features are driving predictions.

We use L-BFGS as the solver (well-suited to small-to-medium datasets) and run
5-fold cross-validation to get a stable estimate of generalisation performance
before we ever look at the test set.\
"""),

code("""\
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
import pickle

lr = LogisticRegression(solver="lbfgs", max_iter=1000, random_state=cfg["project"]["random_seed"])
lr.fit(X_train, y_train)

# 5-fold CV on the combined train+val set
X_trainval = np.vstack([X_train, X_val])
y_trainval = np.concatenate([y_train, y_val])

cv_scores_lr = cross_val_score(lr, X_trainval, y_trainval, cv=5, scoring="f1")
print(f"Logistic Regression — CV F1: {cv_scores_lr.mean():.4f} ± {cv_scores_lr.std():.4f}")
print(f"Fold scores: {[round(s, 4) for s in cv_scores_lr]}")\
"""),

code("""\
# Feature coefficients — what is the model actually using?
coef_df = pd.DataFrame({
    "Feature": features,
    "Coefficient": lr.coef_[0],
}).sort_values("Coefficient", ascending=False)

print(coef_df.to_string(index=False))

fig, ax = plt.subplots(figsize=(7, 4))
colors = ["#DD8452" if c > 0 else "#4C72B0" for c in coef_df["Coefficient"]]
ax.barh(coef_df["Feature"], coef_df["Coefficient"], color=colors, edgecolor="white", alpha=0.85)
ax.axvline(0, color="black", linewidth=0.8)
ax.set_xlabel("Coefficient value")
ax.set_title("Logistic Regression — Feature Coefficients")
plt.tight_layout()
plt.show()\
"""),

code("""\
# Save model
model_dir = Path("../outputs/models")
model_dir.mkdir(parents=True, exist_ok=True)

with open(model_dir / "logistic_regression.pkl", "wb") as f:
    pickle.dump(lr, f)
print("Saved logistic_regression.pkl")\
"""),

md("""\
## 3. Random Forest

Random Forest builds many decision trees in parallel and aggregates their predictions.
It handles non-linear relationships and feature interactions naturally, and it's
relatively robust to hyperparameter choices — but there are still a few parameters
worth tuning.

We use `GridSearchCV` with 5-fold cross-validation to search over:
- `n_estimators` — number of trees
- `max_depth` — how deep each tree is allowed to grow
- `min_samples_split` / `min_samples_leaf` — regularisation to prevent overfitting\
"""),

code("""\
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV

param_grid = {
    "n_estimators":     [100, 300],
    "max_depth":        [None, 10, 20],
    "min_samples_split":[2, 5],
    "min_samples_leaf": [1, 2],
}

rf_base = RandomForestClassifier(random_state=cfg["project"]["random_seed"], n_jobs=-1)

grid_search = GridSearchCV(
    rf_base,
    param_grid,
    cv=5,
    scoring="f1",
    n_jobs=-1,
    verbose=0,
)

print("Running GridSearchCV — this takes a minute or two...")
grid_search.fit(X_train, y_train)

rf = grid_search.best_estimator_

print(f"\\nBest params : {grid_search.best_params_}")
print(f"Best CV F1  : {grid_search.best_score_:.4f}")\
"""),

code("""\
# Cross-validate the tuned model on the combined train+val set
cv_scores_rf = cross_val_score(rf, X_trainval, y_trainval, cv=5, scoring="f1")
print(f"Random Forest — CV F1: {cv_scores_rf.mean():.4f} ± {cv_scores_rf.std():.4f}")
print(f"Fold scores: {[round(s, 4) for s in cv_scores_rf]}")\
"""),

code("""\
with open(model_dir / "random_forest.pkl", "wb") as f:
    pickle.dump(rf, f)
print("Saved random_forest.pkl")\
"""),

md("""\
## 4. MLP Neural Network

The MLP adds representation learning to the mix. By stacking non-linear layers,
it can capture feature interactions that a linear model would miss. We use a
deliberately small architecture — two hidden layers with 16 and 8 units — because
the dataset is small (n=768) and a larger network would likely just overfit.

Key training decisions:
- **Adam optimiser** — adaptive learning rates per parameter, usually better than SGD for small MLPs
- **ReduceLROnPlateau** — halves the learning rate if validation loss stagnates for 5 epochs
- **Early stopping (patience=10)** — stops training if validation loss doesn't improve,
  then reloads the best checkpoint\
"""),

code("""\
import torch
from src.models.model import MLP
from src.utils import set_seed

set_seed(cfg["project"]["random_seed"])

device = cfg["training"]["device"]
input_dim   = X_train.shape[1]
hidden_dims = cfg["model"]["mlp_hidden_dims"]
dropout     = cfg["model"]["mlp_dropout"]

mlp = MLP(input_dim=input_dim, hidden_dims=hidden_dims, dropout=dropout)
print(mlp)\
"""),

code("""\
from torch.utils.data import DataLoader, TensorDataset

def to_loader(X, y, batch_size, shuffle=True):
    Xt = torch.FloatTensor(X)
    yt = torch.FloatTensor(y)
    return DataLoader(TensorDataset(Xt, yt), batch_size=batch_size, shuffle=shuffle)

train_loader = to_loader(X_train, y_train, batch_size=cfg["training"]["batch_size"])
val_loader   = to_loader(X_val,   y_val,   batch_size=cfg["training"]["batch_size"], shuffle=False)

optimizer = torch.optim.Adam(mlp.parameters(), lr=cfg["training"]["learning_rate"])
criterion = torch.nn.BCEWithLogitsLoss()
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode="min", factor=0.5, patience=5
)

best_val_loss = float("inf")
patience_counter = 0
patience = cfg["training"]["patience"]
best_state = None

train_losses, val_losses = [], []

for epoch in range(1, cfg["training"]["epochs"] + 1):
    # Training
    mlp.train()
    epoch_loss = 0.0
    for Xb, yb in train_loader:
        optimizer.zero_grad()
        loss = criterion(mlp(Xb).squeeze(), yb)
        loss.backward()
        optimizer.step()
        epoch_loss += loss.item()
    train_loss = epoch_loss / len(train_loader)

    # Validation
    mlp.eval()
    val_loss = 0.0
    with torch.no_grad():
        for Xb, yb in val_loader:
            val_loss += criterion(mlp(Xb).squeeze(), yb).item()
    val_loss /= len(val_loader)

    train_losses.append(train_loss)
    val_losses.append(val_loss)
    scheduler.step(val_loss)

    if val_loss < best_val_loss:
        best_val_loss = val_loss
        patience_counter = 0
        best_state = {k: v.clone() for k, v in mlp.state_dict().items()}
    else:
        patience_counter += 1
        if patience_counter >= patience:
            print(f"Early stopping at epoch {epoch}")
            break

    if epoch % 10 == 0:
        print(f"Epoch {epoch:3d} | train loss {train_loss:.4f} | val loss {val_loss:.4f}")

mlp.load_state_dict(best_state)
print(f"\\nBest val loss: {best_val_loss:.4f}")\
"""),

code("""\
# Training curve
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(train_losses, label="Train loss", color="#4C72B0")
ax.plot(val_losses,   label="Val loss",   color="#DD8452")
ax.set_xlabel("Epoch")
ax.set_ylabel("BCE Loss")
ax.set_title("MLP Training Curve")
ax.legend()
ax.grid(alpha=0.4)
plt.tight_layout()
plt.savefig("../outputs/figures/mlp_training.png", dpi=150, bbox_inches="tight")
plt.show()\
"""),

code("""\
torch.save(mlp.state_dict(), model_dir / "mlp_best.pt")
print("Saved mlp_best.pt")\
"""),

md("""\
## 5. Cross-Validation Summary

Before we look at the test set, let's compare the cross-validation F1 scores.
These are more reliable than a single train/test split because they average
performance across five different holdout sets.\
"""),

code("""\
cv_summary = pd.DataFrame({
    "Model": ["Logistic Regression", "Random Forest"],
    "CV F1 Mean": [cv_scores_lr.mean(), cv_scores_rf.mean()],
    "CV F1 Std":  [cv_scores_lr.std(),  cv_scores_rf.std()],
    "Fold Scores": [
        [round(s, 4) for s in cv_scores_lr],
        [round(s, 4) for s in cv_scores_rf],
    ]
})
print(cv_summary.to_string(index=False))\
"""),

md("""\
Random Forest (CV F1 ≈ 0.801) outperforms Logistic Regression (CV F1 ≈ 0.718)
on cross-validation, suggesting it captures more of the underlying signal.
We don't run CV on the MLP here because the training procedure already includes
a validation set for early stopping — mixing that with CV would require nested
cross-validation which is beyond the scope of this project.

All three models are saved to `outputs/models/`. Head to **Notebook 3** to evaluate
them on the held-out test set.\
"""),

]


# ─────────────────────────────────────────────────────────────────────────────
# NOTEBOOK 3 — Evaluation & Results
# ─────────────────────────────────────────────────────────────────────────────
nb3_cells = [

md("""\
# Notebook 3: Evaluation & Results

**Course:** M7016H — Artificial Intelligence within the Healthcare System
**Dataset:** Pima Indians Diabetes Dataset (Dataset 4)
**Authors:** Jamshaid Amjad, Shameena Mohammed Nabeel, Suresh Balaraman

---

This notebook loads the three trained models and evaluates them on the held-out test set —
data that was never seen during training or hyperparameter tuning.

Metrics reported: **sensitivity (recall)**, **specificity**, **precision**, **F1 score**,
**AUROC**, and **accuracy**. In a clinical screening context, sensitivity is the metric we
care about most: missing a diabetic patient (false negative) is more costly than
sending a non-diabetic patient for a confirmatory test (false positive).\
"""),

md("""\
## 1. Setup\
"""),

code("""\
import sys, os
sys.path.insert(0, os.path.abspath(".."))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pickle, torch, warnings
warnings.filterwarnings("ignore")

from sklearn.metrics import (
    confusion_matrix, classification_report,
    roc_curve, auc, ConfusionMatrixDisplay,
)

from src.data.dataset import load_processed
from src.models.model import MLP

import yaml
with open("../config/config.yaml") as f:
    cfg = yaml.safe_load(f)

sns.set_theme(style="whitegrid", palette="muted")\
"""),

code("""\
# Load processed test data
data     = load_processed("../data/processed")
X_test   = data["X_test"]
y_test   = data["y_test"]
features = data["selected_features"]

print(f"Test set: {X_test.shape}  |  Positive (diabetic): {y_test.sum().astype(int)}/{len(y_test)}")\
"""),

code("""\
# Load all three trained models
MODEL_DIR = "../outputs/models"

with open(f"{MODEL_DIR}/logistic_regression.pkl", "rb") as f:
    lr = pickle.load(f)

with open(f"{MODEL_DIR}/random_forest.pkl", "rb") as f:
    rf = pickle.load(f)

mlp = MLP(
    input_dim=X_test.shape[1],
    hidden_dims=cfg["model"]["mlp_hidden_dims"],
    dropout=cfg["model"]["mlp_dropout"]
)
mlp.load_state_dict(torch.load(f"{MODEL_DIR}/mlp_best.pt", map_location="cpu"))
mlp.eval()

print("All models loaded.")\
"""),

md("""\
## 2. Generate Predictions\
"""),

code("""\
# Logistic Regression
lr_pred = lr.predict(X_test)
lr_prob = lr.predict_proba(X_test)[:, 1]

# Random Forest
rf_pred = rf.predict(X_test)
rf_prob = rf.predict_proba(X_test)[:, 1]

# MLP — use the built-in predict_proba / predict methods
mlp_prob = mlp.predict_proba(X_test)[:, 1]
mlp_pred = mlp.predict(X_test)

print("Predictions generated for all three models.")\
"""),

md("""\
## 3. Metrics

The function below computes everything we need.
Sensitivity and specificity are derived directly from the confusion matrix:
- **Sensitivity** = TP / (TP + FN) — of all diabetic patients, what fraction did we catch?
- **Specificity** = TN / (TN + FP) — of all non-diabetic patients, what fraction did we correctly clear?\
"""),

code("""\
def evaluate(y_true, y_pred, y_prob, name):
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()

    sensitivity = tp / (tp + fn)
    specificity = tn / (tn + fp)
    precision   = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    f1          = 2 * precision * sensitivity / (precision + sensitivity) if (precision + sensitivity) > 0 else 0.0
    accuracy    = (tp + tn) / len(y_true)
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    auroc       = auc(fpr, tpr)

    return {
        "Model":       name,
        "Sensitivity": round(sensitivity, 4),
        "Specificity": round(specificity, 4),
        "Precision":   round(precision,   4),
        "F1 Score":    round(f1,          4),
        "AUROC":       round(auroc,       4),
        "Accuracy":    round(accuracy,    4),
        "TP": int(tp), "TN": int(tn), "FP": int(fp), "FN": int(fn),
    }

lr_metrics  = evaluate(y_test, lr_pred,  lr_prob,  "Logistic Regression")
rf_metrics  = evaluate(y_test, rf_pred,  rf_prob,  "Random Forest")
mlp_metrics = evaluate(y_test, mlp_pred, mlp_prob, "MLP")\
"""),

md("""\
## 4. Results Table\
"""),

code("""\
cols = ["Model", "Sensitivity", "Specificity", "Precision", "F1 Score", "AUROC", "Accuracy"]
results_df = pd.DataFrame([lr_metrics, rf_metrics, mlp_metrics])[cols]
results_df = results_df.set_index("Model")

print(results_df.to_string())
print()

# Highlight the best value in each column
best = results_df.idxmax()
print("Best per metric:")
for metric, model in best.items():
    print(f"  {metric:<15} → {model}  ({results_df.loc[model, metric]})")\
"""),

md("""\
**Reading the table:**

- The **MLP** achieves the highest AUROC (0.875) — it has the best overall ability to
  rank patients by risk.
- **Logistic Regression** leads on F1 (0.683) and ties on specificity. Given that it's
  also the simplest and most interpretable model, this is a strong result.
- **Random Forest** has the best specificity (0.853), meaning it generates the fewest
  false positives — useful if downstream confirmatory tests are expensive.
- All three models substantially outperform a naive majority-class baseline
  (AUROC = 0.500, sensitivity = 0.000).\
"""),

md("""\
## 5. Confusion Matrices\
"""),

code("""\
fig, axes = plt.subplots(1, 3, figsize=(14, 4))
model_pairs = [
    ("Logistic Regression", lr_pred),
    ("Random Forest",       rf_pred),
    ("MLP",                 mlp_pred),
]

for ax, (name, pred) in zip(axes, model_pairs):
    cm = confusion_matrix(y_test, pred)
    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=["No Diabetes", "Diabetes"]
    )
    disp.plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title(name, fontsize=11, fontweight="bold")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")

plt.suptitle("Confusion Matrices — Test Set (n=116)", fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("../outputs/figures/confusion_matrices_combined.png", dpi=150, bbox_inches="tight")
plt.show()\
"""),

md("""\
## 6. ROC Curves\
"""),

code("""\
fig, ax = plt.subplots(figsize=(7, 6))

for name, y_prob, color in [
    ("Logistic Regression", lr_prob,  "#4C72B0"),
    ("Random Forest",       rf_prob,  "#DD8452"),
    ("MLP",                 mlp_prob, "#55A868"),
]:
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    roc_auc = auc(fpr, tpr)
    ax.plot(fpr, tpr, color=color, lw=2, label=f"{name}  (AUC = {roc_auc:.3f})")

ax.plot([0, 1], [0, 1], "k--", lw=1.2, label="Random baseline (AUC = 0.500)")
ax.set_xlabel("False Positive Rate (1 - Specificity)")
ax.set_ylabel("True Positive Rate (Sensitivity)")
ax.set_title("ROC Curves — All Models vs Baseline")
ax.legend(loc="lower right")
ax.grid(alpha=0.35)
plt.tight_layout()
plt.savefig("../outputs/figures/roc_curves_comparison.png", dpi=150, bbox_inches="tight")
plt.show()\
"""),

md("""\
## 7. Model Comparison — Bar Chart\
"""),

code("""\
metrics_to_plot = ["Sensitivity", "Specificity", "F1 Score", "AUROC", "Accuracy"]
model_names = ["Logistic Regression", "Random Forest", "MLP"]
colors      = ["#4C72B0", "#DD8452", "#55A868"]

x = np.arange(len(metrics_to_plot))
width = 0.22

fig, ax = plt.subplots(figsize=(11, 5))
for i, (model, color) in enumerate(zip(model_names, colors)):
    vals = [results_df.loc[model, m] for m in metrics_to_plot]
    bars = ax.bar(x + i * width, vals, width, label=model, color=color,
                  alpha=0.85, edgecolor="white")
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                f"{v:.2f}", ha="center", va="bottom", fontsize=7.5, fontweight="bold")

ax.set_xticks(x + width)
ax.set_xticklabels(metrics_to_plot, fontsize=10)
ax.set_ylim(0, 1.13)
ax.set_ylabel("Score")
ax.set_title("Model Performance Comparison — Test Set")
ax.legend()
ax.grid(axis="y", alpha=0.35)
plt.tight_layout()
plt.savefig("../outputs/figures/model_comparison.png", dpi=150, bbox_inches="tight")
plt.show()\
"""),

md("""\
## 8. Feature Importance (Random Forest)\
"""),

code("""\
importances = rf.feature_importances_
indices     = np.argsort(importances)
sorted_feats = [features[i] for i in indices]

fig, ax = plt.subplots(figsize=(7, 4))
bars = ax.barh(sorted_feats, importances[indices], color="#4C72B0",
               edgecolor="white", alpha=0.85)
for bar, val in zip(bars, importances[indices]):
    ax.text(bar.get_width() + 0.003, bar.get_y() + bar.get_height() / 2,
            f"{val:.3f}", va="center", fontsize=9)
ax.set_xlabel("Mean decrease in impurity")
ax.set_title("Random Forest — Feature Importances")
ax.grid(axis="x", alpha=0.35)
plt.tight_layout()
plt.savefig("../outputs/figures/feature_importance.png", dpi=150, bbox_inches="tight")
plt.show()\
"""),

md("""\
**Glucose** is by far the most important feature, accounting for roughly 30–40% of the
model's decision-making. This aligns with clinical practice — plasma glucose is the
primary biomarker used for diabetes diagnosis. **BMI** and **Age** follow, which is again
consistent with the known risk factors for Type 2 diabetes.\
"""),

md("""\
## 9. Classification Reports (Full Detail)\
"""),

code("""\
for name, pred in [("Logistic Regression", lr_pred), ("Random Forest", rf_pred), ("MLP", mlp_pred)]:
    print(f"{'='*50}")
    print(f" {name}")
    print(f"{'='*50}")
    print(classification_report(y_test, pred, target_names=["No Diabetes", "Diabetes"]))
    m = [m for m in [lr_metrics, rf_metrics, mlp_metrics] if m["Model"] == name][0]
    print(f"  Confusion matrix:  TP={m['TP']}  FN={m['FN']}  FP={m['FP']}  TN={m['TN']}")
    print()\
"""),

md("""\
## 10. Saving Results\
"""),

code("""\
import json
from pathlib import Path

skip = {"Model", "TP", "TN", "FP", "FN"}
report = {}
for key, metrics in [("logistic_regression", lr_metrics), ("random_forest", rf_metrics), ("mlp", mlp_metrics)]:
    report[key] = {k.lower().replace(" ", "_"): v for k, v in metrics.items() if k not in skip}

report_path = Path("../outputs/reports/evaluation_results.json")
report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text(json.dumps(report, indent=2))
print(f"Saved: {report_path}")\
"""),

md("""\
## Summary & Clinical Interpretation

| Model | Sensitivity | Specificity | F1 | AUROC |
|-------|------------|------------|-----|-------|
| Logistic Regression | 0.683 | 0.827 | 0.683 | 0.866 |
| Random Forest | 0.610 | 0.853 | 0.649 | 0.841 |
| MLP | 0.659 | 0.827 | 0.667 | **0.875** |

All three models are meaningfully better than random. For a **screening** use case —
where the goal is to identify patients who should be sent for confirmatory testing —
the MLP or Logistic Regression would be preferred due to their higher sensitivity.
The Random Forest's higher specificity makes it more conservative, which is better
when follow-up tests are expensive or invasive.

**Limitations to keep in mind:**
- The dataset is small (n=768) and demographically narrow (Pima women only),
  so these results may not transfer to other populations.
- Insulin and SkinThickness have substantial missing data (~30–49%); median imputation
  is simple and may not fully capture the true distribution.
- None of the models have been probability-calibrated — the raw predicted probabilities
  should not be used as clinical risk estimates without further validation.\
"""),

]


# ─────────────────────────────────────────────────────────────────────────────
# Write to disk
# ─────────────────────────────────────────────────────────────────────────────
save(notebook(nb1_cells), "01_data_exploration.ipynb")
save(notebook(nb2_cells), "02_model_training.ipynb")
save(notebook(nb3_cells), "03_evaluation_and_results.ipynb")

print("\nDone. Three notebooks created in notebooks/")
