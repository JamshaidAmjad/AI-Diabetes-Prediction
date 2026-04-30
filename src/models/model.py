"""Model placeholders for CNN and transfer learning."""

import torch.nn as nn


class ChestXrayClassifier(nn.Module):
    """
    Minimal model skeleton.

    Responsibility:
    - Define CNN or transfer learning architecture.
    - Expose a forward pass for training/evaluation scripts.
    """

    def __init__(self, num_classes: int = 3, backbone: str = "resnet18", pretrained: bool = True):
        super().__init__()
        self.num_classes = num_classes
        self.backbone = backbone
        self.pretrained = pretrained

        # TODO: Initialize model layers or pretrained backbone.
        self.network = None

    def forward(self, x):
        # TODO: Return logits from the model.
        raise NotImplementedError("Model forward pass not implemented yet.")

