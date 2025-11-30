# Developer Guide

## Extending the System

### 1. Adding New Stocks
To add support for a new company, edit `src/app.py`.

1.  Locate the `STOCK_DATA` dictionary.
2.  Add a new entry following this format:

```python
"Display Name": {
    "ticker": "TICKER.CA",  # Must be a valid Yahoo Finance ticker
    "keywords": ["English Name", "Ticker", "Arabic Name", "Alias"]
}
```

**Example:**
```python
"Domty": {
    "ticker": "DOMT.CA",
    "keywords": ["Domty", "DOMT", "Arabian Food Industries", "دومتي"]
}
```

### 2. Retraining the Model
If you gather more data and want to improve the model:

1.  **Prepare Data:** Ensure your new data is in `data/testing_data.jsonl`.
2.  **Open Notebook:** Launch `notebooks/fine_tune.ipynb`.
3.  **Run Training:** Execute the cells to fine-tune Llama 3.1.
4.  **Export GGUF:** The notebook will save the new model to `models/`.
5.  **Update Modelfile:**
    ```dockerfile
    FROM ./models/new_model_name.gguf
    ```
6.  **Re-create Model:**
    ```bash
    ollama create egysentiment -f Modelfile
    ```

### 3. Modifying the Airflow Pipeline
The DAG is defined in `dags/sentiment_collection.py`.

*   **Adding Sources:** Update `src/data_pipeline.py` to include new RSS feeds or scrapers.
*   **Changing Schedule:** Edit the `schedule_interval` in the DAG definition.

## Testing
Run the test suite to verify core functionality:

```bash
python -m unittest discover tests
```
*(Note: Ensure you create the `tests/` directory if it doesn't exist, or use the provided test script).*
