# User Guide

## Getting Started

### Prerequisites
Ensure the system is running:
1.  **Ollama:** Must be running in the background (`ollama serve`).
2.  **Streamlit:** Launch the app via terminal.

```bash
streamlit run src/app.py
```

## Dashboard Features

### 1. Real-Time Analysis
Use this tab for instant analysis of breaking news.

1.  **Select Market Context:** Choose a company from the sidebar (e.g., "CIB") to see its current stock price and chart.
2.  **Input News:** Paste a headline or article snippet into the text area.
3.  **Analyze:** Click the "⚡ Analyze Sentiment" button.
4.  **Result:**
    *   **Sentiment:** Positive (Green), Negative (Red), or Neutral (Purple).
    *   **Reasoning:** A brief explanation of *why* the model chose that sentiment.

### 2. Batch Processing (Forecasting)
Use this tab to generate features for your quantitative models (LSTM, XGBoost, etc.).

1.  **Upload Data:** Drag and drop your historical CSV or JSONL file.
2.  **Select Columns:**
    *   **Text Column:** Choose the column containing the news text.
    *   **Date Column (Optional):** Select the column with dates if you want time-series features.
3.  **Smart Filter (Optional):**
    *   Select a target stock (e.g., "Elsewedy Electric").
    *   The system automatically filters for relevant keywords (English & Arabic).
4.  **Aggregation (Optional):**
    *   Check **"📅 Aggregate Scores by Day?"** to calculate the mean sentiment score per day.
    *   *Best for:* Creating daily features for forecasting models (e.g., matching with daily stock prices).
5.  **Process:** Click "🚀 Start Batch Processing".
6.  **Download:** Get a CSV with `daily_sentiment_score` (if aggregated) or individual `sentiment_score` features.

## Troubleshooting

### "Model not found"
*   **Cause:** Ollama cannot find the `egysentiment` model.
*   **Fix:** Run `ollama create egysentiment -f Modelfile` in your terminal.

### "Connection Error"
*   **Cause:** Ollama is not running.
*   **Fix:** Open a new terminal and run `ollama serve`.

### "JSON Error" / "Neutral Output"
*   **Cause:** The model generated malformed output.
*   **Fix:** The system has auto-repair logic, but if it persists, try simplifying the input text.
