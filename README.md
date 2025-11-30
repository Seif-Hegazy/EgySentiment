# EgySentiment: Egyptian Financial News Sentiment Analysis

## Overview
EgySentiment is a specialized Natural Language Processing (NLP) system designed to analyze sentiment in Egyptian financial news. It leverages a fine-tuned Large Language Model (LLM) to detect market sentiment (Positive, Negative, Neutral) from Arabic and English news sources, specifically tailored for the Egyptian Stock Exchange (EGX).

This project provides an end-to-end pipeline:
1.  **Data Collection:** Automated scraping and RSS aggregation from 14+ local sources.
2.  **Model:** A fine-tuned 8B parameter model optimized for Egyptian financial context.
3.  **Inference:** A local dashboard for real-time analysis and batch processing for forecasting models.

## Key Features
*   **Domain-Specific:** Trained on a hybrid dataset of global financial news and local Egyptian market reports.
*   **Automated Pipeline:** Daily data collection and deduplication using Apache Airflow.
*   **Local Privacy:** Runs entirely on local hardware (Apple Silicon optimized) without external API dependencies.
*   **Forecasting Ready:** Batch processing module to generate sentiment features for downstream quantitative models (LSTM/XGBoost).

## System Architecture
The system is composed of three main modules:

### 1. Data Engineering (Airflow)
*   **DAGs:** Automated daily workflows for collection and cleaning.
*   **Sources:** Daily News Egypt, Enterprise, Mubasher, and more.
*   **Storage:** JSONL format for efficient processing.

### 2. Model (Fine-Tuned LLM)
*   **Base:** Llama 3.1 8B Instruct.
*   **Training:** LoRA (Low-Rank Adaptation) with 4-bit quantization.
*   **Optimization:** Context-aware prompt engineering for financial nuance.

### 3. Application (Streamlit)
*   **Dashboard:** Real-time sentiment analysis with market data overlay (yfinance).
*   **Batch Processor:** Bulk scoring of historical data with keyword filtering for specific stocks (e.g., CIB, Ezz Steel).

## Installation

### Prerequisites
*   Python 3.9+
*   Docker & Docker Compose
*   Ollama (for local inference)

### Setup
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Seif-Hegazy/EgySentiment.git
    cd EgySentiment
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Setup Model:**
    Ensure Ollama is installed, then create the model:
    ```bash
    ollama create egysentiment -f Modelfile
    ```

4.  **Start Dashboard:**
    ```bash
    streamlit run src/app.py
    ```

## Usage

### Real-Time Analysis
Open the dashboard at `http://localhost:8501`. Paste any news article to get an instant sentiment classification and reasoning.

### Batch Processing (For Forecasting)
1.  Navigate to the **Batch Processing** tab.
2.  Upload your historical dataset (CSV/JSONL).
3.  Select a target stock (e.g., "Elsewedy Electric") to automatically filter relevant articles.
4.  Download the generated `sentiment_score` features (`1`, `0`, `-1`) for your predictive models.

## License
Private Research Project.
