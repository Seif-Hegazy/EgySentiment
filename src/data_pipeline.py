#!/usr/bin/env python3
"""
EgySentiment Daily Data Pipeline (Enhanced)
RSS scraping with workarounds for blocked feeds + direct web scraping
Optimized for continuous fine-tuning data collection
"""

import feedparser
import requests
import urllib3
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
RATE_LIMIT_DELAY = 2.5  # Non-negotiable 30 RPM rate limit

# Enhanced RSS Feeds - With SSL bypass workarounds
RSS_FEEDS = [
    # Verified Working (✓)
    "https://dailynewsegypt.com/feed/",
    "https://egyptindependent.com/feed/",
    "https://www.investing.com/rss/news_1.rss",
    "https://www.investing.com/rss/news_285.rss",
    
    # New Sources
    "https://www.al-monitor.com/rss",
    "https://www.arabnews.com/cat/4/rss.xml", # Economy
    "https://www.thenationalnews.com/rss/business/xml",
    "https://amwalalghad.com/feed/",
    
    # With SSL bypass workaround (may need direct scrape fallback)
    "https://www.zawya.com/en/economy/north-africa/rss",
    "https://www.egypttoday.com/feed",
    "https://www.reuters.com/places/egypt/feed",
    "https://www.businesstodayegypt.com/feed",
]

# Direct scraping sources (for blocked RSS or empty feeds)
DIRECT_SCRAPE_SOURCES = {
    "Mubasher": {
        "url": "https://english.mubasher.info/news/latest",
        "selector": "div.news-item h3 a",
        "base": "https://english.mubasher.info"
    },
    "Arab Finance": {
        "url": "https://www.arabfinance.com/en/news/latest",
        "selector": "div.news-title a",
        "base": "https://www.arabfinance.com"
    },
    "EGX News": {
        "url": "https://www.egx.com.eg/en/NewsDetails.aspx",
        "selector": "div.news-list a",
        "base": "https://www.egx.com.eg"
    },
    "Ahram Business": {
        "url": "https://english.ahram.org.eg/News/Business.aspx",
        "selector": "div.titlearticle a",
        "base": "https://english.ahram.org.eg"
    },
    # Fallbacks for empty RSS feeds
    "Zawya": {
        "url": "https://www.zawya.com/en/economy/north-africa",
        "selector": "a.article-title",
        "base": "https://www.zawya.com"
    },
    "Reuters Egypt": {
        "url": "https://www.reuters.com/world/middle-east/",
        "selector": "h3.story-title a", # Generic selector, needs testing
        "base": "https://www.reuters.com"
    },
    "Egypt Today": {
        "url": "https://www.egypttoday.com/Section/3/Business",
        "selector": "div.news-title a",
        "base": "https://www.egypttoday.com"
    },
    "Economy Plus": {
        "url": "https://economyplusme.com/en/",
        "selector": "h3.entry-title a",
        "base": ""
    }
}

