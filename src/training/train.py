"""Starter training script skeleton."""

from pathlib import Path

import yaml

from src.models.model import ChestXrayClassifier


def load_config(config_path: str = "config/config.yaml") -> dict:
    """Load YAML configuration file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def train_one_epoch():
    """
    Placeholder for one epoch of training.

    TODO:
    - Iterate over dataloader.
    - Forward pass, loss, backward pass, optimizer step.
    """
    pass


def main():
    """Project training entry point (placeholder)."""
    config = load_config()

    # Create output directory if it does not exist.
    Path(config["outputs"]["model_dir"]).mkdir(parents=True, exist_ok=True)

    # Initialize placeholder model.
    model = ChestXrayClassifier(
        num_classes=config["data"]["num_classes"],
        backbone=config["model"]["backbone"],
        pretrained=config["model"]["pretrained"],
    )

    # TODO: Add dataset, dataloader, loss function, optimizer, scheduler, and loop.
    print("Training scaffold ready. Implement training pipeline in this module.")
    _ = model


if __name__ == "__main__":
    main()

