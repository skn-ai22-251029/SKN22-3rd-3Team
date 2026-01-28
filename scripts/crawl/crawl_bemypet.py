import os
import sys

# Ensure src is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.crawler.bemypet import BeMyPetCrawler

def main():
    print("Starting crawler...")
    
    # Create output directory if not exists
    # os.getcwd() should be the project root when running via "conda run python scripts/..."
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, "bemypet_catlab.json")
    
    existing_data = []
    start_page = 1
    if os.path.exists(output_file):
        try:
            import json
            with open(output_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
            if existing_data:
                last_item = existing_data[-1]
                start_page = last_item.get("page", 0) + 1
                print(f"Resuming from page {start_page} (Found {len(existing_data)} items)")
        except Exception as e:
            print(f"Error loading existing data: {e}")

    crawler = BeMyPetCrawler(max_pages=116, start_page=start_page) 
    new_data = crawler.crawl()
    
    if new_data:
        final_data = existing_data + new_data
        crawler.save(final_data, output_file)
    else:
        print("No new data collected.")

if __name__ == "__main__":
    main()