# Keywords (expanded for better coverage)
KEYWORDS = [
    # English - Markets & Trading
    "egx", "egx30", "egx70", "egypt stock exchange", "cairo stock exchange",
    "stock", "shares", "equity", "securities", "trading", "listed", "delisted",
    "market cap", "volume", "index", "benchmark", "bullish", "bearish",
    
    # EGX30 Companies (Top constituents)
    "cib", "commercial international bank", "efg hermes", "elsewedy electric",
    "talaat moustafa", "tmgh", "fawry", "eastern company", "abu qir fertilizers",
    "mopco", "sidi kerir", "sidpec", "ezz steel", "gb corp", "ghabbour",
    "palm hills", "sodic", "emaar misr", "heliopolis housing", "madinet masr",
    "credit agricole", "qnb alahli", "faisal islamic bank", "housing and development bank",
    "egyptian kuwaiti holding", "ekh", "alexandria container", "amoc",
    "telecom egypt", "we", "vodafone egypt", "orange egypt", "etisalat",
    "edita", "juhayna", "domty", "obour land", "ibnsina pharma", "rameda",
    
    # Financial Performance
    "profit", "earnings", "revenue", "sales", "income", "ebitda", "ebt",
    "dividend", "payout", "distribution", "yield", "quarterly", "annual",
    "fiscal year", "fy", "q1", "q2", "q3", "q4", "margins", "growth",
    "performance", "results", "financial statements", "balance sheet",
    "net income", "gross profit", "operating profit", "cash flow",
    
    # Corporate Actions
    "merger", "acquisition", "m&a", "takeover", "buyout", "consolidation",
    "ipo", "initial public offering", "listing", "offering", "capital increase",
    "rights issue", "bonus shares", "stock split", "buyback", "restructuring",
    "private placement", "tender offer", "divestment", "spin-off",
    
    # Investment & Finance
    "investment", "investor", "fund", "portfolio", "venture capital",
    "private equity", "valuation", "financing", "funding", "capital",
    "bond", "debt", "loan", "credit", "sukuk", "treasury", "t-bills",
    "eurobond", "sovereign debt", "fdi", "foreign direct investment",
    
    # Sectors
    "banking", "bank", "insurance", "real estate", "construction", "telecom",
    "pharmaceutical", "pharma", "manufacturing", "retail", "tourism",
    "energy", "oil", "gas", "infrastructure", "logistics", "fintech",
    "textiles", "agriculture", "automotive", "healthcare", "education",
    
    # Economic & Regulatory
    "economy", "economic", "gdp", "inflation", "interest rate", "monetary policy",
    "fiscal", "budget", "subsidy", "tax", "regulation", "compliance",
    "central bank", "cbe", "financial regulatory authority", "fra",
    "egyptian exchange", "misr clearing", "imf", "international monetary fund",
    "world bank", "ebrd", "currency", "exchange rate", "egp", "pound", "dollar",
    "devaluation", "float", "reserves", "foreign reserves", "external debt",
    "pmi", "purchasing managers index", "trade balance", "current account",
    
    # Geography
    "egypt", "egyptian", "cairo", "alexandria", "suez", "new administrative capital",
    
    # Arabic Keywords
    "البورصة", "المصرية", "البورصة المصرية", "تداول", "أسهم", "سهم",
    "مؤشر", "إيجى إكس", "السوق المالي", "قيمة سوقية", "رأس المال السوقي",
    "أرباح", "إيرادات", "مبيعات", "دخل", "صافي", "ربحية",
    "توزيعات", "توزيعات أرباح", "عائد", "ربع سنوي", "سنوي",
    "اندماج", "استحواذ", "طرح", "زيادة رأسمال", "اكتتاب",
    "استثمار", "مستثمر", "محفظة", "صندوق", "تمويل",
    "بنوك", "بنك", "تأمين", "عقارات", "اتصالات",
    "اقتصاد", "اقتصادي", "تضخم", "البنك المركزي", "فائدة", "سعر الفائدة",
    "مصر", "المصري", "القاهرة", "الجنيه", "الدولار", "تعويم",
    "صندوق النقد", "الدين الخارجي", "الاحتياطي النقدي", "أذون الخزانة",
    "التجاري الدولي", "هيرميس", "السويدي", "طلعت مصطفى", "فوري",
    "الشرقية للدخان", "أبو قير", "موبكو", "عز الدخيلة", "حديد عز"
]


def get_headers():
    """Generate headers with random user agent"""
    return {
        'User-Agent': ua.random,
        'Accept': 'application/rss+xml, application/xml, text/xml, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
    }


def fetch_rss_entries():
    """Parse RSS feeds with user-agent spoofing and SSL bypass"""
    entries = []
    print("📡 Fetching RSS feeds...")
    
    # Disable SSL warnings for problematic feeds
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    for feed_url in RSS_FEEDS:
        success = False
        
        # Try with SSL verification first
        try:
            response = requests.get(feed_url, headers=get_headers(), timeout=15, verify=True)
            feed = feedparser.parse(response.content)
            
            if feed.entries:
                entries.extend(feed.entries)
                print(f"✓ Fetched {len(feed.entries)} entries from {feed_url}")
                success = True
            else:
                print(f"⚠️  No entries from {feed_url}")
                
        except requests.exceptions.SSLError:
            # Retry without SSL verification for blocked sources
            try:
                response = requests.get(feed_url, headers=get_headers(), timeout=15, verify=False)
                feed = feedparser.parse(response.content)
                
                if feed.entries:
                    entries.extend(feed.entries)
                    print(f"✓ Fetched {len(feed.entries)} entries from {feed_url} (SSL bypass)")
                    success = True
                else:
                    print(f"⚠️  No entries from {feed_url}")
                    
            except Exception as e2:
                print(f"✗ SSL bypass also failed for {feed_url}: {type(e2).__name__}")
                
        except Exception as e:
            # Try SSL bypass as fallback
            if not success:
                try:
                    response = requests.get(feed_url, headers=get_headers(), timeout=15, verify=False)
                    feed = feedparser.parse(response.content)
                    
                    if feed.entries:
                        entries.extend(feed.entries)
                        print(f"✓ Fetched {len(feed.entries)} entries from {feed_url} (fallback)")
                        success = True
                    else:
                        print(f"⚠️  No entries from {feed_url}")
                        
                except Exception as e2:
                    print(f"✗ Error fetching {feed_url}: {type(e).__name__}")
    
    return entries


def scrape_latest_articles(source_name, config):
    """Scrape latest articles directly from website"""
    articles = []
    
    try:
        response = requests.get(config['url'], headers=get_headers(), timeout=10)
        soup = BeautifulSoup(response.content, 'lxml')
        
        links = soup.select(config['selector'])[:15]  # Get latest 15 articles
        
        for link in links:
            href = link.get('href', '')
            title = link.get_text(strip=True)
            
            if href and title:
                full_url = urljoin(config['base'], href)
                # Create entry similar to RSS format
                entry = {
                    'title': title,
                    'link': full_url,
                    'summary': '',
                    'published': ''
                }
                articles.append(entry)
        
        if articles:
            print(f"✓ Scraped {len(articles)} articles from {source_name}")
        
    except Exception as e:
        print(f"✗ Error scraping {source_name}: {e}")
    
    return articles


