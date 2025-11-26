"""
Airflow DAG for EgySentiment Daily Data Collection
Runs every 4 hours to collect new Egyptian financial news articles
"""

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import json
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'egy_sentiment_daily_collection',
    default_args=default_args,
    description='Collect Egyptian financial news articles every 4 hours',
   schedule_interval='0 */4 * * *',  # Every 4 hours
    start_date=datetime(2025, 11, 26),
    catchup=False,
    tags=['sentiment', 'scraping', 'egyptian-finance'],
)


def check_data_quality(**context):
    """Verify data collection succeeded and check quality"""
    data_file = '/opt/airflow/data/training_data.jsonl'
    
    if not os.path.exists(data_file):
        raise FileNotFoundError(f"Data file not found: {data_file}")
    
    # Count lines
    with open(data_file, 'r') as f:
        lines = f.readlines()
    
    total_samples = len(lines)
    
    # Get sentiment distribution
    sentiments = []
    for line in lines[-100:]:  # Check last 100 samples
        try:
            record = json.loads(line.strip())
            sentiments.append(record.get('sentiment', 'unknown'))
        except:
            continue
    
    from collections import Counter
    distribution = Counter(sentiments)
    
    print(f"✓ Total samples: {total_samples}")
    print(f"✓ Recent sentiment distribution: {dict(distribution)}")
    
    # Push to XCom for monitoring
    context['task_instance'].xcom_push(key='total_samples', value=total_samples)
    context['task_instance'].xcom_push(key='sentiment_dist', value=dict(distribution))
    
    return total_samples


# Task 1: Run daily data collection pipeline
collect_data = BashOperator(
    task_id='collect_daily_articles',
    bash_command='cd /opt/airflow && python src/data_pipeline.py',
    dag=dag,
)

# Task 2: Check data quality
quality_check = PythonOperator(
    task_id='check_data_quality',
    python_callable=check_data_quality,
    provide_context=True,
    dag=dag,
)

# Task 3: Log success
log_success = BashOperator(
    task_id='log_collection_success',
    bash_command='echo "EgySentiment collection completed at $(date)"',
    dag=dag,
)

# Define task dependencies
collect_data >> quality_check >> log_success
