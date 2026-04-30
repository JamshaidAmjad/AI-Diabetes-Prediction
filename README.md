# AI Medical X-ray Classification

## Project Overview
This repository is a team scaffold for a Master's-level **AI in Healthcare** project.
The goal is to build a medical decision support system for chest X-ray image classification.

## Problem Statement
We aim to classify chest X-ray images into three classes:
- `COVID-19`
- `Viral Pneumonia`
- `Normal`

This project will explore deep learning approaches suitable for healthcare imaging tasks.

## Planned Modeling Approach
- Baseline Convolutional Neural Network (CNN)
- Transfer Learning with pretrained CNN backbones (PyTorch)

## Repository Structure
```text
project-root/
|
|-- data/
|   |-- raw/
|   `-- processed/
|
|-- notebooks/
|
|-- src/
|   |-- data/
|   |   `-- dataset.py
|   |-- models/
|   |   `-- model.py
|   |-- training/
|   |   `-- train.py
|   |-- evaluation/
|   |   `-- evaluate.py
|   `-- utils/
|
|-- outputs/
|   |-- models/
|   |-- figures/
|   `-- reports/
|
|-- config/
|   `-- config.yaml
|
|-- tests/
|
|-- README.md
|-- requirements.txt
`-- .gitignore
```

## Folder Responsibilities
- `data/raw/`: Original dataset files (not committed)
- `data/processed/`: Preprocessed data artifacts
- `notebooks/`: EDA, experiments, and visual analysis
- `src/data/`: Dataset and data-loading logic
- `src/models/`: Model definitions (CNN and transfer learning wrappers)
- `src/training/`: Training entry points and loops
- `src/evaluation/`: Metrics and evaluation scripts
- `src/utils/`: Shared utility functions
- `outputs/`: Saved models, figures, and reports
- `config/`: Centralized configuration files
- `tests/`: Unit/integration test placeholders

## Quick Start (Placeholder)
1. Create and activate a Python virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Add data files to `data/raw/`.
4. Update `config/config.yaml` as needed.
5. Run placeholder training script:
   ```bash
   python -m src.training.train
   ```

## Team Notes
This scaffold is intentionally minimal so team members can implement modules in parallel.
Please keep changes modular and documented.

