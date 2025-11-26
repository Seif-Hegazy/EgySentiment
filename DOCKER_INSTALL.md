# Docker Installation & Setup

## Install Docker Desktop

**Download:** https://www.docker.com/products/docker-desktop/

1. Download Docker Desktop for Mac (Apple Silicon)
2. Install the `.dmg` file
3. Open Docker Desktop
4. Wait for Docker engine to start (whale icon in menu bar)

## Start EgySentiment with Docker

```bash
cd /Users/seifhegazy/Documents/NLP\ Project/EgySentiment
./setup_docker.sh
```

## Access Airflow

- **URL:** http://localhost:8080
- **Username:** admin
- **Password:** admin

Enable DAG: `egy_sentiment_daily_collection`

## Run Without Docker (Current Method)

Already working:
```bash
cd /Users/seifhegazy/Documents/NLP\ Project/EgySentiment
source data_sci_env/bin/activate
python src/data_pipeline.py
```

Runs every 4-6 hours manually for continuous data  collection.
