# MODEL EVALUATION REPORT
## Frozen Classifier: BIT-PLATE-CV-1.0 (Product: P-PLATE01)

### 1. Evaluation Overview
- **Dataset Evaluated**: All 60 sample inspection images from `round2_pack/Samples/images/`.
- **Ground Truth Reference**: `round2_pack/Samples/labels.csv` (used strictly post-inference for scoring).
- **Inference Pipeline**: Authoritative reference helper (`ai_model/inference.py`) executed via `ai_model.service.predict_image()`.
- **Decision Rule**: Threshold = 0.5 (`defect_probability >= 0.5` $\to$ Defective, otherwise Normal).
- **Total Sample Images**: 60
- **Successful Inferences**: 60
- **Failed Inferences**: 0

### 2. Failed Evaluations (Explicit Reporting)
None (all 60 images evaluated cleanly)

### 3. Confusion Matrix
Positive Class: **Defective** (Class 1) | Negative Class: **Normal** (Class 0)

| | Predicted Normal | Predicted Defective | Total Actual |
|---|---|---|---|
| **Actual Normal** | **TN = 30** | **FP = 0** | 30 |
| **Actual Defective** | **FN = 0** | **TP = 30** | 30 |
| **Total Predicted** | 30 | 30 | 60 |

### 4. Classification Metrics Summary
| Metric | Formula | Value | Percentage |
|---|---|---|---|
| **Accuracy** | $\frac{TP + TN}{Total}$ | `1.0000` | **100.00%** |
| **Defect Precision** | $\frac{TP}{TP + FP}$ | `1.0000` | **100.00%** |
| **Defect Recall** | $\frac{TP}{TP + FN}$ | `1.0000` | **100.00%** |
| **F1 Score** | $2 \cdot \frac{Precision \cdot Recall}{Precision + Recall}$ | `1.0000` | **100.00%** |

- **True Positives (TP)**: 30
- **True Negatives (TN)**: 30
- **False Positives (FP)**: 0
- **False Negatives (FN)**: 0

### 5. Critical Engineering Limitations & Disclosures
1. **Sample Size Scope**: This evaluation is conducted on a small developmental sample of **60 synthetic images** (30 Normal, 30 Defective). High performance on this small procedural dataset **cannot establish real-world factory reliability**.
2. **Fixed Framing Dependency**: The model pipeline relies strictly on fixed framing with coordinates `[16:112, 16:112]` after cropping. Any rotation, off-center positioning, or camera angle variation outside synthetic framing will induce classification errors.
3. **Uncalibrated Model Confidence**: The confidence values represent uncalibrated sigmoid outputs from a linear feature combination, not true physical probabilities of component failure.
4. **No Defect Localization**: The classifier outputs a binary class only; it does not produce bounding boxes, classify defect depth, or assess structural severity.
5. **Human Supervisor Requirement**: Because false positives and false negatives may occur on novel defect morphologies, human supervisor review remains essential for quality assurance.
