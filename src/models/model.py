"""Models for diabetes prediction: Logistic Regression, Random Forest, and MLP.

Architecture
------------
Logistic Regression  — interpretable linear baseline
Random Forest        — strong tabular ensemble model
MLP Neural Network   — nonlinear learning

    Input Layer (8 features)
          ↓
    Dense(16) + ReLU
          ↓
      Dropout(0.2)
          ↓
    Dense(8)  + ReLU
          ↓
    Dense(1)  + Sigmoid
"""

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
    """
    Feed-forward network for binary diabetes prediction.

    Architecture:
        Input → Dense(16) + ReLU → Dropout(0.2) → Dense(8) + ReLU → Dense(1) + Sigmoid

    Training uses BCEWithLogitsLoss (numerically equivalent to Sigmoid + BCE but
    more stable). The Sigmoid is applied explicitly only during inference.
    """

    def __init__(self, input_dim: int = 8, hidden_dims: List[int] = None, dropout: float = 0.2):
        super().__init__()
        if hidden_dims is None:
            hidden_dims = [16, 8]
        layers: List[nn.Module] = []
        prev = input_dim
        for i, h in enumerate(hidden_dims):
            layers.append(nn.Linear(prev, h))
            layers.append(nn.ReLU())
            # Dropout only after the first hidden layer (matches the diagram)
            if i == 0:
                layers.append(nn.Dropout(dropout))
            prev = h
        layers.append(nn.Linear(prev, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Returns raw logits (no sigmoid). Use BCEWithLogitsLoss during training."""
        return self.net(x).squeeze(1)

    def predict_proba(self, X: np.ndarray, device: str = "cpu") -> np.ndarray:
        """Returns class probabilities via sigmoid — matches the diagram output."""
        self.eval()
        with torch.no_grad():
            t = torch.tensor(X, dtype=torch.float32).to(device)
            logits = self.forward(t).cpu().numpy()
        probs = torch.sigmoid(torch.tensor(logits)).numpy()
        return np.stack([1 - probs, probs], axis=1)

    def predict(self, X: np.ndarray, device: str = "cpu", threshold: float = 0.5) -> np.ndarray:
        return (self.predict_proba(X, device)[:, 1] >= threshold).astype(int)
