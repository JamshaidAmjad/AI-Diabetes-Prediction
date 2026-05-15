"""Generate the 3-page project report as a DOCX file."""

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGS = os.path.join(BASE, "outputs", "figures")
OUT  = os.path.join(BASE, "outputs", "reports")
os.makedirs(OUT, exist_ok=True)


def set_font(run, name="Calibri", size=11, bold=False, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)


def add_heading(doc, text, level=1, size=13, color=(31, 73, 125)):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    set_font(run, size=size, bold=True, color=color)
    return p


def add_body(doc, text, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(0)
    run = p.add_run(text)
    set_font(run, size=10.5)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    return p


def add_caption(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(8)
    run = p.add_run(text)
    set_font(run, size=9, color=(89, 89, 89))
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER


def set_cell_bg(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def build_report():
    doc = Document()

    # --- Narrow margins ---
    for section in doc.sections:
        section.top_margin    = Inches(0.85)
        section.bottom_margin = Inches(0.85)
        section.left_margin   = Inches(1.0)
        section.right_margin  = Inches(1.0)

    # ── TITLE BLOCK ──────────────────────────────────────────────────────────
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_p.paragraph_format.space_after = Pt(4)
    r = title_p.add_run("Early Diabetes Prediction Using Machine Learning:\nA Medical Decision Support System")
    set_font(r, size=15, bold=True, color=(31, 73, 125))

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_p.paragraph_format.space_after = Pt(2)
    r2 = sub_p.add_run("Jamshaid Amjad  |  AI in Healthcare — Capstone Project  |  May 2026")
    set_font(r2, size=10, color=(89, 89, 89))

    doc.add_paragraph().paragraph_format.space_after = Pt(2)

    # ── ABSTRACT ─────────────────────────────────────────────────────────────
    add_heading(doc, "Abstract", size=11)
    add_body(doc,
        "Diabetes mellitus is a chronic metabolic disorder affecting over 500 million people globally. "
        "Early identification of at-risk individuals is critical for timely intervention and improved "
        "outcomes. This project develops and evaluates a machine learning pipeline for binary diabetes "
        "classification using the Pima Indians Diabetes Dataset. Three complementary models — Logistic "
        "Regression, Random Forest, and a Multilayer Perceptron (MLP) — are trained on clinically "
        "relevant features and compared on a held-out test set. The MLP achieves the highest ROC-AUC "
        "of 0.875, while Logistic Regression attains the best F1 score of 0.683. Results suggest that "
        "ensemble and neural models generalise well, with Glucose and BMI consistently identified as "
        "the most discriminative features.")

    # ── 1. INTRODUCTION ──────────────────────────────────────────────────────
    add_heading(doc, "1. Introduction")
    add_body(doc,
        "Diabetes affects approximately 537 million adults worldwide and is projected to rise to "
        "783 million by 2045 (IDF, 2021). Type 2 diabetes, which accounts for over 90% of cases, "
        "progresses silently and is frequently diagnosed late — after irreversible organ damage has "
        "occurred. Automated screening tools that can flag high-risk individuals from routine clinical "
        "measurements offer a cost-effective complement to clinical judgement.")
    add_body(doc,
        "This project addresses the task of binary classification: predicting whether a patient is "
        "diabetic based on eight tabular clinical features. The clinical context is primary-care "
        "screening, where a model capable of high sensitivity can prioritise patients for confirmatory "
        "testing. Three model families are compared to balance interpretability (Logistic Regression), "
        "predictive power (Random Forest), and representation learning (MLP).")

    # ── 2. METHODS ───────────────────────────────────────────────────────────
    add_heading(doc, "2. Methods")

    add_heading(doc, "2.1  Dataset & Preprocessing", size=11, color=(0, 0, 0))
    add_body(doc,
        "The Pima Indians Diabetes Dataset (NIDDK, n=768) contains eight clinical features: number of "
        "pregnancies, plasma glucose concentration, diastolic blood pressure, triceps skin-fold "
        "thickness, serum insulin, BMI, diabetes pedigree function, and age. The outcome is binary "
        "(1 = diabetic, 0 = non-diabetic). The dataset is imbalanced (65% negative, 35% positive).")
    add_body(doc,
        "The preprocessing pipeline applies the following steps, all transformers fitted exclusively "
        "on training data to prevent leakage: (1) biologically impossible zeros in Glucose, BMI, "
        "Insulin, BloodPressure, and SkinThickness are replaced with NaN; (2) a stratified 70/15/15 "
        "train-validation-test split is applied; (3) missing values are imputed with the training-set "
        "median; (4) features are standardised with StandardScaler; (5) the top-5 features are "
        "selected by averaging ANOVA F-test and Random Forest importance ranks "
        "(selected: Glucose, BMI, Insulin, Age, Pregnancies); (6) SMOTE oversampling is applied "
        "to the training set only to address class imbalance.")

    add_heading(doc, "2.2  Models", size=11, color=(0, 0, 0))
    add_body(doc,
        "Three models are trained and compared. "
        "Logistic Regression (LR) serves as an interpretable linear baseline (L-BFGS solver, "
        "max_iter=1000). "
        "Random Forest (RF) is an ensemble of 300 decision trees; hyperparameters "
        "(n_estimators, max_depth, min_samples_split, min_samples_leaf) are optimised via "
        "5-fold GridSearchCV, yielding max_depth=10, n_estimators=100. "
        "The MLP comprises two hidden layers (Dense-16 → ReLU → Dropout-0.2 → Dense-8 → ReLU → "
        "Dense-1 → Sigmoid), trained with Adam (lr=1e-3), BCEWithLogitsLoss, a ReduceLROnPlateau "
        "scheduler, and early stopping (patience=10).")

    add_heading(doc, "2.3  Evaluation", size=11, color=(0, 0, 0))
    add_body(doc,
        "Models are evaluated on the held-out test set (n=116) using accuracy, precision, recall, "
        "F1 score, and ROC-AUC. Five-fold cross-validation on the combined train+validation set "
        "is additionally reported for LR and RF to assess stability. Confusion matrices, ROC curves, "
        "and a feature importance plot are generated for interpretability.")

    # ── 3. RESULTS ───────────────────────────────────────────────────────────
    add_heading(doc, "3. Results")

    add_body(doc,
        "Table 1 summarises test-set performance across all three models. The MLP achieves the "
        "highest ROC-AUC (0.875), indicating strong probabilistic discrimination. Logistic Regression "
        "attains the best F1 score (0.683) and accuracy (0.776). All three models substantially "
        "outperform a majority-class baseline (ROC-AUC = 0.500).")

    # Results table
    table = doc.add_table(rows=5, cols=6)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    headers = ["Model", "Accuracy", "Precision", "Recall", "F1 Score", "ROC-AUC"]
    rows_data = [
        ["Logistic Regression", "0.776", "0.683", "0.683", "0.683", "0.866"],
        ["Random Forest",       "0.767", "0.694", "0.610", "0.649", "0.841"],
        ["MLP",                 "0.767", "0.675", "0.659", "0.667", "0.875"],
        ["Majority Baseline",   "0.647", "—",     "0.000", "0.000", "0.500"],
    ]

    hdr_row = table.rows[0]
    for i, h in enumerate(headers):
        cell = hdr_row.cells[i]
        set_cell_bg(cell, "1F497D")
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h)
        set_font(run, size=9.5, bold=True, color=(255, 255, 255))

    for ri, row_data in enumerate(rows_data):
        row = table.rows[ri + 1]
        bg = "DCE6F1" if ri % 2 == 0 else "FFFFFF"
        for ci, val in enumerate(row_data):
            cell = row.cells[ci]
            set_cell_bg(cell, bg)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if ci > 0 else WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(val)
            bold = ci == 0
            set_font(run, size=9.5, bold=bold)

    add_caption(doc, "Table 1. Test-set performance metrics for all three models (n=116).")

    add_body(doc,
        "Cross-validation F1 (5-fold) on the combined train+validation set yielded "
        "0.718 ± 0.029 for Logistic Regression and 0.801 ± 0.042 for Random Forest, "
        "confirming that RF generalises robustly across folds. Feature importance analysis "
        "(Figure 1) consistently identifies Glucose as the strongest predictor, followed by "
        "BMI and Age, consistent with the clinical literature.")

    # Figure: ROC curves
    roc_path = os.path.join(FIGS, "roc_curves_comparison.png")
    cmp_path = os.path.join(FIGS, "model_comparison.png")
    imp_path = os.path.join(FIGS, "feature_importance.png")

    if os.path.exists(roc_path) and os.path.exists(cmp_path):
        # Side-by-side via a 1x2 table (invisible borders)
        fig_table = doc.add_table(rows=1, cols=2)
        fig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        left_cell  = fig_table.cell(0, 0)
        right_cell = fig_table.cell(0, 1)
        for cell in [left_cell, right_cell]:
            for border in ["top", "left", "bottom", "right"]:
                tc = cell._tc
                tcPr = tc.get_or_add_tcPr()
        lp = left_cell.paragraphs[0]
        lp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        lp.add_run().add_picture(roc_path, width=Inches(2.9))
        rp = right_cell.paragraphs[0]
        rp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        rp.add_run().add_picture(cmp_path, width=Inches(2.9))
        add_caption(doc,
            "Figure 1. Left: ROC curves for all three models on the held-out test set. "
            "Right: Grouped bar chart comparing Accuracy, F1, and ROC-AUC.")

    if os.path.exists(imp_path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(imp_path, width=Inches(4.5))
        add_caption(doc, "Figure 2. Random Forest feature importances for the five selected features.")

    # ── 4. DISCUSSION & CONCLUSION ───────────────────────────────────────────
    add_heading(doc, "4. Discussion & Conclusion")
    add_body(doc,
        "All three models achieve test accuracy above 76% and ROC-AUC above 0.84, demonstrating "
        "that routine clinical measurements are sufficient for meaningful diabetes screening. "
        "The MLP's superior ROC-AUC (0.875) suggests that non-linear feature interactions "
        "contribute to discrimination, though its F1 score is comparable to Logistic Regression. "
        "The Random Forest's strong cross-validation performance (CV F1 = 0.801) indicates "
        "robust generalisation despite a slightly lower test F1 (0.649), likely due to the "
        "small test set size (n=116).")
    add_body(doc,
        "Glucose and BMI emerge as the most informative features across all methods, consistent "
        "with clinical guidelines that use fasting plasma glucose and body-mass index as primary "
        "diabetes risk indicators. Insulin and SkinThickness, despite high missingness (~30–49%), "
        "remain in the selected feature set, suggesting that even partially observed variables "
        "carry predictive signal after median imputation.")
    add_body(doc,
        "Limitations include the small, demographically homogeneous dataset (Pima women only), "
        "which limits external validity. Future work should validate on larger, diverse cohorts, "
        "explore uncertainty quantification (e.g., calibration curves), and incorporate "
        "additional clinical features such as HbA1c. Deploying such a model in practice would "
        "require prospective validation and careful attention to fairness across demographic groups.")
    add_body(doc,
        "In conclusion, this project demonstrates that a well-engineered machine learning "
        "pipeline — combining principled preprocessing, feature selection, class-imbalance "
        "correction, and hyperparameter tuning — can produce clinically useful diabetes "
        "screening predictions from standard tabular data.", space_after=8)

    # ── REFERENCES ───────────────────────────────────────────────────────────
    add_heading(doc, "References", size=11)
    refs = [
        "International Diabetes Federation (2021). IDF Diabetes Atlas, 10th edition. Brussels, Belgium.",
        "Smith, J.W. et al. (1988). Using the ADAP learning algorithm to forecast the onset of diabetes mellitus. "
        "Proceedings of the Annual Symposium on Computer Application in Medical Care, 261–265.",
        "Chawla, N.V. et al. (2002). SMOTE: Synthetic minority over-sampling technique. "
        "Journal of Artificial Intelligence Research, 16, 321–357.",
        "Pedregosa, F. et al. (2011). Scikit-learn: Machine learning in Python. "
        "Journal of Machine Learning Research, 12, 2825–2830.",
        "Paszke, A. et al. (2019). PyTorch: An imperative style, high-performance deep learning library. "
        "NeurIPS, 32.",
    ]
    for ref in refs:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after = Pt(3)
        run = p.add_run(ref)
        set_font(run, size=9.5)

    out_path = os.path.join(OUT, "report.docx")
    doc.save(out_path)
    print(f"Saved: {out_path}")
    return out_path


if __name__ == "__main__":
    build_report()
