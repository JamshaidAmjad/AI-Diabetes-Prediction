"""Evaluation pipeline: metrics and confusion matrix for all models."""

import json
import pickle
from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import torch
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from src.models.model import MLP


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray = None) -> Dict[str, float]:
    metrics = {
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_true, y_pred, zero_division=0), 4),
        "f1_score": round(f1_score(y_true, y_pred, zero_division=0), 4),
    }
    if y_prob is not None:
        metrics["roc_auc"] = round(roc_auc_score(y_true, y_prob), 4)
    return metrics


def plot_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, model_name: str, save_path: str):
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues", ax=ax,
        xticklabels=["No Diabetes", "Diabetes"],
        yticklabels=["No Diabetes", "Diabetes"],
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title(f"Confusion Matrix — {model_name}")
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150)
    plt.close()


def evaluate_sklearn(model, X_test: np.ndarray, y_test: np.ndarray, model_name: str, figures_dir: str) -> Dict[str, float]:
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None
    metrics = compute_metrics(y_test, y_pred, y_prob)
    plot_confusion_matrix(y_test, y_pred, model_name, f"{figures_dir}/{model_name}_confusion.png")
    print(f"\n{model_name}")
    print(classification_report(y_test, y_pred, target_names=["No Diabetes", "Diabetes"]))
    return metrics


def evaluate_mlp(
    mlp: MLP,
    X_test: np.ndarray,
    y_test: np.ndarray,
    device: str,
    figures_dir: str,
) -> Dict[str, float]:
    y_pred = mlp.predict(X_test, device=device)
    y_prob = mlp.predict_proba(X_test, device=device)[:, 1]
    metrics = compute_metrics(y_test, y_pred, y_prob)
    plot_confusion_matrix(y_test, y_pred, "MLP", f"{figures_dir}/mlp_confusion.png")
    print("\nMLP")
    print(classification_report(y_test, y_pred, target_names=["No Diabetes", "Diabetes"]))
    return metrics


def evaluate_all(
    model_dir: str,
    figures_dir: str,
    reports_dir: str,
    X_test: np.ndarray,
    y_test: np.ndarray,
    mlp_input_dim: int,
    mlp_hidden_dims,
    mlp_dropout: float,
    device: str = "cpu",
) -> Dict[str, Dict[str, float]]:
    """Load all saved models and evaluate on the test set."""
    results = {}
    Path(reports_dir).mkdir(parents=True, exist_ok=True)

    lr_path = Path(model_dir) / "logistic_regression.pkl"
    if lr_path.exists():
        with open(lr_path, "rb") as f:
            lr_model = pickle.load(f)
        results["logistic_regression"] = evaluate_sklearn(
            lr_model, X_test, y_test, "Logistic Regression", figures_dir
        )

    rf_path = Path(model_dir) / "random_forest.pkl"
    if rf_path.exists():
        with open(rf_path, "rb") as f:
            rf_model = pickle.load(f)
        results["random_forest"] = evaluate_sklearn(
            rf_model, X_test, y_test, "Random Forest", figures_dir
        )

    mlp_path = Path(model_dir) / "mlp_best.pt"
    if mlp_path.exists():
        mlp = MLP(input_dim=mlp_input_dim, hidden_dims=mlp_hidden_dims, dropout=mlp_dropout)
        mlp.load_state_dict(torch.load(mlp_path, map_location=device))
        mlp.eval()
        results["mlp"] = evaluate_mlp(mlp, X_test, y_test, device, figures_dir)

    report_path = Path(reports_dir) / "evaluation_results.json"
    report_path.write_text(json.dumps(results, indent=2))
    print(f"\nSaved evaluation report → {report_path}")
    return results


if __name__ == "__main__":
    import yaml
    from src.data.dataset import load_processed

    with open("config/config.yaml", "r") as f:
        cfg = yaml.safe_load(f)

    data = load_processed(cfg["data"]["processed_dir"])
    evaluate_all(
        model_dir=cfg["outputs"]["model_dir"],
        figures_dir=cfg["outputs"]["figures_dir"],
        reports_dir=cfg["outputs"]["reports_dir"],
        X_test=data["X_test"],
        y_test=data["y_test"],
        mlp_input_dim=data["X_test"].shape[1],
        mlp_hidden_dims=cfg["model"]["mlp_hidden_dims"],
        mlp_dropout=cfg["model"]["mlp_dropout"],
        device=cfg["training"]["device"],
    )
