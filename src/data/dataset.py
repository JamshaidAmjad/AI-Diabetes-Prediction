"""Tabular dataset loader and preprocessing pipeline for diabetes prediction."""

from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE


FEATURE_NAMES = [
    "Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
    "Insulin", "BMI", "DiabetesPedigreeFunction", "Age",
]
TARGET_NAME = "Outcome"
ZERO_AS_MISSING = ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]


def load_raw(csv_path: str) -> pd.DataFrame:
    """Load raw CSV and replace biologically impossible zeros with NaN."""
    df = pd.read_csv(csv_path)
    df[ZERO_AS_MISSING] = df[ZERO_AS_MISSING].replace(0, np.nan)
    return df


def split_data(
    df: pd.DataFrame,
    val_split: float = 0.15,
    test_split: float = 0.15,
    random_seed: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame,
           pd.Series, pd.Series, pd.Series]:
    """Stratified 70/15/15 train-val-test split."""
    X = df[FEATURE_NAMES]
    y = df[TARGET_NAME]

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=(val_split + test_split), stratify=y, random_state=random_seed
    )
    relative_test = test_split / (val_split + test_split)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=relative_test, stratify=y_temp, random_state=random_seed
    )
    return X_train, X_val, X_test, y_train, y_val, y_test


def select_features(
    X_train: np.ndarray,
    y_train: np.ndarray,
    feature_names: List[str],
    n_features: int = 5,
    random_seed: int = 42,
) -> Tuple[np.ndarray, List[str]]:
    """
    Select top-n features by averaging ANOVA F-test and Random Forest ranks.
    Fitted only on training data to prevent leakage.
    """
    anova = SelectKBest(score_func=f_classif, k="all")
    anova.fit(X_train, y_train)
    anova_ranks = pd.Series(anova.scores_, index=feature_names).rank(ascending=False)

    rf = RandomForestClassifier(n_estimators=300, random_state=random_seed, n_jobs=-1)
    rf.fit(X_train, y_train)
    rf_ranks = pd.Series(rf.feature_importances_, index=feature_names).rank(ascending=False)

    avg_ranks = ((anova_ranks + rf_ranks) / 2).sort_values()
    selected = avg_ranks.head(n_features).index.tolist()
    sel_idx = [feature_names.index(f) for f in selected]
    return X_train[:, sel_idx], selected


def build_dataset(
    csv_path: str,
    val_split: float = 0.15,
    test_split: float = 0.15,
    n_features: int = 5,
    use_smote: bool = True,
    random_seed: int = 42,
    processed_dir: Optional[str] = None,
) -> dict:
    """
    Full preprocessing pipeline:
      load → split → impute → scale → feature selection → SMOTE → (save)

    Returns a dict with keys:
      X_train, y_train, X_val, y_val, X_test, y_test, selected_features
    """
    df = load_raw(csv_path)
    X_train_df, X_val_df, X_test_df, y_train, y_val, y_test = split_data(
        df, val_split, test_split, random_seed
    )

    imputer = SimpleImputer(strategy="median")
    X_train_imp = pd.DataFrame(imputer.fit_transform(X_train_df), columns=FEATURE_NAMES)
    X_val_imp = pd.DataFrame(imputer.transform(X_val_df), columns=FEATURE_NAMES)
    X_test_imp = pd.DataFrame(imputer.transform(X_test_df), columns=FEATURE_NAMES)

    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train_imp)
    X_val_sc = scaler.transform(X_val_imp)
    X_test_sc = scaler.transform(X_test_imp)

    X_train_sel, selected = select_features(
        X_train_sc, y_train.values, FEATURE_NAMES, n_features, random_seed
    )
    sel_idx = [FEATURE_NAMES.index(f) for f in selected]
    X_val_sel = X_val_sc[:, sel_idx]
    X_test_sel = X_test_sc[:, sel_idx]

    if use_smote:
        sm = SMOTE(random_state=random_seed)
        X_train_sel, y_train_arr = sm.fit_resample(X_train_sel, y_train.values)
    else:
        y_train_arr = y_train.values

    result = {
        "X_train": X_train_sel,
        "y_train": y_train_arr,
        "X_val": X_val_sel,
        "y_val": y_val.values,
        "X_test": X_test_sel,
        "y_test": y_test.values,
        "selected_features": selected,
    }

    if processed_dir:
        out = Path(processed_dir)
        out.mkdir(parents=True, exist_ok=True)
        np.save(out / "X_train.npy", X_train_sel)
        np.save(out / "y_train.npy", y_train_arr)
        np.save(out / "X_val.npy", X_val_sel)
        np.save(out / "y_val.npy", y_val.values)
        np.save(out / "X_test.npy", X_test_sel)
        np.save(out / "y_test.npy", y_test.values)
        (out / "selected_features.txt").write_text("\n".join(selected))

    return result


def load_processed(processed_dir: str) -> dict:
    """Load pre-saved processed splits from disk."""
    d = Path(processed_dir)
    selected = (d / "selected_features.txt").read_text().splitlines()
    return {
        "X_train": np.load(d / "X_train.npy"),
        "y_train": np.load(d / "y_train.npy"),
        "X_val": np.load(d / "X_val.npy"),
        "y_val": np.load(d / "y_val.npy"),
        "X_test": np.load(d / "X_test.npy"),
        "y_test": np.load(d / "y_test.npy"),
        "selected_features": selected,
    }
