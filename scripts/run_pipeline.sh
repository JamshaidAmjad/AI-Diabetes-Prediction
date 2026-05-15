#!/usr/bin/env bash
# End-to-end pipeline: preprocess → train all models → evaluate
set -euo pipefail

echo "================================================="
echo " AI Diabetes Prediction — Full Pipeline"
echo "================================================="

echo ""
echo "[1/2] Training all models (includes preprocessing, CV, and hyperparameter tuning)..."
python -m src.training.train

echo ""
echo "[2/2] Evaluating on held-out test set..."
python -m src.evaluation.evaluate

echo ""
echo "================================================="
echo " Done! Results saved to:"
echo "   outputs/models/     — trained model files"
echo "   outputs/figures/    — all plots (ROC, confusion matrices, comparison)"
echo "   outputs/reports/    — evaluation_results.json, cv_results.json"
echo "================================================="
