"""Evaluation pipeline: metrics, confusion matrices, ROC curves, and model comparison."""

import json
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import torch
from sklearn.metrics import (
    accuracy_score,
    auc,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

from src.models.model import MLP


def compute_metrics(
    y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray = None
) -> Dict[str, float]:
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    metrics = {
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "sensitivity": round(sensitivity, 4),
        "specificity": round(specificity, 4),
        "precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_true, y_pred, zero_division=0), 4),
        "f1_score": round(f1_score(y_true, y_pred, zero_division=0), 4),
    }
    if y_prob is not None:
        metrics["roc_auc"] = round(roc_auc_score(y_true, y_prob), 4)
    return metrics


def plot_confusion_matrix(
    y_true: np.ndarray, y_pred: np.ndarray, model_name: str, save_path: str
) -> None:
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


def plot_roc_curves(
    model_probs: Dict[str, Tuple[np.ndarray, np.ndarray]], figures_dir: str
) -> None:
    """Plot ROC curves for all models on a single chart for side-by-side comparison."""
    fig, ax = plt.subplots(figsize=(7, 6))
    colors = ["steelblue", "tomato", "seagreen", "darkorange"]

    for (name, (y_true, y_prob)), color in zip(model_probs.items(), colors):
        fpr, tpr, _ = roc_curve(y_true, y_prob)
        roc_auc = auc(fpr, tpr)
        ax.plot(fpr, tpr, color=color, lw=2, label=f"{name} (AUC = {roc_auc:.3f})")

    ax.plot([0, 1], [0, 1], "k--", lw=1.5, label="Random baseline (AUC = 0.500)")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curves — Model Comparison")
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)
    plt.tight_layout()

    save_path = f"{figures_dir}/roc_curves_comparison.png"
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved ROC curves       → {save_path}")


def plot_model_comparison(
    results: Dict[str, Dict[str, float]], figures_dir: str
) -> None:
    """Grouped bar chart comparing Accuracy, F1, and ROC-AUC across all models."""
    display_names = {
        "logistic_regression": "Logistic Regression",
        "random_forest": "Random Forest",
        "mlp": "MLP",
    }
    metrics_to_plot = ["accuracy", "f1_score", "roc_auc"]
    metric_labels = ["Accuracy", "F1 Score", "ROC-AUC"]
    colors = ["steelblue", "tomato", "seagreen"]

    model_keys = list(results.keys())
    model_labels = [display_names.get(k, k) for k in model_keys]
    x = np.arange(len(model_keys))
    width = 0.25

    fig, ax = plt.subplots(figsize=(10, 6))
    for i, (metric, label, color) in enumerate(zip(metrics_to_plot, metric_labels, colors)):
        values = [results[m].get(metric, 0.0) for m in model_keys]
        bars = ax.bar(x + i * width, values, width, label=label, color=color, alpha=0.85,
                      edgecolor="white")
        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.005,
                f"{val:.3f}",
                ha="center", va="bottom", fontsize=8, fontweight="bold",
            )

    ax.set_xticks(x + width)
    ax.set_xticklabels(model_labels, fontsize=11)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Score")
    ax.set_title("Model Performance Comparison (Test Set)")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    save_path = f"{figures_dir}/model_comparison.png"
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved model comparison  → {save_path}")


def plot_feature_importance(
    rf_model, feature_names: List[str], figures_dir: str
) -> None:
    """Horizontal bar chart of Random Forest feature importances."""
    importances = rf_model.feature_importances_
    indices = np.argsort(importances)  # ascending so most important is at top
    sorted_names = [feature_names[i] for i in indices]
    sorted_values = importances[indices]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(
        sorted_names, sorted_values, color="steelblue", edgecolor="white", alpha=0.85
    )
    for bar, val in zip(bars, sorted_values):
        ax.text(
            bar.get_width() + 0.003, bar.get_y() + bar.get_height() / 2,
            f"{val:.3f}", va="center", fontsize=9,
        )
    ax.set_xlabel("Importance")
    ax.set_title("Random Forest — Feature Importances")
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()

    save_path = f"{figures_dir}/feature_importance.png"
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved feature importance → {save_path}")


