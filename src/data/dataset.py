"""Dataset placeholders for chest X-ray classification."""

from typing import Optional

from torch.utils.data import Dataset


class ChestXrayDataset(Dataset):
    """
    Minimal dataset skeleton.

    Responsibility:
    - Read image paths and labels.
    - Load and transform chest X-ray images.
    - Return (image, label) pairs.
    """

    def __init__(self, annotations_file: str, image_dir: str, transform: Optional[object] = None):
        self.annotations_file = annotations_file
        self.image_dir = image_dir
        self.transform = transform

        # TODO: Load annotation metadata into memory (e.g., from CSV).
        self.samples = []

    def __len__(self) -> int:
        # TODO: Return number of samples.
        return len(self.samples)

    def __getitem__(self, idx: int):
        # TODO: Implement image reading and label extraction.
        # Expected output format: image_tensor, label_int
        raise NotImplementedError("Dataset loading logic not implemented yet.")

