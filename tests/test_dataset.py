"""Tests for the data preprocessing pipeline."""

import numpy as np
import pandas as pd
import pytest

from src.data.dataset import (
    FEATURE_NAMES,
    ZERO_AS_MISSING,
    load_raw,
    split_data,
    build_dataset,
)


@pytest.fixture
def synthetic_csv(tmp_path):
    """Create a minimal synthetic diabetes CSV for testing."""
    np.random.seed(0)
    n = 200
    data = {f: np.random.uniform(1, 100, n) for f in FEATURE_NAMES}
    data["Outcome"] = np.random.randint(0, 2, n)
    # Introduce some zeros that should become NaN
    data["Glucose"][::10] = 0
    data["BMI"][::15] = 0
    df = pd.DataFrame(data)
    csv = tmp_path / "diabetes.csv"
    df.to_csv(csv, index=False)
    return str(csv)


def test_load_raw_zeros_replaced(synthetic_csv):
    df = load_raw(synthetic_csv)
    for col in ZERO_AS_MISSING:
        assert df[col].isna().sum() > 0 or (df[col] > 0).all(), \
            f"Zeros in {col} should be replaced with NaN"


def test_split_sizes(synthetic_csv):
    df = load_raw(synthetic_csv)
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(df, val_split=0.15, test_split=0.15)
    total = len(X_train) + len(X_val) + len(X_test)
    assert total == len(df)
    assert len(X_val) > 0
    assert len(X_test) > 0


def test_split_no_overlap(synthetic_csv):
    df = load_raw(synthetic_csv)
    df = df.reset_index(drop=True)
    X_train, X_val, X_test, *_ = split_data(df)
    assert set(X_train.index).isdisjoint(X_val.index)
    assert set(X_train.index).isdisjoint(X_test.index)
    assert set(X_val.index).isdisjoint(X_test.index)


def test_build_dataset_shapes(synthetic_csv, tmp_path):
    data = build_dataset(
        csv_path=synthetic_csv,
        val_split=0.15,
        test_split=0.15,
        n_features=5,
        use_smote=False,
        random_seed=42,
    )
    assert data["X_train"].shape[1] == 5
    assert data["X_val"].shape[1] == 5
    assert data["X_test"].shape[1] == 5
    assert len(data["selected_features"]) == 5
    assert data["X_train"].shape[0] == len(data["y_train"])


def test_build_dataset_saves_files(synthetic_csv, tmp_path):
    processed = str(tmp_path / "processed")
    build_dataset(
        csv_path=synthetic_csv,
        n_features=5,
        use_smote=False,
        processed_dir=processed,
    )
    from pathlib import Path
    out = Path(processed)
    for fname in ["X_train.npy", "y_train.npy", "X_val.npy", "y_val.npy",
                  "X_test.npy", "y_test.npy", "selected_features.txt"]:
        assert (out / fname).exists(), f"Missing {fname}"


def test_smote_balances_classes(synthetic_csv):
    data = build_dataset(
        csv_path=synthetic_csv,
        n_features=5,
        use_smote=True,
        random_seed=42,
    )
    unique, counts = np.unique(data["y_train"], return_counts=True)
    assert len(unique) == 2
    assert counts[0] == counts[1], "SMOTE should produce equal class counts"
