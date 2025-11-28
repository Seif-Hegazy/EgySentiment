#!/usr/bin/env python3
"""
EgySentiment Data Deduplication Script
Removes duplicates based on:
1. Exact URL matches
2. Fuzzy title matching (to catch same news from different sources)
"""

import json
import os
from difflib import SequenceMatcher
from tqdm import tqdm

DATA_FILE = "data/training_data.jsonl"
BACKUP_FILE = "data/training_data.jsonl.bak"
SIMILARITY_THRESHOLD = 0.90  # 90% similarity threshold for titles

def similar(a, b):
    """Check similarity ratio between two strings"""
    return SequenceMatcher(None, a, b).ratio()

def deduplicate():
    if not os.path.exists(DATA_FILE):
        print(f"✗ File not found: {DATA_FILE}")
        return

    print(f"🔍 Reading {DATA_FILE}...")
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    original_count = len(lines)
    print(f"📊 Total records: {original_count}")

    # Step 1: Exact URL Deduplication
    unique_urls = {}
    url_duplicates = 0
    
    for line in lines:
        try:
            record = json.loads(line.strip())
            url = record.get('source', '').strip()
            
            if not url:
                continue
                
            # Keep the one with longer content if URL exists
            if url in unique_urls:
                existing_record = unique_urls[url]
                if len(record.get('text', '')) > len(existing_record.get('text', '')):
                    unique_urls[url] = record
                url_duplicates += 1
            else:
                unique_urls[url] = record
        except:
            continue

    print(f"✓ Removed {url_duplicates} exact URL duplicates")
    
    # Step 2: Fuzzy Title Deduplication
    final_records = []
    title_duplicates = 0
    
    # Convert to list for iteration
    candidates = list(unique_urls.values())
    
    # Sort by text length (descending) to prefer longer articles
    candidates.sort(key=lambda x: len(x.get('text', '')), reverse=True)
    
    print("\n🔍 Checking for semantic duplicates (Title Similarity)...")
    
    processed_titles = []
    
    for record in tqdm(candidates):
        title = record.get('title', '').lower().strip()
        if not title:
            final_records.append(record)
            continue
            
        is_duplicate = False
        for existing_title in processed_titles:
            if similar(title, existing_title) > SIMILARITY_THRESHOLD:
                is_duplicate = True
                title_duplicates += 1
                break
        
        if not is_duplicate:
            final_records.append(record)
            processed_titles.append(title)

    print(f"✓ Removed {title_duplicates} semantic duplicates")
    
    # Save result
    print(f"\n💾 Saving cleaned dataset...")
    
    # Backup original
    if os.path.exists(BACKUP_FILE):
        os.remove(BACKUP_FILE)
    os.rename(DATA_FILE, BACKUP_FILE)
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        for record in final_records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
            
    final_count = len(final_records)
    removed_total = original_count - final_count
    
    print("=" * 60)
    print(f"✓ Deduplication Complete")
    print(f"  Original: {original_count}")
    print(f"  Final:    {final_count}")
    print(f"  Removed:  {removed_total} duplicates")
    print("=" * 60)

if __name__ == "__main__":
    deduplicate()
