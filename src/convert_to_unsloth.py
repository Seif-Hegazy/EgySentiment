#!/usr/bin/env python3
"""
Convert EgySentiment training data to Unsloth/Llama fine-tuning format
"""

import json
from datetime import datetime

def convert_to_unsloth_format(input_file="data/training_data.jsonl", output_file="data/training_data_unsloth.json"):
    """
    Convert JSONL sentiment data to instruction format for Llama fine-tuning
    """
    
    print("=" * 60)
    print("EgySentiment → Unsloth Converter")
    print("=" * 60)
    
    # Load data
    data = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data.append(json.loads(line.strip()))
            except:
                continue
    
    print(f"\n📊 Loaded {len(data)} samples from {input_file}")
    
    # Count sentiments
    from collections import Counter
    sentiments = Counter([d['sentiment'] for d in data])
    print(f"\nSentiment Distribution:")
    for sentiment, count in sentiments.items():
        print(f"  {sentiment.capitalize()}: {count} ({count/len(data)*100:.1f}%)")
    
    # Convert to instruction format
    formatted_data = []
    
    for item in data:
        # Format for Llama instruction tuning
        instruction = "Analyze the sentiment of this Egyptian financial news article and classify it as positive, negative, or neutral. Provide reasoning for your classification."
        
        input_text = f"Article: {item['text'][:1500]}"  # Limit length
        
        output_text = f"""Sentiment: {item['sentiment'].upper()}

Reasoning: {item['reasoning']}"""
        
        formatted_data.append({
            "instruction": instruction,
            "input": input_text,
            "output": output_text
        })
    
    # Save in Unsloth format
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(formatted_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Converted to Unsloth format: {output_file}")
    print(f"✓ Ready for Llama 3-8B fine-tuning!")
    
    # Print sample
    print(f"\n{'=' * 60}")
    print("Sample Entry:")
    print(f"{'=' * 60}")
    print(json.dumps(formatted_data[0], ensure_ascii=False, indent=2))
    print(f"{'=' * 60}")
    
    return len(formatted_data)


if __name__ == "__main__":
    count = convert_to_unsloth_format()
    
    print(f"\n📦 Next Steps for Fine-tuning:")
    print(f"  1. Ensure you have {count} samples (recommended: 1000+ for quality)")
    print(f"  2. Install Unsloth: pip install unsloth")
    print(f"  3. Use training_data_unsloth.json with Unsloth/Llama-3-8B")
    print(f"  4. Train with QLoRA for efficient fine-tuning")
