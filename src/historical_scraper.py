#!/usr/bin/env python3
"""
EgySentiment Historical Data Scraper
One-time use bulk data collection from Egyptian financial news archives
Collects historical articles for fine-tuning Llama 3.1-8B
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import os
from datetime import datetime
from groq import Groq
from tqdm import tqdm
from dotenv import load_dotenv
from fake_useragent import UserAgent
from urllib.parse import urljoin
from newspaper import Article
import nltk

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Load environment variables
load_dotenv()

# Initialize
ua = UserAgent()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Configuration
GROQ_MODEL = "llama-3.3-70b-versatile"
RATE_LIMIT_DELAY = 2.5  # 30 RPM compliance
MAX_ARTICLES_PER_SOURCE = 200  # Increased limit for aggressive scraping

# Keywords for filtering
KEYWORDS = [
    # English
    "egx", "egx30", "egypt stock exchange", "stock", "shares", "profit", "earnings",
    "dividend", "revenue", "bank", "investment", "ipo", "merger", "acquisition",
    "economy", "gdp", "inflation", "central bank", "financial", "market",
    # Arabic
    "البورصة", "المصرية", "أسهم", "أرباح", "توزيعات", "استثمار",
    "اقتصاد", "بنك", "مالي", "تداول"
]

# Egyptian Financial News Sources with Archive URLs
SOURCES = {
    # Daily News Egypt - Archive pages
    "Daily News Egypt": {
        "base": "https://dailynewsegypt.com",
        "archive_pattern": "https://dailynewsegypt.com/category/business/page/{page}/",
        "pages": 50,
        "selector": "h3.entry-title a"
    },
    
    # Egypt Independent - Archive
    "Egypt Independent": {
        "base": "https://egyptindependent.com",
        "archive_pattern": "https://egyptindependent.com/category/business/page/{page}/",
        "pages": 50,
        "selector": "h2.entry-title a"
    },
    
    # Ahram Online - Business
    "Ahram Business": {
        "base": "https://english.ahram.org.eg",
        "archive_pattern": "https://english.ahram.org.eg/News/Business/{page}.aspx",
        "pages": 30,
        "selector": "div.titlearticle a"
    },
    
    # Mubasher
    "Mubasher": {
        "base": "https://english.mubasher.info",
        "archive_pattern": "https://english.mubasher.info/news/list?page={page}",
        "pages": 50,
        "selector": "h3.title a"
    },
    
    # Arab Finance
    "Arab Finance": {
        "base": "https://www.arabfinance.com",
        "archive_pattern": "https://www.arabfinance.com/en/news/latest?page={page}",
        "pages": 50,
        "selector": "div.news-title a"
    },
}


def get_headers():
    """Generate random user agent headers to bypass blocks"""
    return {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }


def fetch_article_urls(source_name, config):
    """Fetch article URLs from archive pages"""
    urls = []
    base_url = config['base']
    pattern = config['archive_pattern']
    pages = config['pages']
    selector = config['selector']
    
    print(f"\n📰 Scraping {source_name} archives...")
    
    for page in tqdm(range(1, pages + 1), desc=f"  Pages from {source_name}"):
        try:
            url = pattern.format(page=page)
            response = requests.get(url, headers=get_headers(), timeout=15)
            
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.content, 'lxml')
            links = soup.select(selector)
            
            for link in links:
                href = link.get('href', '')
                if href:
                    full_url = urljoin(base_url, href)
                    urls.append(full_url)
            
            time.sleep(1)  # Polite scraping delay
            
        except Exception as e:
            # print(f"  ⚠️  Error on page {page}: {e}")
            continue
    
    print(f"  ✓ Found {len(urls)} article URLs")
    return urls


def extract_article_text(url):
    """Extract article title and content using newspaper3k"""
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.title, article.text
    except Exception as e:
        return None, None


def filter_relevant(title, content):
    """Check if article is relevant based on keywords"""
    if not title or not content:
        return False
    text = f"{title} {content}".lower()
    return any(keyword.lower() in text for keyword in KEYWORDS)


def distill_knowledge(text):
    """Get sentiment from Groq"""
    prompt = f"""Analyze the sentiment of this Egyptian financial news article.

Article: {text[:2000]}

Respond ONLY with valid JSON in this exact format:
{{"sentiment": "positive/negative/neutral", "reasoning": "brief explanation"}}"""

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a financial sentiment analysis expert. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=150
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    
    except:
        return {"sentiment": "neutral", "reasoning": "parsing_error"}


def load_existing_urls(output_file):
    """Load existing URLs to avoid duplicates"""
    existing = set()
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    existing.add(record.get('source', ''))
                except:
                    continue
    return existing


def main():
    """Run historical scraper"""
    print("=" * 70)
    print("EgySentiment Historical Scraper")
    print("Bulk Data Collection for Llama 3.1-8B Fine-tuning")
    print("=" * 70)
    
    output_file = "data/testing_data.jsonl"
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    existing_urls = load_existing_urls(output_file)
    print(f"\n📊 Existing dataset: {len(existing_urls)} samples")
    
    all_articles = []
    
    # Step 1: Collect article URLs from all sources
    for source_name, config in SOURCES.items():
        urls = fetch_article_urls(source_name, config)
        # Filter out existing URLs
        new_urls = [u for u in urls if u not in existing_urls]
        all_articles.extend([(source_name, u) for u in new_urls[:MAX_ARTICLES_PER_SOURCE]])
    
    print(f"\n📦 Total new articles to process: {len(all_articles)}")
    
    if not all_articles:
        print("✓ No new articles found. Historical collection complete!")
        return
    
    # Step 2: Process articles
    processed = 0
    skipped = 0
    
    print(f"\n🔬 Processing articles through Groq...")
    print(f"⏱️  Rate limit: {RATE_LIMIT_DELAY}s per request")
    print(f"⏳ Estimated time: {len(all_articles) * RATE_LIMIT_DELAY / 60:.1f} minutes\n")
    
    with open(output_file, 'a', encoding='utf-8') as f:
        for source_name, url in tqdm(all_articles, desc="Extracting & labeling"):
            # Extract article
            title, content = extract_article_text(url)
            
            if not title or not content:
                skipped += 1
                continue
            
            # Filter relevance
            if not filter_relevant(title, content):
                skipped += 1
                continue
            
            # Get sentiment
            text = f"{title}. {content[:1500]}"
            analysis = distill_knowledge(text)
            
            # Save record
            record = {
                "text": text,
                "title": title,
                "sentiment": analysis.get("sentiment", "neutral"),
                "reasoning": analysis.get("reasoning", ""),
                "source": url,
                "source_name": source_name,
                "published": "",
                "timestamp": datetime.now().isoformat()
            }
            
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
            f.flush()  # Save immediately
            processed += 1
            
            # Rate limiting
            time.sleep(RATE_LIMIT_DELAY)
    
    total = len(existing_urls) + processed
    print(f"\n{'=' * 70}")
    print(f"✓ Historical scraping complete!")
    print(f"  New articles processed: {processed}")
    print(f"  Skipped (irrelevant/error): {skipped}")
    print(f"  Total dataset size: {total} samples")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
