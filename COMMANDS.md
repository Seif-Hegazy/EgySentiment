# EgySentiment - Quick Command Reference

## 🐳 Docker Commands

### Initial Setup (One Time)
```bash
cd /Users/seifhegazy/Documents/NLP\ Project/EgySentiment
./setup_docker.sh
```

### Start/Stop Services
```bash
# Start all services (Airflow + PostgreSQL)
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove all data
docker-compose down -v

# Restart services
docker-compose restart
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f airflow-scheduler
docker-compose logs -f airflow-webserver
docker-compose logs -f scraper
```

## 📊 Data Collection

### Historical Scraper (Bootstrap Dataset)
```bash
# Via Docker
docker-compose run scraper python src/historical_scraper.py

# Direct (if venv active)
cd EgySentiment && python src/historical_scraper.py
```

### Daily Pipeline (Manual Run)
```bash
# Via Docker
docker-compose run scraper python src/data_pipeline.py

# Direct (if venv active)
python src/data_pipeline.py
```

## 🤖 Airflow

### Access UI
- URL: http://localhost:8080
- Username: `admin`
- Password: `admin`

### DAG Operations
```bash
# List DAGs
docker-compose exec airflow-scheduler airflow dags list

# Trigger DAG manually
docker-compose exec airflow-scheduler airflow dags trigger egy_sentiment_daily_collection

# Pause DAG
docker-compose exec airflow-scheduler airflow dags pause egy_sentiment_daily_collection

# Unpause DAG
docker-compose exec airflow-scheduler airflow dags unpause egy_sentiment_daily_collection
```

## 📈 Monitoring

### Check Dataset Size
```bash
# Total samples
wc -l data/training_data.jsonl

# Via Docker
docker-compose run scraper wc -l data/training_data.jsonl
```

### Sentiment Distribution
```bash
# Via Docker
docker-compose run scraper python src/convert_to_unsloth.py

# Direct
python src/convert_to_unsloth.py
```

### View Latest Entries
```bash
# Last 5 entries (formatted)
tail -5 data/training_data.jsonl | python -m json.tool

# Count by sentiment
grep -o '"sentiment":"[^"]*"' data/training_data.jsonl | sort | uniq -c
```

## 🔄 Convert to Unsloth Format
```bash
# Via Docker
docker-compose run scraper python src/convert_to_unsloth.py

# Direct
python src/convert_to_unsloth.py
```

## 🛠️ Troubleshooting

### Rebuild Docker Images
```bash
docker-compose build --no-cache
docker-compose up -d
```

### Reset Airflow Database
```bash
docker-compose down -v
docker-compose up airflow-init
docker-compose up -d
```

### Fix Permission Issues
```bash
sudo chown -R $USER:$USER data/ logs/
chmod -R 755 data/ logs/
```

### Check Container Status
```bash
docker-compose ps
```

### Access Container Shell
```bash
# Scraper container
docker-compose run scraper /bin/bash

# Airflow scheduler
docker-compose exec airflow-scheduler /bin/bash
```

## 📦 Backup Data
```bash
# Backup training data
cp data/training_data.jsonl data/backup_$(date +%Y%m%d).jsonl

# Archive data directory
tar -czf egysentiment_data_$(date +%Y%m%d).tar.gz data/
```

## 🎯 Production Workflow

### Day 1: Bootstrap
```bash
# 1. Start Docker
./setup_docker.sh

# 2. Run historical scraper
docker-compose run scraper python src/historical_scraper.py

# 3. Check results
docker-compose run scraper wc -l data/training_data.jsonl
```

### Day 1-14: Automated Collection
```bash
# 1. Enable DAG in Airflow UI (http://localhost:8080)
# 2. Monitor via Airflow UI or logs
docker-compose logs -f airflow-scheduler

# 3. Check progress daily
docker-compose run scraper python src/convert_to_unsloth.py
```

### Day 14+: Fine-tuning
```bash
# 1. Convert to Unsloth format
docker-compose run scraper python src/convert_to_unsloth.py

# 2. Copy data for fine-tuning
cp data/training_data_unsloth.json /path/to/your/training/dir

# 3. Use with Unsloth/Llama-3-8B
```

## 🔐 Environment Variables

Edit `.env`:
```bash
GROQ_API_KEY=your_actual_groq_api_key
AIRFLOW_UID=50000  # Auto-set by setup script
```

## 📊 Expected Timeline

| Day | Action | Samples |
|-----|--------|---------|
| 1 | Historical scraper | 500-1,500 |
| 2-7 | Airflow (6x daily) | +400-700 |
| 8-14 | Airflow (6x daily) | +400-700 |
| **Total** | **2 weeks** | **~1,300-2,900** |
