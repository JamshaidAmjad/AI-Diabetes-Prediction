"""
Standalone preprocessing script.

Run this once to generate processed data splits and EDA figures:

    python scripts/preprocess.py

Outputs:
    data/processed/  — imputed, scaled, SMOTE-balanced NumPy splits
    outputs/figures/ — EDA plots (class distribution, feature distributions,
                       correlation heatmap, feature selection)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
from src.data.dataset import build_dataset

with open("config/config.yaml", "r") as f:
    cfg = yaml.safe_load(f)

csv_path = Path(cfg["data"]["raw_dir"]) / cfg["data"]["filename"]

print("Running preprocessing pipeline...")
data = build_dataset(
    csv_path=str(csv_path),
    val_split=cfg["data"]["val_split"],
    test_split=cfg["data"]["test_split"],
    n_features=cfg["data"]["n_features_to_select"],
    use_smote=cfg["data"]["use_smote"],
    random_seed=cfg["project"]["random_seed"],
    processed_dir=cfg["data"]["processed_dir"],
)

print(f"\nSelected features : {data['selected_features']}")
print(f"Train shape       : {data['X_train'].shape}  (after SMOTE)")
print(f"Val   shape       : {data['X_val'].shape}")
print(f"Test  shape       : {data['X_test'].shape}")
print(f"\nSaved to {cfg['data']['processed_dir']}/")

# Generate EDA figures
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.data.dataset import FEATURE_NAMES, ZERO_AS_MISSING, load_raw

sns.set_theme(style="whitegrid")
figs_dir = Path(cfg["outputs"]["figures_dir"])
figs_dir.mkdir(parents=True, exist_ok=True)

df_raw = pd.read_csv(str(csv_path))
df = load_raw(str(csv_path))

# Class distribution
fig, ax = plt.subplots(figsize=(5, 4))
counts = df_raw["Outcome"].value_counts().sort_index()
bars = ax.bar(["No Diabetes (0)", "Diabetes (1)"], counts.values,
              color=["steelblue", "tomato"], edgecolor="black")
for bar in bars:
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 3,
            str(int(bar.get_height())), ha="center", fontsize=11)
ax.set_ylabel("Count")
ax.set_title("Class Distribution")
plt.tight_layout()
plt.savefig(figs_dir / "class_distribution.png", dpi=150)
plt.close()

# Feature distributions by outcome
fig, axes = plt.subplots(2, 4, figsize=(16, 8))
for ax, feat in zip(axes.flatten(), FEATURE_NAMES):
    for outcome, color, label in [(0, "steelblue", "No Diabetes"), (1, "tomato", "Diabetes")]:
        df[df["Outcome"] == outcome][feat].dropna().plot(
            kind="kde", ax=ax, color=color, label=label, linewidth=2
        )
    ax.set_title(feat)
    ax.legend(fontsize=7)
plt.suptitle("Feature Distributions by Outcome", fontsize=13)
plt.tight_layout()
plt.savefig(figs_dir / "feature_distributions.png", dpi=150)
plt.close()

# Correlation heatmap
fig, ax = plt.subplots(figsize=(9, 7))
sns.heatmap(df_raw.corr(), annot=True, fmt=".2f", cmap="coolwarm",
            ax=ax, linewidths=0.5)
ax.set_title("Feature Correlation Heatmap")
plt.tight_layout()
plt.savefig(figs_dir / "correlation_heatmap.png", dpi=150)
plt.close()

# Feature importance from Random Forest
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer

X = df[FEATURE_NAMES]
y = df["Outcome"]
X_imp = pd.DataFrame(SimpleImputer(strategy="median").fit_transform(X), columns=FEATURE_NAMES)
rf = RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)
rf.fit(X_imp, y)
importances = pd.Series(rf.feature_importances_, index=FEATURE_NAMES).sort_values()
fig, ax = plt.subplots(figsize=(7, 5))
importances.plot(kind="barh", ax=ax, color="tomato", edgecolor="black")
ax.set_xlabel("Importance")
ax.set_title("Feature Importance (Random Forest)")
plt.tight_layout()
plt.savefig(figs_dir / "feature_importance.png", dpi=150)
plt.close()

print(f"Saved EDA figures to {figs_dir}/")
print("\nDone.")
