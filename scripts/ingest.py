import os
import sys
import asyncio
import argparse
from src.domain.ingestor import ZipsaIngestor

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

async def main():
    parser = argparse.ArgumentParser(description="Zipsa Knowledge Base Ingestion")
    parser.add_argument("--version", type=str, choices=["v1", "v2"], default="v2", help="Zipsa version (v1 or v2)")
    args = parser.parse_args()

    ingestor = ZipsaIngestor(args.version)
    
    print(f"🚀 Starting {args.version} Ingestion...")
    
    await ingestor.ingest_breeds()
    await ingestor.ingest_guides()
    
    print(f"✨ {args.version} Ingestion Complete!")

if __name__ == "__main__":
    asyncio.run(main())
