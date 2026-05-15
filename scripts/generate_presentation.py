"""Generate the flash-talk PowerPoint presentation."""

import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGS = os.path.join(BASE, "outputs", "figures")
OUT  = os.path.join(BASE, "outputs", "reports")
os.makedirs(OUT, exist_ok=True)

# ── Colour palette ────────────────────────────────────────────────────────────
DARK_BLUE  = RGBColor(0x1F, 0x49, 0x7D)   # headers / title bg
MID_BLUE   = RGBColor(0x2E, 0x75, 0xB6)   # accent
LIGHT_BLUE = RGBColor(0xDC, 0xE6, 0xF1)   # row alt / box bg
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
DARK_GREY  = RGBColor(0x40, 0x40, 0x40)
RED_ACCENT = RGBColor(0xC0, 0x00, 0x00)

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)


def new_prs():
    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H
    return prs


def blank_slide(prs):
    layout = prs.slide_layouts[6]   # completely blank
    return prs.slides.add_slide(layout)


def add_rect(slide, left, top, width, height, fill_color, line_color=None):
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if line_color:
        shape.line.color.rgb = line_color
    else:
        shape.line.fill.background()
    return shape


def add_textbox(slide, text, left, top, width, height,
                font_size=18, bold=False, color=WHITE,
                align=PP_ALIGN.LEFT, wrap=True, italic=False):
    txb = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    txb.word_wrap = wrap
    tf = txb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return txb


def add_picture_safe(slide, path, left, top, width=None, height=None):
    if os.path.exists(path):
        pic = slide.shapes.add_picture(path, Inches(left), Inches(top),
                                       width=Inches(width) if width else None,
                                       height=Inches(height) if height else None)
        return pic
    return None