def fetch_direct_scrape():
    """Fetch from direct scraping sources"""
    entries = []
    print("\n🌐 Direct scraping from blocked sources...")
    
    for source_name, config in DIRECT_SCRAPE_SOURCES.items():
        articles = scrape_latest_articles(source_name, config)
        entries.extend(articles)
        time.sleep(1)  # Polite delay
    
    return entries


def filter_relevant_entries(entries):
    """Filter entries containing Egyptian financial keywords"""
    filtered = []
    
    for entry in entries:
        text = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
        
        if any(keyword.lower() in text for keyword in KEYWORDS):
            filtered.append(entry)
    
    print(f"🔍 Filtered {len(filtered)} relevant entries from {len(entries)} total")
    return filtered


def distill_knowledge(text):
    """Send text to Groq for sentiment analysis"""
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
    
    except json.JSONDecodeError:
        return {"sentiment": "neutral", "reasoning": "parsing_error"}
    except Exception as e:
        return {"sentiment": "neutral", "reasoning": f"error: {str(e)}"}


def load_existing_urls(output_file):
    """Load URLs of already processed articles"""
    existing_urls = set()
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                for line in f:
                    record = json.loads(line.strip())
                    existing_urls.add(record.get('source', ''))
        except Exception as e:
            print(f"⚠️  Warning: Could not load existing URLs: {e}")
    return existing_urls


def extract_full_text(url):
    """Extract full article text using newspaper3k"""
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        # print(f"⚠️  Could not extract full text from {url}: {e}")
        return ""

def build_training_dataset(entries):
    """Process entries and save to JSONL with deduplication"""
    output_file = 'data/testing_data.jsonl'
    
    # Load existing URLs
    existing_urls = load_existing_urls(output_file)
    initial_count = len(existing_urls)
    
    # Filter new entries
    new_entries = [e for e in entries if e.get('link', '') not in existing_urls]
    
    if not new_entries:
        print("\n⚠️  All entries already processed. No new data to add.")
        print(f"Total samples in dataset: {initial_count}")
        return output_file
    
    processed_count = 0
    
    print(f"\n🔬 Processing {len(new_entries)} NEW entries (skipping {len(entries) - len(new_entries)} duplicates)")
    print(f"⏱️  Rate limit: {RATE_LIMIT_DELAY}s per request (30 RPM enforcement)")
    
    with open(output_file, 'a', encoding='utf-8') as f:
        for entry in tqdm(new_entries, desc="Distilling knowledge"):
            title = entry.get('title', '')
            summary = entry.get('summary', '')
            link = entry.get('link', '')
            
            # Try to get full text
            full_text = extract_full_text(link)
            
            # Fallback to summary if full text extraction fails or is too short
            if len(full_text) < 100:
                text = f"{title}. {summary}"
            else:
                text = f"{title}. {full_text}"
            
            # Get sentiment from Groq
            analysis = distill_knowledge(text)
            
            # Build training record
            record = {
                "text": text,
                "title": title,
                "sentiment": analysis.get("sentiment", "neutral"),
                "reasoning": analysis.get("reasoning", ""),
                "source": link,
                "published": entry.get('published', ''),
                "timestamp": datetime.now().isoformat()
            }
            
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
            processed_count += 1
            
            # ENFORCE PHYSICS: Rate limiting
            time.sleep(RATE_LIMIT_DELAY)
    
    total_count = initial_count + processed_count
    print(f"\n✓ Added {processed_count} new labeled samples")
    print(f"✓ Total dataset size: {total_count} samples")
    return output_file


def main():
    """Execute the daily data ingestion pipeline"""
    print("=" * 60)
    print("EgySentiment Daily Data Pipeline (Enhanced)")
    print("=" * 60)
    
    # Validate API key
    if not os.getenv("GROQ_API_KEY"):
        print("✗ ERROR: GROQ_API_KEY not found in .env file")
        return
    
    # Step 1: Fetch from RSS feeds
    rss_entries = fetch_rss_entries()
    
    # Step 2: Fetch from direct scraping
    scraped_entries = fetch_direct_scrape()
    
    # Combine all entries
    all_entries = rss_entries + scraped_entries
    
    if not all_entries:
        print("✗ No entries fetched. Check sources.")
        return
    
    # Step 3: Filter relevant entries
    filtered = filter_relevant_entries(all_entries)
    
    if not filtered:
        print("✗ No relevant entries found.")
        return
    
    # Step 4: Build training dataset
    output_file = build_training_dataset(filtered)
    
    print("\n" + "=" * 60)
    print(f"✓ Pipeline complete! Training data: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
