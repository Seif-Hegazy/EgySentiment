# System Architecture

## Overview
EgySentiment is a modular NLP system designed for the Egyptian financial market. It operates in three distinct phases: **Data Engineering**, **Model Development**, and **Production Inference**.

## 1. High-Level Diagram

```mermaid
graph TD
    subgraph "Data Engineering (Airflow)"
        A[RSS Feeds] -->|Fetch| B(Data Pipeline)
        C[Web Scrapers] -->|Scrape| B
        B -->|Deduplicate| D{New Article?}
        D -->|Yes| E[Pre-processing]
        D -->|No| F[Discard]
    end

    subgraph "Inference Engine (Local)"
        E -->|JSON Payload| G[Ollama API]
        G -->|Llama 3.1 Model| H[Sentiment Analysis]
        H -->|JSON Response| I[Feature Store (CSV)]
    end

    subgraph "User Interface (Streamlit)"
        I -->|Load Features| J[Batch Processor]
        K[User Input] -->|Real-time| G
        J -->|Export| L[Forecasting Model]
        K -->|Visualize| M[Dashboard]
    end
```

## 2. Component Details

### A. Data Engineering Module
*   **Orchestrator:** Apache Airflow (Dockerized).
*   **Schedule:** Runs every 4 hours.
*   **Sources:** 14+ Egyptian financial news outlets (Daily News Egypt, Enterprise, etc.).
*   **Logic:**
    1.  **Collection:** Fetches latest news via RSS and direct scraping.
    2.  **Deduplication:** Checks URL hashes against existing database.
    3.  **Cleaning:** Removes HTML tags and irrelevant metadata.

### B. The Model (EgySentiment-Llama3.1)
*   **Base Architecture:** Llama 3.1 8B Instruct.
*   **Fine-Tuning:** QLoRA (Quantized Low-Rank Adaptation).
*   **Dataset:** Hybrid mix of Financial PhraseBank (General) and Local Egyptian News (Domain-Specific).
*   **Quantization:** 4-bit (GGUF format) for optimized Apple Silicon inference.
*   **Context Window:** 8192 tokens.

### C. Inference & Application
*   **Backend:** Ollama (Local API).
*   **Frontend:** Streamlit.
*   **Features:**
    *   **Real-time Analysis:** Instant sentiment scoring for ad-hoc news.
    *   **Batch Processing:** Bulk scoring for historical datasets.
    *   **Smart Filtering:** Keyword-based filtering for specific EGX stocks.

## 3. Data Flow

### Input Data (Raw News)
```json
{
  "date": "2024-11-30",
  "source": "Enterprise",
  "text": "CIB reports a 25% increase in net income..."
}
```

### Model Output (Sentiment Feature)
```json
{
  "sentiment": "positive",
  "sentiment_score": 1,
  "reasoning": "Significant increase in net income indicates strong financial performance."
}
```

## 4. Technology Stack
*   **Language:** Python 3.9+
*   **Containerization:** Docker & Docker Compose
*   **ML Ops:** Apache Airflow, MLflow (optional)
*   **LLM Runtime:** Ollama
*   **UI Framework:** Streamlit
*   **Data Analysis:** Pandas, Plotly, yfinance