def header_bar(slide, title, subtitle=None):
    """Dark-blue header bar across the top."""
    add_rect(slide, 0, 0, 13.33, 1.1, DARK_BLUE)
    add_textbox(slide, title, 0.3, 0.08, 12.0, 0.65,
                font_size=28, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
    if subtitle:
        add_textbox(slide, subtitle, 0.3, 0.72, 12.0, 0.32,
                    font_size=13, bold=False, color=LIGHT_BLUE, align=PP_ALIGN.LEFT)


def footer_bar(slide, text="Jamshaid Amjad  |  AI in Healthcare Capstone  |  May 2026"):
    add_rect(slide, 0, 7.18, 13.33, 0.32, DARK_BLUE)
    add_textbox(slide, text, 0.2, 7.2, 13.0, 0.28,
                font_size=9, color=LIGHT_BLUE, align=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — Title
# ═══════════════════════════════════════════════════════════════════════════════
def slide_title(prs):
    sl = blank_slide(prs)
    # full-bleed background
    add_rect(sl, 0, 0, 13.33, 7.5, DARK_BLUE)
    # lighter accent band
    add_rect(sl, 0, 5.2, 13.33, 2.3, MID_BLUE)

    add_textbox(sl,
        "Early Diabetes Prediction\nUsing Machine Learning",
        0.6, 1.3, 12.0, 2.2,
        font_size=40, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    add_textbox(sl,
        "A Medical Decision Support System",
        0.6, 3.4, 12.0, 0.6,
        font_size=20, bold=False, color=LIGHT_BLUE, align=PP_ALIGN.CENTER, italic=True)

    add_textbox(sl,
        "Jamshaid Amjad",
        0.6, 5.4, 12.0, 0.5,
        font_size=18, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    add_textbox(sl,
        "AI in Healthcare — Capstone Project  |  May 2026",
        0.6, 5.9, 12.0, 0.4,
        font_size=13, bold=False, color=LIGHT_BLUE, align=PP_ALIGN.CENTER)

    add_textbox(sl,
        "Dataset: Pima Indians Diabetes (n=768)  |  Models: Logistic Regression, Random Forest, MLP",
        0.6, 6.5, 12.0, 0.4,
        font_size=11, bold=False, color=LIGHT_BLUE, align=PP_ALIGN.CENTER, italic=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — Problem & Dataset
# ═══════════════════════════════════════════════════════════════════════════════
def slide_problem(prs):
    sl = blank_slide(prs)
    add_rect(sl, 0, 0, 13.33, 7.5, WHITE)
    header_bar(sl, "Problem & Dataset", "Why does early diabetes detection matter?")
    footer_bar(sl)

    # Left column — clinical context
    add_rect(sl, 0.3, 1.25, 5.8, 5.6, LIGHT_BLUE)
    add_textbox(sl, "Clinical Motivation", 0.5, 1.35, 5.4, 0.45,
                font_size=14, bold=True, color=DARK_BLUE)

    bullets = [
        "537M adults have diabetes globally (IDF 2021)",
        "Type 2 diabetes progresses silently — often diagnosed late",
        "Early screening from routine blood tests = cost-effective prevention",
        "Task: predict diabetes risk from 8 clinical measurements",
        "Clinical setting: primary-care screening tool",
    ]
    top = 1.85
    for b in bullets:
        add_textbox(sl, f"•  {b}", 0.55, top, 5.3, 0.55, font_size=12, color=DARK_GREY)
        top += 0.57

    # Right column — dataset facts
    add_rect(sl, 6.8, 1.25, 6.2, 5.6, LIGHT_BLUE)
    add_textbox(sl, "Pima Indians Diabetes Dataset", 7.0, 1.35, 5.8, 0.45,
                font_size=14, bold=True, color=DARK_BLUE)

    facts = [
        ("Samples",         "768 patients"),
        ("Features",        "8 clinical variables"),
        ("Target",          "Binary (0=No, 1=Yes)"),
        ("Class ratio",     "65% negative / 35% positive"),
        ("Missing data",    "Encoded as biological zeros"),
        ("Source",          "NIDDK / UCI Repository"),
    ]
    top = 1.85
    for label, val in facts:
        add_textbox(sl, label, 7.05, top, 2.3, 0.42, font_size=11, bold=True, color=DARK_BLUE)
        add_textbox(sl, val,   9.3,  top, 3.5, 0.42, font_size=11, color=DARK_GREY)
        top += 0.52

    add_picture_safe(sl, os.path.join(FIGS, "class_distribution.png"),
                     left=7.3, top=5.1, width=5.4)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — Methods Pipeline
# ═══════════════════════════════════════════════════════════════════════════════
def slide_methods(prs):
    sl = blank_slide(prs)
    add_rect(sl, 0, 0, 13.33, 7.5, WHITE)
    header_bar(sl, "Methods", "End-to-end ML pipeline with leakage-free preprocessing")
    footer_bar(sl)

    # Pipeline steps as connected boxes
    steps = [
        ("1. Load &\nClean",      "Replace bio-\nimpossible zeros\nwith NaN"),
        ("2. Split",              "Stratified\n70 / 15 / 15\ntrain-val-test"),
        ("3. Impute",             "Median imputation\n(fit on train\nonly)"),
        ("4. Scale",              "StandardScaler\n(fit on train\nonly)"),
        ("5. Feature\nSelection", "Top-5 by ANOVA\n+ RF rank:\nGlucose, BMI…"),
        ("6. SMOTE",              "Oversample\nminority class\n(train only)"),
    ]

    box_w = 1.85
    gap   = 0.25
    start = 0.25
    top_title = 1.25
    top_desc  = 1.85

    for i, (title, desc) in enumerate(steps):
        x = start + i * (box_w + gap)
        add_rect(sl, x, top_title, box_w, 0.55, DARK_BLUE)
        add_textbox(sl, title, x + 0.05, top_title + 0.04, box_w - 0.1, 0.5,
                    font_size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_rect(sl, x, top_desc, box_w, 1.55, LIGHT_BLUE)
        add_textbox(sl, desc, x + 0.05, top_desc + 0.1, box_w - 0.1, 1.4,
                    font_size=10, color=DARK_GREY, align=PP_ALIGN.CENTER)
        # Arrow (except after last)
        if i < len(steps) - 1:
            ax = x + box_w + 0.02
            add_textbox(sl, "▶", ax, top_title + 0.08, 0.22, 0.4,
                        font_size=14, color=MID_BLUE, align=PP_ALIGN.CENTER)

    # Models section
    add_textbox(sl, "Models Trained", 0.3, 3.65, 12.5, 0.45,
                font_size=15, bold=True, color=DARK_BLUE)

    models = [
        ("Logistic Regression",
         "Interpretable linear baseline\nL-BFGS solver, max_iter=1000\n5-fold CV reported"),
        ("Random Forest",
         "300 trees, non-linear ensemble\nGridSearchCV tuning:\nmax_depth=10, n_estimators=100"),
        ("MLP Neural Network",
         "Dense-16→ReLU→Dropout(0.2)\n→Dense-8→ReLU→Dense-1→Sigmoid\nEarly stopping, patience=10"),
    ]
    mw = 3.9
    for i, (name, desc) in enumerate(models):
        x = 0.3 + i * (mw + 0.3)
        add_rect(sl, x, 4.15, mw, 0.48, MID_BLUE)
        add_textbox(sl, name, x + 0.1, 4.17, mw - 0.2, 0.44,
                    font_size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_rect(sl, x, 4.63, mw, 1.9, LIGHT_BLUE)
        add_textbox(sl, desc, x + 0.1, 4.68, mw - 0.2, 1.8,
                    font_size=11, color=DARK_GREY, align=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — Results
# ═══════════════════════════════════════════════════════════════════════════════
def slide_results(prs):
    sl = blank_slide(prs)
    add_rect(sl, 0, 0, 13.33, 7.5, WHITE)
    header_bar(sl, "Results", "Test-set evaluation (n=116 held-out samples)")
    footer_bar(sl)

    # Metrics table
    headers = ["Model", "Accuracy", "Precision", "Recall", "F1 Score", "ROC-AUC"]
    data = [
        ["Logistic Regression", "0.776", "0.683", "0.683", "0.683", "0.866"],
        ["Random Forest",       "0.767", "0.694", "0.610", "0.649", "0.841"],
        ["MLP",                 "0.767", "0.675", "0.659", "0.667", "0.875 ★"],
    ]

    col_widths = [2.6, 1.45, 1.45, 1.3, 1.45, 1.65]
    row_h = 0.48
    t_left = 0.3
    t_top  = 1.25

    # header row
    x = t_left
    for i, (h, w) in enumerate(zip(headers, col_widths)):
        add_rect(sl, x, t_top, w, row_h, DARK_BLUE)
        add_textbox(sl, h, x + 0.05, t_top + 0.08, w - 0.1, row_h - 0.1,
                    font_size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        x += w

    for ri, row in enumerate(data):
        bg = LIGHT_BLUE if ri % 2 == 0 else WHITE
        x = t_left
        for ci, (val, w) in enumerate(zip(row, col_widths)):
            add_rect(sl, x, t_top + (ri + 1) * row_h, w, row_h, bg)
            bold = ci == 0
            add_textbox(sl, val, x + 0.05,
                        t_top + (ri + 1) * row_h + 0.08,
                        w - 0.1, row_h - 0.1,
                        font_size=12, bold=bold, color=DARK_GREY,
                        align=PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER)
            x += w

    add_textbox(sl, "★ Highest ROC-AUC", 10.5, t_top + 4 * row_h - 0.05, 2.5, 0.35,
                font_size=10, italic=True, color=MID_BLUE)

    # CV results
    add_textbox(sl, "5-Fold Cross-Validation F1 (train + val set)",
                0.3, t_top + 3.6 * row_h, 8.0, 0.42,
                font_size=13, bold=True, color=DARK_BLUE)

    cv_data = [
        ("Logistic Regression", "0.718", "±0.029"),
        ("Random Forest",       "0.801", "±0.042"),
    ]
    cv_top = t_top + 4.1 * row_h
    cv_headers = ["Model", "CV F1 Mean", "CV F1 Std"]
    cv_widths   = [3.2, 2.2, 2.0]

    x = 0.3
    for h, w in zip(cv_headers, cv_widths):
        add_rect(sl, x, cv_top, w, 0.40, MID_BLUE)
        add_textbox(sl, h, x + 0.05, cv_top + 0.06, w - 0.1, 0.30,
                    font_size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        x += w

    for ri, (name, mean, std) in enumerate(cv_data):
        bg = LIGHT_BLUE if ri % 2 == 0 else WHITE
        x = 0.3
        for val, w in zip([name, mean, std], cv_widths):
            add_rect(sl, x, cv_top + (ri + 1) * 0.4, w, 0.40, bg)
            add_textbox(sl, val, x + 0.05, cv_top + (ri + 1) * 0.4 + 0.07,
                        w - 0.1, 0.30, font_size=11,
                        color=DARK_GREY,
                        align=PP_ALIGN.LEFT if val == name else PP_ALIGN.CENTER)
            x += w

    # Key finding callout
    add_rect(sl, 8.0, cv_top - 0.05, 5.0, 1.5, LIGHT_BLUE)
    add_textbox(sl, "Key Findings",
                8.15, cv_top, 4.7, 0.38,
                font_size=12, bold=True, color=DARK_BLUE)
    findings = (
        "• MLP achieves best ROC-AUC (0.875)\n"
        "• LR achieves best F1 (0.683)\n"
        "• RF most stable across CV folds\n"
        "• All models >> random baseline (0.500)"
    )
    add_textbox(sl, findings, 8.15, cv_top + 0.40, 4.7, 1.05,
                font_size=11, color=DARK_GREY)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — Visualisations
# ═══════════════════════════════════════════════════════════════════════════════
def slide_visuals(prs):
    sl = blank_slide(prs)
    add_rect(sl, 0, 0, 13.33, 7.5, WHITE)
    header_bar(sl, "Visualisations", "ROC curves, model comparison, and feature importance")
    footer_bar(sl)

    roc_path = os.path.join(FIGS, "roc_curves_comparison.png")
    cmp_path = os.path.join(FIGS, "model_comparison.png")
    imp_path = os.path.join(FIGS, "feature_importance.png")

    add_picture_safe(sl, roc_path, left=0.2,  top=1.2, width=5.8)
    add_picture_safe(sl, cmp_path, left=6.2,  top=1.2, width=6.9)
    add_picture_safe(sl, imp_path, left=2.0,  top=4.7, width=9.0)

    add_textbox(sl, "ROC Curve Comparison", 0.2, 5.55, 5.8, 0.35,
                font_size=10, italic=True, color=DARK_GREY, align=PP_ALIGN.CENTER)
    add_textbox(sl, "Accuracy / F1 / ROC-AUC by Model", 6.2, 5.55, 6.9, 0.35,
                font_size=10, italic=True, color=DARK_GREY, align=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — Conclusion
# ═══════════════════════════════════════════════════════════════════════════════
def slide_conclusion(prs):
    sl = blank_slide(prs)
    add_rect(sl, 0, 0, 13.33, 7.5, WHITE)
    header_bar(sl, "Conclusion & Clinical Relevance",
               "What this means for real-world diabetes screening")
    footer_bar(sl)

    # Left — conclusions
    add_rect(sl, 0.3, 1.25, 6.0, 5.55, LIGHT_BLUE)
    add_textbox(sl, "Conclusions", 0.5, 1.35, 5.6, 0.45,
                font_size=15, bold=True, color=DARK_BLUE)

    conclusions = [
        "All 3 models achieve ROC-AUC > 0.84 from\nroutine blood tests alone",
        "Glucose & BMI are the strongest predictors\n— consistent with clinical guidelines",
        "MLP best for probabilistic triage (AUC 0.875);\nLR best for interpretable decisions (F1 0.683)",
        "SMOTE + feature selection + hyperparameter\ntuning all contribute to performance",
        "Pipeline is fully reproducible: one command\nreproduces all results",
    ]
    top = 1.9
    for c in conclusions:
        add_rect(sl, 0.45, top, 0.25, 0.25, MID_BLUE)
        add_textbox(sl, c, 0.8, top - 0.05, 5.3, 0.65, font_size=11, color=DARK_GREY)
        top += 0.75

    # Right — limitations & future work
    add_rect(sl, 6.8, 1.25, 6.2, 2.55, LIGHT_BLUE)
    add_textbox(sl, "Limitations", 7.0, 1.35, 5.8, 0.45,
                font_size=15, bold=True, color=RED_ACCENT)

    lims = [
        "Small, demographically narrow dataset (Pima women only)",
        "High missingness in Insulin (~49%) and SkinThickness (~30%)",
        "No prospective or external validation performed",
    ]
    top = 1.9
    for l in lims:
        add_textbox(sl, f"⚠  {l}", 7.0, top, 5.8, 0.55, font_size=11, color=DARK_GREY)
        top += 0.6

    add_rect(sl, 6.8, 3.9, 6.2, 2.9, LIGHT_BLUE)
    add_textbox(sl, "Future Work", 7.0, 4.0, 5.8, 0.45,
                font_size=15, bold=True, color=DARK_BLUE)

    future = [
        "Validate on larger, diverse multi-ethnic cohorts",
        "Add calibration curves for uncertainty quantification",
        "Incorporate HbA1c, fasting glucose, family history",
        "Fairness audit across age / sex subgroups",
    ]
    top = 4.55
    for f in future:
        add_textbox(sl, f"→  {f}", 7.0, top, 5.8, 0.52, font_size=11, color=DARK_GREY)
        top += 0.54

    # Thank you strip
    add_rect(sl, 0.3, 6.78, 12.7, 0.3, MID_BLUE)
    add_textbox(sl, "Thank you  |  Questions?  |  Code: github.com/JamshaidAmjad/AI-Diabetes-Prediction",
                0.4, 6.8, 12.5, 0.28,
                font_size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════════════════════════
def build_presentation():
    prs = new_prs()
    slide_title(prs)
    slide_problem(prs)
    slide_methods(prs)
    slide_results(prs)
    slide_visuals(prs)
    slide_conclusion(prs)

    out_path = os.path.join(OUT, "presentation.pptx")
    prs.save(out_path)
    print(f"Saved: {out_path}")
    return out_path


if __name__ == "__main__":
    build_presentation()
