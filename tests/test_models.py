"""Tests for model definitions."""

import numpy as np
import pytest
import torch

from src.models.model import MLP, build_logistic_regression, build_random_forest


@pytest.fixture
def small_data():
    np.random.seed(42)
    X = np.random.randn(100, 5).astype(np.float32)
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    return X, y


def test_logistic_regression_fit_predict(small_data):
    X, y = small_data
    model = build_logistic_regression(random_seed=42)
    model.fit(X, y)
    preds = model.predict(X)
    assert preds.shape == (100,)
    assert set(preds).issubset({0, 1})


def test_random_forest_fit_predict(small_data):
    X, y = small_data
    model = build_random_forest(n_estimators=10, random_seed=42)
    model.fit(X, y)
    preds = model.predict(X)
    assert preds.shape == (100,)
    assert set(preds).issubset({0, 1})


def test_mlp_forward_shape():
    model = MLP(input_dim=5, hidden_dims=[16, 8], dropout=0.0)
    x = torch.randn(32, 5)
    out = model(x)
    assert out.shape == (32,), f"Expected (32,), got {out.shape}"


def test_mlp_predict_binary(small_data):
    X, y = small_data
    model = MLP(input_dim=5, hidden_dims=[16, 8], dropout=0.0)
    preds = model.predict(X)
    assert preds.shape == (100,)
    assert set(preds).issubset({0, 1})


def test_mlp_predict_proba_sums_to_one(small_data):
    X, _ = small_data
    model = MLP(input_dim=5, hidden_dims=[16, 8], dropout=0.0)
    proba = model.predict_proba(X)
    assert proba.shape == (100, 2)
    np.testing.assert_allclose(proba.sum(axis=1), np.ones(100), atol=1e-5)


def test_mlp_no_xray_references():
    """Ensure the model file contains no leftover X-ray references."""
    import inspect
    src = inspect.getsource(MLP)
    assert "xray" not in src.lower()
    assert "resnet" not in src.lower()
    assert "covid" not in src.lower()
