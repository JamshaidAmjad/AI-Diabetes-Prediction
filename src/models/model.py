"""Models for diabetes prediction: Logistic Regression, Random Forest, and MLP."""

from typing import List

import numpy as np
import torch
import torch.nn as nn
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier


def build_logistic_regression(random_seed: int = 42) -> LogisticRegression:
    return LogisticRegression(max_iter=1000, random_state=random_seed, solver="lbfgs")


def build_random_forest(n_estimators: int = 300, random_seed: int = 42) -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=n_estimators, random_state=random_seed, n_jobs=-1
    )


class MLP(nn.Module):
    """Small fully-connected network for binary tabular classification."""

    def __init__(self, input_dim: int, hidden_dims: List[int], dropout: float = 0.3):
        super().__init__()
        layers: List[nn.Module] = []
        prev = input_dim
        for h in hidden_dims:
            layers += [nn.Linear(prev, h), nn.BatchNorm1d(h), nn.ReLU(), nn.Dropout(dropout)]
            prev = h
        layers.append(nn.Linear(prev, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x).squeeze(1)

    def predict_proba(self, X: np.ndarray, device: str = "cpu") -> np.ndarray:
        self.eval()
        with torch.no_grad():
            t = torch.tensor(X, dtype=torch.float32).to(device)
            logits = self.forward(t).cpu().numpy()
        probs = 1 / (1 + np.exp(-logits))
        return np.stack([1 - probs, probs], axis=1)

    def predict(self, X: np.ndarray, device: str = "cpu", threshold: float = 0.5) -> np.ndarray:
        return (self.predict_proba(X, device)[:, 1] >= threshold).astype(int)
