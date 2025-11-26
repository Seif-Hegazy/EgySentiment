# 🚀 QUICK START GUIDE - EgySentiment Data Collection

## For Llama 3-8B Fine-Tuning

---

## Step 1: Run Historical Scraper (ONE TIME)

```bash
cd /Users/seifhegazy/Documents/NLP\ Project/EgySentiment
source data_sci_env/bin/activate
python historical_scraper.py
```

**What it does:**
- Scrapes archives from 8 Egyptian financial news sources
- Processes up to 100 articles per source (800 total potential)
- Filters for financial relevance
- Labels sentiment with Groq

**Expected:**
- Duration: 30-90 minutes
- Output: 500-1,500 labeled samples
- File: `training_data.jsonl`

---

## Step 2: Set Up Daily Collection (AUTOMATED)

### Option A: Cron Job (Recommended)
```bash
crontab -e
```

Add this line to run every 4 hours:
```bash
0 */4 * * * cd /Users/seifhegazy/Documents/NLP\ Project/EgySentiment && /Users/seifhegazy/Documents/NLP\ Project/EgySentiment/data_sci_env/bin/python data_pipeline.py >> /tmp/egy_collection.log 2>&1
```

### Option B: Manual (4-6 times daily)
```bash
python data_pipeline.py
```

**What it does:**
- Fetches from 10 RSS feeds (with user-agent spoofing)
- Scrapes 4 blocked sources directly (Mubasher, Arab Finance, EGX, Ahram)
- Adds 15-50 new samples per run
- Auto-deduplicates

---

## Step 3: Monitor Collection

```bash
# Check total samples
wc -l training_data.jsonl

# View sentiment distribution
python -c "import json; from collections import Counter; print(Counter([json.loads(l)['sentiment'] for l in open('training_data.jsonl')]))"

# Watch it grow
watch -n 10 wc -l training_data.jsonl
```

---

## Step 4: Convert for Fine-tuning (When ready)

Wait until you have **1,000+ samples**, then:

```bash
python convert_to_unsloth.py
```

This creates `training_data_unsloth.json` in instruction format for Llama.

---

## ⏱️ Timeline to 2,000 Samples

| Method | Duration | Samples |
|--------|----------|---------|
| **Historical scraper** | 1 hour | ~800-1,200 |
| **Daily (4x/day)** | 1 week | ~400-700 |
| **Daily (4x/day)** | 2 weeks | ~800-1,400 |
| **TOTAL** | **2-3 weeks** | **~2,000-2,600** |

---

## 📊 Data Sources

### Historical Scraper (Bulk - Run Once)
1. Daily News Egypt (50 pages)
2. Egypt Independent (30 pages)
3. Enterprise (20 pages)
4. Business Today Egypt (30 pages)
5. Egypt Today (25 pages)
6. Ahram Business (20 pages)
7. **Mubasher** (30 pages) ✓ *Bypasses RSS block*
8. **Arab Finance** (40 pages) ✓ *Bypasses RSS block*

### Daily Pipeline (Continuous)
**RSS (10 feeds):**
- Daily News Egypt, Egypt Independent, Enterprise
- Business Today, Egypt Today
- Reuters Egypt, Middle East Eye
- Investing.com, Zawya, Al Jazeera

**Direct Scraping (4 sources):**
- **Mubasher** ✓ *RSS workaround*
- **Arab Finance** ✓ *RSS workaround*  
- **EGX News** (Egyptian Exchange official)
- **Ahram Business** ✓ *Additional coverage*

---

## 🎯 Current Status

```bash
# Check current dataset
wc -l training_data.jsonl
# Output: 40 training_data.jsonl

# Sentiment distribution
python convert_to_unsloth.py
```

**Next Action:** Run `python historical_scraper.py` to bootstrap dataset!

---

## 🔧 Troubleshooting

**"No new entries"**  
→ Normal. Wait 4-6 hours between runs for new articles.

**RSS feed errors (SSL, timeout)**  
→ Expected. Direct scraping provides fallback coverage.

**Rate limit warnings**  
→ Delay enforced at 2.5s. Check Groq API key is valid.

**Historical scraper taking long**  
→ Normal. Processing 1000+ articles takes 40-90 mins.

---

## 📁 Files Overview

| File | Purpose |
|------|---------|
| `historical_scraper.py` | ONE-TIME bulk collection |
| `data_pipeline.py` | DAILY new articles |
| `convert_to_unsloth.py` | Convert to fine-tuning format |
| `training_data.jsonl` | Raw labeled dataset |
| `training_data_unsloth.json` | Ready for Llama training |
| `README.md` | Full documentation |

---

## ✅ Checklist

- [ ] Run `python historical_scraper.py` (once, ~1 hour)
- [ ] Set up cron job OR run `data_pipeline.py` 4x daily
- [ ] Wait 1-2 weeks to reach 1,500-2,500 samples
- [ ] Run `python convert_to_unsloth.py`
- [ ] Fine-tune Llama 3-8B with generated JSON

**Target:** 2,000+ samples for production-quality fine-tuning
