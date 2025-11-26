# EgySentiment Data Collection Strategy

## Current Status
- **Total Samples:** 24 labeled articles
- **Active RSS Feeds:** 3/16 sources returning data
  - Daily News Egypt (10 articles)
  - Egypt Independent (10 articles)  
  - Investing.com (10 articles)

## Why Only ~30 Articles Per Run?

**RSS Feed Limitation:** RSS feeds only show the 10-20 most recent articles. This is by design.

## Strategy to Collect 1000+ Samples

### Option 1: Automated Scheduled Collection (RECOMMENDED)
Run the pipeline **multiple times per day** to capture new articles as they're published:

```bash
# Run every 6 hours to capture ~40-60 new articles daily
# Day 1: ~24 samples
# Week 1: ~168-420 samples
# Month 1: ~720-1,800 samples
```

**Setup a cron job (macOS):**
```bash
# Edit crontab
crontab -e

# Add this line to run every 6 hours
0 */6 * * * cd /Users/seifhegazy/Documents/NLP\ Project/EgySentiment && /Users/seifhegazy/Documents/NLP\ Project/EgySentiment/data_sci_env/bin/python data_pipeline.py >> collection.log 2>&1
```

### Option 2: Manual Batch Collection
Run the pipeline manually 4-6 times per day:
```bash
cd /Users/seifhegazy/Documents/NLP\ Project/EgySentiment
source data_sci_env/bin/activate
python data_pipeline.py
```

Wait 4-6 hours between runs for new articles to be published.

### Option 3: Increase Feed Diversity
Add more specialized feeds:
- Sector-specific: banking, real estate, energy
- Regional Arabic news sources
- Financial data providers
- Corporate announcement feeds

## Rate Limit Constraints
- **Groq Free Tier:** 30 requests per minute
- **Current Setting:** 2.5s delay = ~24 requests/min (safe buffer)
- **Max Processing:** ~720 articles/hour (theoretical)
- **Practical Limit:** Depends on available RSS content

## Data Accumulation Timeline

| Timeframe | Collection Frequency | Expected Samples |
|-----------|---------------------|------------------|
| 1 Day     | 4x daily            | 80-120          |
| 1 Week    | 4x daily            | 560-840         |
| 2 Weeks   | 4x daily            | 1,120-1,680     |
| 1 Month   | 2x daily            | 1,440-2,160     |

## Deduplication
✓ The pipeline automatically:
- Tracks processed URLs
- Skips duplicate articles
- Appends only new data
- Preserves existing samples

## Next Steps
1. Set up automated collection (cron job)
2. Let it run for 1-2 weeks
3. Monitor `training_data.jsonl` growth
4. Adjust frequency based on new article rate

## Quick Commands
```bash
# Check total samples
wc -l training_data.jsonl

# View sentiment distribution
grep -o '"sentiment":"[^"]*"' training_data.jsonl | sort | uniq -c

# Run pipeline
python data_pipeline.py

# Monitor in real-time
tail -f collection.log
```