def evaluate_sklearn(
    model,
    X_test: np.ndarray,
    y_test: np.ndarray,
    model_name: str,
    figures_dir: str,
) -> Tuple[Dict[str, float], Optional[np.ndarray]]:
    """Evaluate a sklearn model; returns (metrics_dict, y_prob)."""
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None
    metrics = compute_metrics(y_test, y_pred, y_prob)
    safe_name = model_name.lower().replace(" ", "_")
    plot_confusion_matrix(
        y_test, y_pred, model_name, f"{figures_dir}/{safe_name}_confusion.png"
    )
    print(f"\n{'=' * 50}")
    print(f" {model_name}")
    print(f"{'=' * 50}")
    print(classification_report(y_test, y_pred, target_names=["No Diabetes", "Diabetes"]))
    return metrics, y_prob


def evaluate_mlp(
    mlp: MLP,
    X_test: np.ndarray,
    y_test: np.ndarray,
    device: str,
    figures_dir: str,
) -> Tuple[Dict[str, float], np.ndarray]:
    """Evaluate the MLP; returns (metrics_dict, y_prob)."""
    y_pred = mlp.predict(X_test, device=device)
    y_prob = mlp.predict_proba(X_test, device=device)[:, 1]
    metrics = compute_metrics(y_test, y_pred, y_prob)
    plot_confusion_matrix(y_test, y_pred, "MLP", f"{figures_dir}/mlp_confusion.png")
    print(f"\n{'=' * 50}")
    print(" MLP (Neural Network)")
    print(f"{'=' * 50}")
    print(classification_report(y_test, y_pred, target_names=["No Diabetes", "Diabetes"]))
    return metrics, y_prob


def evaluate_all(
    model_dir: str,
    figures_dir: str,
    reports_dir: str,
    X_test: np.ndarray,
    y_test: np.ndarray,
    mlp_input_dim: int,
    mlp_hidden_dims,
    mlp_dropout: float,
    feature_names: Optional[List[str]] = None,
    device: str = "cpu",
) -> Dict[str, Dict[str, float]]:
    """Load all saved models, evaluate on the test set, and produce all comparison plots."""
    results: Dict[str, Dict[str, float]] = {}
    model_probs: Dict[str, Tuple[np.ndarray, np.ndarray]] = {}
    rf_model_ref = None
    Path(reports_dir).mkdir(parents=True, exist_ok=True)

    lr_path = Path(model_dir) / "logistic_regression.pkl"
    if lr_path.exists():
        with open(lr_path, "rb") as f:
            lr_model = pickle.load(f)
        metrics, y_prob = evaluate_sklearn(
            lr_model, X_test, y_test, "Logistic Regression", figures_dir
        )
        results["logistic_regression"] = metrics
        if y_prob is not None:
            model_probs["Logistic Regression"] = (y_test, y_prob)

    rf_path = Path(model_dir) / "random_forest.pkl"
    if rf_path.exists():
        with open(rf_path, "rb") as f:
            rf_model = pickle.load(f)
        rf_model_ref = rf_model
        metrics, y_prob = evaluate_sklearn(
            rf_model, X_test, y_test, "Random Forest", figures_dir
        )
        results["random_forest"] = metrics
        if y_prob is not None:
            model_probs["Random Forest"] = (y_test, y_prob)

    mlp_path = Path(model_dir) / "mlp_best.pt"
    if mlp_path.exists():
        mlp = MLP(input_dim=mlp_input_dim, hidden_dims=mlp_hidden_dims, dropout=mlp_dropout)
        mlp.load_state_dict(torch.load(mlp_path, map_location=device))
        mlp.eval()
        metrics, y_prob = evaluate_mlp(mlp, X_test, y_test, device, figures_dir)
        results["mlp"] = metrics
        model_probs["MLP"] = (y_test, y_prob)

    # Comparison plots — only meaningful when multiple models are evaluated
    if len(model_probs) > 1:
        plot_roc_curves(model_probs, figures_dir)
    if len(results) > 1:
        plot_model_comparison(results, figures_dir)
    if rf_model_ref is not None and feature_names:
        plot_feature_importance(rf_model_ref, feature_names, figures_dir)

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
        feature_names=data["selected_features"],
        device=cfg["training"]["device"],
    )
