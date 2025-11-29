# 📊 Model Performance Analysis: Transfer Learning (Run 1)

**Date:** November 29, 2025
**Model:** Llama-3-8B (Fine-tuned on Financial PhraseBank)
**Test Set:** Egyptian Financial News (Local Data)

## 1. Executive Summary
*   **Overall Accuracy:** **53%** (Moderate)
*   **Key Strength:** **High Precision** for Positive (88%) and Negative (84%). When the model predicts a sentiment, it is highly reliable.
*   **Key Weakness:** **Low Recall** for Positive (46%). The model is overly conservative and "plays it safe" by predicting **Neutral** too often.
*   **Diagnosis:** **Domain Mismatch**. The "Financial PhraseBank" likely contains shorter, more direct sentences, whereas Egyptian news articles are longer and more nuanced. The model struggles to detect the "Positive" signal in the longer Egyptian text and defaults to "Neutral".

## 2. Detailed Metrics

| Class | Precision | Recall | F1-Score | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Positive** | **0.88** (Excellent) | **0.46** (Poor) | 0.60 | ⚠️ Misses 54% of positive news (classified as Neutral) |
| **Neutral** | 0.25 (Low) | **0.72** (High) | 0.37 | ⚠️ Over-predicted (Hallucinates neutrality) |
| **Negative** | **0.84** (Great) | **0.76** (Good) | **0.80** | ✅ Performing well! |

## 3. Confusion Matrix Analysis
*   **Positive Samples (200 total):**
    *   ✅ 91 Correctly identified.
    *   ❌ **108 Misclassified as Neutral** (The biggest issue).
    *   ❌ 1 Misclassified as Negative.
*   **Neutral Samples (53 total):**
    *   ✅ 38 Correctly identified.
    *   ❌ 13 Misclassified as Positive.
*   **Negative Samples (21 total):**
    *   ✅ 16 Correctly identified.
    *   ❌ 5 Misclassified as Neutral.

## 4. Recommendations for Phase 2.5 (Improvement)

To fix the "Positive -> Neutral" bias, we need to teach the model the *style* of Egyptian news.

### 🚀 Strategy: Hybrid Training
Instead of training *only* on PhraseBank, we should mix in a small portion of your local data.

1.  **Split Local Data:** Take 50% of your `training_data.jsonl` for **Training** and keep 50% for **Testing**.
2.  **Combine Datasets:** Train on `[Financial PhraseBank + Local Train]`.
3.  **Benefit:** The model learns general finance from PhraseBank AND the specific length/style of Egyptian news from your local data.

**Expected Outcome:** Recall for Positive should increase significantly (likely >70%).
