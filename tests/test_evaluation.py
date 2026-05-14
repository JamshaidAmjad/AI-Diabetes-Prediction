"""Tests for evaluation metrics."""

import numpy as np
import pytest

from src.evaluation.evaluate import compute_metrics


def test_perfect_predictions():
    y = np.array([0, 1, 0, 1, 1])
    metrics = compute_metrics(y, y, y_prob=y.astype(float))
    assert metrics["accuracy"] == 1.0
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1_score"] == 1.0
    assert metrics["roc_auc"] == 1.0


def test_all_wrong_predictions():
    y_true = np.array([0, 0, 1, 1])
    y_pred = np.array([1, 1, 0, 0])
    metrics = compute_metrics(y_true, y_pred)
    assert metrics["accuracy"] == 0.0
    assert metrics["recall"] == 0.0


def test_metrics_keys_present():
    y = np.array([0, 1, 0, 1])
    metrics = compute_metrics(y, y)
    for key in ("accuracy", "precision", "recall", "f1_score"):
        assert key in metrics


def test_roc_auc_only_when_prob_provided():
    y = np.array([0, 1, 0, 1])
    without_prob = compute_metrics(y, y, y_prob=None)
    assert "roc_auc" not in without_prob

    with_prob = compute_metrics(y, y, y_prob=np.array([0.1, 0.9, 0.2, 0.8]))
    assert "roc_auc" in with_prob


def test_metrics_values_in_range():
    np.random.seed(0)
    y_true = np.random.randint(0, 2, 50)
    y_pred = np.random.randint(0, 2, 50)
    y_prob = np.random.rand(50)
    metrics = compute_metrics(y_true, y_pred, y_prob)
    for v in metrics.values():
        assert 0.0 <= v <= 1.0
