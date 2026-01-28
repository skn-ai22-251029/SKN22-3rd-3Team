import os
import json
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv
from .base import BaseCrawler

load_dotenv()

class TheCatAPICrawler(BaseCrawler):
    def __init__(self):
        self.api_key = os.getenv("THECATAPI_API_KEY")
        self.base_url = "https://api.thecatapi.com/v1"
        if not self.api_key:
            # Fallback for dev environments where .env might not be loaded automatically by other means
            # logic to check if it's already in env var not needed if load_dotenv works, 
            # but usually good to check os.environ directly too if load_dotenv fails or isn't used.
            pass
            
        if not self.api_key:
             raise ValueError("THECATAPI_API_KEY not found in environment variables")

    def crawl(self) -> List[Dict[str, Any]]:
        headers = {"x-api-key": self.api_key}
        breeds = []
        page = 0
        limit = 100 

        print(f"Fetching breeds from {self.base_url}/breeds...")
        
        while True:
            try:
                print(f"  Fetching page {page}...")
                response = requests.get(
                    f"{self.base_url}/breeds",
                    headers=headers,
                    params={"page": page, "limit": limit}
                )
                response.raise_for_status()
                data = response.json()
                
                if not data:
                    break
                
                breeds.extend(data)
                
                pagination_count = response.headers.get('pagination-count')
                if pagination_count:
                    print(f"  Progress: {len(breeds)}/{pagination_count}")
                    if len(breeds) >= int(pagination_count):
                        break
                
                # If less data than limit returned, we are likely at the end
                if len(data) < limit:
                    break
                    
                page += 1
                
            except requests.RequestException as e:
                print(f"Error fetching data: {e}")
                break
                
        return breeds

    def save(self, data: List[Dict[str, Any]], filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(data)} items to {filepath}")
