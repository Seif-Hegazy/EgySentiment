# EgySentiment: Egyptian Financial News Sentiment Dataset

Automated data collection pipeline for fine-tuning Llama 3-8B on Egyptian financial sentiment analysis.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Groq API Key (free tier: 30 RPM)

### 1. Setup Environment
```bash
# Clone/navigate to project
cd EgySentiment

# Add your Groq API key to .env
echo "GROQ_API_KEY=your_key_here" > .env

# Start Docker services (Airflow + PostgreSQL)
docker-compose up -d
```

### 2. Run One-Time Historical Collection
```bash
docker-compose run scraper python src/historical_scraper.py
```
**Expected:** 500-1,500 labeled samples in 30-90 minutes

### 3. Access Airflow UI
- URL: http://localhost:8080
- Username: `admin`
- Password: `admin`

**DAG:** `egy_sentiment_daily_collection` (runs every 4 hours)

---

## � Project Structure

```
EgySentiment/
├── src/                          # Source code
│   ├── data_pipeline.py          # Daily RSS + scraping
│   ├── historical_scraper.py     # Bulk archive collection
│   └── convert_to_unsloth.py     # Format converter
├── dags/                         # Airflow DAGs
│   └── sentiment_collection.py   # Daily automation
├── docker/                       # Docker configuration
│   ├── Dockerfile                # Python scraper image
│   └── requirements.txt          # Dependencies
├── data/                         # Output data
│   ├── testing_data.jsonl        # Raw labeled data (Local Egyptian Data)
│   └── training_data_unsloth.json# (Deprecated) Ready for fine-tuning
├── logs/                         # Airflow logs
├── docs/                         # Documentation
├── .env                          # Environment variables
├── docker-compose.yml            # Docker orchestration
└── README.md                     # This file
```

---

## � Data Sources (14 Total)

### Historical Scraper (8 sources, ~2,500 articles)
- Daily News Egypt, Egypt Independent, Enterprise
- Business Today Egypt, Egypt Today, Ahram Business
- **Mubasher**, **Arab Finance** (RSS bypass with scraping)

### Daily Pipeline (10 RSS + 4 Direct Scraping)
- **RSS:** Daily News Egypt, Egypt Today, Enterprise, Reuters, Investing.com, etc.
- **Direct Scraping:** Mubasher, Arab Finance, EGX News, Ahram Business

**Total Coverage:** 80+ financial keywords (English + Arabic)

---

## 🎯 Data Collection Strategy

| Phase | Method | Duration | Samples |
|-------|--------|----------|---------|
| **Bootstrap** | Historical scraper | 1-2 hours | 500-1,500 |
| **Daily** | Airflow automation | 2 weeks | +800-1,400 |
| **Total** | Combined | ~2 weeks | **1,300-2,900** |

---

## � Docker Services

### Services
- **airflow-webserver** (port 8080): UI dashboard
- **airflow-scheduler**: Runs DAGs on schedule
- **postgres**: Airflow metadata database
- **scraper**: Python scraping environment

### Commands
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f airflow-scheduler

# Run historical scraper
docker-compose run scraper python src/historical_scraper.py

# Run daily pipeline manually
docker-compose run scraper python src/data_pipeline.py

# Stop services
docker-compose down

# Stop and remove data
docker-compose down -v
```

---

## 🤖 Airflow Automation

### DAG: `egy_sentiment_daily_collection`
- **Schedule:** Every 4 hours (`0 */4 * * *`)
- **Tasks:**
  1. Run daily data pipeline
  2. Deduplicate data (Automated)
  3. Check data quality
  4. Send alerts (optional)

### Accessing Airflow
1. Navigate to http://localhost:8080
2. Login with `admin` / `admin`
3. Enable the DAG: `egy_sentiment_daily_collection`
4. Monitor runs in the UI

---

## 📈 Monitoring

### Check Dataset Size
```bash
# From host
wc -l data/testing_data.jsonl

# From Docker
docker-compose run scraper wc -l data/testing_data.jsonl
```

### Sentiment Distribution
```bash
docker-compose run scraper python src/convert_to_unsloth.py
```

### View Logs
```bash
# Airflow scheduler logs
docker-compose logs -f airflow-scheduler

