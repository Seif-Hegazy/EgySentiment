import json
import pandas as pd
import requests
import os
import time
from datetime import datetime

# Configuration
INPUT_FILE = "data/testing_data.jsonl"
OUTPUT_FILE = "data/forecast_features.csv"
OLLAMA_URL = "http://host.docker.internal:11434/api/chat"  # For Docker -> Host communication
MODEL_NAME = "egysentiment"

def get_sentiment_score(sentiment):
    if sentiment == "positive": return 1
    if sentiment == "negative": return -1
    return 0

def analyze_text(text):
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": text}],
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        content = response.json()['message']['content']
        
        # Robust JSON extraction
        if "{" in content:
            content = content[content.find("{"):content.rfind("}")+1]
        
        result = json.loads(content)
        return result.get("sentiment", "neutral").lower(), result.get("reasoning", "")
    except Exception as e:
        print(f"⚠️ Error analyzing text: {e}")
        return "neutral", "Error"

def main():
    print(f"🚀 Starting Auto-Scoring at {datetime.now()}")
    
    # 1. Load Input Data
    try:
        data = []
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                data.append(json.loads(line))
        df_input = pd.DataFrame(data)
        print(f"📚 Loaded {len(df_input)} articles from {INPUT_FILE}")
    except FileNotFoundError:
        print(f"❌ Input file {INPUT_FILE} not found.")
        return

    # 2. Load Existing Features (to avoid re-scoring)
    if os.path.exists(OUTPUT_FILE):
        df_existing = pd.read_csv(OUTPUT_FILE)
        # Create a unique signature for deduplication (e.g., text hash or URL if available)
        # Assuming 'text' is unique enough for now, or we can use URL if present
        existing_texts = set(df_existing['text'].astype(str))
        print(f"📂 Loaded {len(df_existing)} existing scored articles.")
    else:
        df_existing = pd.DataFrame(columns=['date', 'text', 'sentiment', 'sentiment_score', 'reasoning'])
        existing_texts = set()
        print("✨ Creating new features file.")

    # 3. Identify New Articles
    new_articles = df_input[~df_input['text'].astype(str).isin(existing_texts)]
    
    if new_articles.empty:
        print("✅ No new articles to score.")
        return

    print(f"⚡ Found {len(new_articles)} new articles to score.")

    # 4. Score New Articles
    new_rows = []
    for index, row in new_articles.iterrows():
        text = row.get('text', '')
        date = row.get('date', datetime.now().strftime('%Y-%m-%d')) # Default to today if missing
        
        print(f"   Processing: {text[:50]}...")
        sentiment, reasoning = analyze_text(text)
        score = get_sentiment_score(sentiment)
        
        new_rows.append({
            'date': date,
            'text': text,
            'sentiment': sentiment,
            'sentiment_score': score,
            'reasoning': reasoning
        })

    # 5. Append and Save
    if new_rows:
        df_new = pd.DataFrame(new_rows)
        # Append to file (header only if file didn't exist)
        df_new.to_csv(OUTPUT_FILE, mode='a', header=not os.path.exists(OUTPUT_FILE), index=False)
        print(f"💾 Appended {len(df_new)} new scored articles to {OUTPUT_FILE}")
    
    print("🏁 Auto-Scoring Complete.")

if __name__ == "__main__":
    main()
