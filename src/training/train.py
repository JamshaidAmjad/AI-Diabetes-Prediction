"""Training pipeline for all three diabetes prediction models."""

import pickle
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import yaml

from src.data.dataset import build_dataset
from src.models.model import MLP, build_logistic_regression, build_random_forest
from src.utils import set_seed, plot_training_history


def load_config(config_path: str = "config/config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def train_sklearn_model(model, X_train: np.ndarray, y_train: np.ndarray):
    """Fit a scikit-learn estimator and return it."""
    model.fit(X_train, y_train)
    return model


def train_mlp(
    model: MLP,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    epochs: int = 50,
    batch_size: int = 32,
    lr: float = 1e-3,
    patience: int = 10,
    device: str = "cpu",
    model_path: str = "outputs/models/mlp_best.pt",
) -> dict:
    """
    Train MLP with early stopping on validation loss.
    Returns training history dict: {train_loss, val_loss, train_acc, val_acc}.
    """
    model = model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.BCEWithLogitsLoss()
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=5
    )

    train_ds = TensorDataset(
        torch.tensor(X_train, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.float32),
    )
    val_ds = TensorDataset(
        torch.tensor(X_val, dtype=torch.float32),
        torch.tensor(y_val, dtype=torch.float32),
    )
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size)

    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    best_val_loss = float("inf")
    no_improve = 0

    for epoch in range(epochs):
        model.train()
        t_loss, t_correct = 0.0, 0
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            optimizer.zero_grad()
            logits = model(X_batch)
            loss = criterion(logits, y_batch)
            loss.backward()
            optimizer.step()
            t_loss += loss.item() * len(y_batch)
            t_correct += ((logits > 0) == y_batch.bool()).sum().item()

        model.eval()
        v_loss, v_correct = 0.0, 0
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch, y_batch = X_batch.to(device), y_batch.to(device)
                logits = model(X_batch)
                v_loss += criterion(logits, y_batch).item() * len(y_batch)
                v_correct += ((logits > 0) == y_batch.bool()).sum().item()

        n_train, n_val = len(train_ds), len(val_ds)
        history["train_loss"].append(t_loss / n_train)
        history["val_loss"].append(v_loss / n_val)
        history["train_acc"].append(t_correct / n_train)
        history["val_acc"].append(v_correct / n_val)

        scheduler.step(v_loss / n_val)

        if v_loss < best_val_loss:
            best_val_loss = v_loss
            no_improve = 0
            Path(model_path).parent.mkdir(parents=True, exist_ok=True)
            torch.save(model.state_dict(), model_path)
        else:
            no_improve += 1
            if no_improve >= patience:
                print(f"Early stopping at epoch {epoch + 1}")
                break

        if (epoch + 1) % 10 == 0:
            print(
                f"Epoch {epoch + 1:3d} | "
                f"train loss {history['train_loss'][-1]:.4f} acc {history['train_acc'][-1]:.4f} | "
                f"val loss   {history['val_loss'][-1]:.4f} acc {history['val_acc'][-1]:.4f}"
            )

    model.load_state_dict(torch.load(model_path, map_location=device))
    return history


def main():
    config = load_config()
    seed = config["project"]["random_seed"]
    set_seed(seed)

    for d in [
        config["outputs"]["model_dir"],
        config["outputs"]["figures_dir"],
        config["outputs"]["reports_dir"],
    ]:
        Path(d).mkdir(parents=True, exist_ok=True)

    csv_path = (
        Path(config["data"]["raw_dir"]) / config["data"]["filename"]
    )
    data = build_dataset(
        csv_path=str(csv_path),
        val_split=config["data"]["val_split"],
        test_split=config["data"]["test_split"],
        n_features=config["data"]["n_features_to_select"],
        use_smote=config["data"]["use_smote"],
        random_seed=seed,
        processed_dir=config["data"]["processed_dir"],
    )
    X_train, y_train = data["X_train"], data["y_train"]
    X_val, y_val = data["X_val"], data["y_val"]
    print(f"Features selected: {data['selected_features']}")
    print(f"Train: {X_train.shape}  Val: {X_val.shape}  Test: {data['X_test'].shape}")

    model_type = config["model"]["type"]
    model_dir = config["outputs"]["model_dir"]

    if model_type in ("logistic_regression", "all"):
        print("\n--- Logistic Regression ---")
        lr_model = train_sklearn_model(
            build_logistic_regression(seed), X_train, y_train
        )
        with open(f"{model_dir}/logistic_regression.pkl", "wb") as f:
            pickle.dump(lr_model, f)
        print("Saved logistic_regression.pkl")

    if model_type in ("random_forest", "all"):
        print("\n--- Random Forest ---")
        rf_model = train_sklearn_model(
            build_random_forest(config["model"]["rf_n_estimators"], seed),
            X_train,
            y_train,
        )
        with open(f"{model_dir}/random_forest.pkl", "wb") as f:
            pickle.dump(rf_model, f)
        print("Saved random_forest.pkl")

    if model_type in ("mlp", "all"):
        print("\n--- MLP ---")
        mlp = MLP(
            input_dim=X_train.shape[1],
            hidden_dims=config["model"]["mlp_hidden_dims"],
            dropout=config["model"]["mlp_dropout"],
        )
        history = train_mlp(
            mlp,
            X_train, y_train,
            X_val, y_val,
            epochs=config["training"]["epochs"],
            batch_size=config["training"]["batch_size"],
            lr=config["training"]["learning_rate"],
            patience=config["training"]["patience"],
            device=config["training"]["device"],
            model_path=f"{model_dir}/mlp_best.pt",
        )
        plot_training_history(
            history,
            save_path=f"{config['outputs']['figures_dir']}/mlp_training.png",
        )
        print("Saved mlp_best.pt and training curve")


if __name__ == "__main__":
    main()
