import os
import sys
import asyncio
import argparse
import json
from src.domain.classifier import ClassifierFactory
from src.core.config import ZipsaConfig

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

async def main():
    parser = argparse.ArgumentParser(description="Zipsa Knowledge Base Classification")
    parser.add_argument("--version", type=str, choices=["v1", "v2"], default="v2", help="Zipsa version (v1 or v2)")
    parser.add_argument("--batch-size", type=int, default=15, help="Batch size for LLM processing")
    args = parser.parse_args()

    policy = ZipsaConfig.get_policy(args.version)
    classifier = ClassifierFactory.create(args.version)
    
    print(f"🚀 Starting {args.version} Classification...")
    
    if not os.path.exists(policy.raw_data_path):
        print(f"❌ Error: Raw data not found at {policy.raw_data_path}")
        return

    with open(policy.raw_data_path, 'r') as f:
        raw_items = json.load(f)

    for i, item in enumerate(raw_items):
        if 'uid' not in item:
            item['uid'] = f"doc_{i}"

    results = []
    if os.path.exists(policy.processed_data_path):
        with open(policy.processed_data_path, 'r') as f:
            try:
                results = json.load(f)
                print(f"📦 Resuming from {len(results)} items...")
            except:
                results = []

    processed_uids = {r['uid'] for r in results}
    remaining_items = [item for item in raw_items if item['uid'] not in processed_uids]

    if not remaining_items:
        print("✅ All items already processed.")
        return

    for i in range(0, len(remaining_items), args.batch_size):
        batch = remaining_items[i : i + args.batch_size]
        print(f"📦 Batch {i//args.batch_size + 1}...")
        
        batch_results = await classifier.classify_batch(batch)
        
        for res in batch_results:
            orig = next((item for item in batch if item['uid'] == res['uid']), {})
            res.update({k: v for k, v in orig.items() if k not in res})
            results.append(res)

        os.makedirs(os.path.dirname(policy.processed_data_path), exist_ok=True)
        with open(policy.processed_data_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"✨ {args.version} Complete. Path: {policy.processed_data_path}")

if __name__ == "__main__":
    asyncio.run(main())
