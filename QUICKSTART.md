# 🚀 EgySentiment Quick Start Guide

## Phase 2.5: Hybrid Training Pipeline

This guide covers how to run the automated data pipeline and perform hybrid fine-tuning.

### 1. Start the Automated Pipeline
The pipeline collects data, deduplicates it, and saves it to `data/testing_data.jsonl`.

```bash
# Start Airflow and Scraper
docker-compose up -d

# (Optional) Trigger a manual run immediately
docker-compose exec airflow-scheduler airflow dags trigger egy_sentiment_daily_collection
```

### 2. Monitor Progress
Check the dataset size (growing every 4 hours):
```bash
wc -l data/testing_data.jsonl
```

### 3. Fine-Tuning (Hybrid Strategy)
We use a **Hybrid Training** approach to fix domain mismatch.

1.  **Download Files:**
    *   `fine_tune.ipynb` (Updated notebook)
    *   `data/testing_data.jsonl` (Your local Egyptian data)

2.  **Upload to Google Colab:**
    *   Upload both files to the files section in Colab.

3.  **Run the Notebook:**
    *   The notebook will automatically:
        *   Load `Financial PhraseBank` (General Finance).
        *   Load `testing_data.jsonl` (Local Egyptian).
        *   Split Local Data: 50% for Training (Mixed), 50% for Testing.
        *   Fine-tune Llama 3.1-8B.
        *   Evaluate on the unseen Egyptian test set.

### 4. Expected Results
*   **Recall:** >70% on Positive/Negative classes.
*   **Bias:** Reduced "Neutral" over-prediction.

---
**Troubleshooting:**
*   **DAG Failed?** Check logs: `docker-compose logs -f airflow-scheduler`
*   **No Data?** Ensure `GROQ_API_KEY` is set in `.env`.