# Scraper logs
docker-compose logs -f scraper
```

---

## � Fine-Tuning Preparation

### Convert to Unsloth Format
```bash
docker-compose run scraper python src/convert_to_unsloth.py
```

### Output Format
```json
{
  "instruction": "Analyze the sentiment of this Egyptian financial news...",
  "input": "Article: [full text]",
  "output": "Sentiment: POSITIVE\nReasoning: ..."
}
```

### Use with Unsloth
```python
from unsloth import FastLanguageModel
import json

# Load converted data
with open('data/training_data_unsloth.json') as f:
    dataset = json.load(f)

# Load model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-3-8b-Instruct-bnb-4bit",
    max_seq_length=2048,
    load_in_4bit=True,
)

# Fine-tune with your Egyptian sentiment data

### Hybrid Training Strategy (Phase 2.5)
We now use a **Hybrid Training** approach to fix domain mismatch:
1.  **Train:** Financial PhraseBank + 50% of `testing_data.jsonl` (Local Data).
2.  **Test:** Remaining 50% of `testing_data.jsonl`.
3.  **Goal:** Teach the model both general financial sentiment and Egyptian news nuances.
```

---

## � Configuration

### Environment Variables (.env)
```bash
GROQ_API_KEY=your_groq_api_key_here
AIRFLOW_UID=50000
```

### Airflow Configuration
- **Executor:** LocalExecutor
- **Database:** PostgreSQL
- **Web Server Port:** 8080
- **DAG Files:** `/opt/airflow/dags`

---

## 🛠️ Troubleshooting

### "No new entries" message
✓ **Expected** - Wait 4 hours for new articles to be published

### RSS feed errors (SSL, timeout)
✓ **Expected** - Direct scraping provides fallback coverage

### Airflow webserver not accessible
```bash
# Restart services
docker-compose restart airflow-webserver
```

### Permission errors with data files
```bash
# Fix ownership
sudo chown -R $USER:$USER data/ logs/
```

### Groq rate limit errors
✓ Check API key validity
✓ Delay enforced at 2.5s per request (30 RPM compliant)

---

## 📊 Expected Dataset Characteristics

### Target Metrics (@ 2,000 samples)
- **Sentiments:** Positive (40-50%), Neutral (30-40%), Negative (15-25%)
- **Sources:** 14+ distinct Egyptian financial news outlets
- **Time Range:** 1-12 months of articles
- **Language:** English with Arabic keyword coverage
- **Topics:** Banking, markets, economy, corporate actions, regulations

---

## � System Status

**Current Implementation:**
- ✅ Historical scraper (8 sources, bulk collection)
- ✅ Daily pipeline (14 sources with RSS bypass)
- ✅ Docker containerization
- ✅ Airflow automation (4-hour schedule)
- ✅ Automated Deduplication
- ✅ Unsloth format converter
- ✅ Complete documentation

**Production Ready:** ✅ Yes

---

## 📚 Additional Documentation

- **Architecture Details:** `docs/ARCHITECTURE.md`
- **Collection Strategy:** `docs/DATA_COLLECTION_GUIDE.md`
- **Quick Reference:** `docs/QUICKSTART.md`

---

## � Recommended Workflow

1. **Day 1:** Run historical scraper → Get 500-1,500 samples
2. **Day 1-14:** Airflow runs automatically every 4 hours → +40-70 samples/day
3. **Day 14:** Check dataset size → Should have 1,300-2,900 samples
4. **Day 14:** Run converter → Generate Unsloth format
5. **Day 15:** Fine-tune Llama 3-8B with your dataset

---

## 📞 Support

For issues or questions:
- Check `docs/` folder for detailed guides
- Review Docker logs: `docker-compose logs`
- Check Airflow UI for DAG execution history

---

**Built for:** Fine-tuning Llama 3-8B Instruct on Egyptian financial sentiment analysis  
**Dataset Format:** JSONL (raw) → JSON (Unsloth instruction format)  
**Automation:** Apache Airflow + Docker  
**API:** Groq (Llama 3.3-70B for labeling)
