import requests
from typing import Optional, Dict, Any

class WikipediaAPI:
    """
    A simple wrapper for the Wikipedia API.
    """
    def __init__(self, language: str = 'en'):
        self.api_url = f"https://{language}.wikipedia.org/w/api.php"
        self.session = requests.Session()
        # Wikipedia requires a User-Agent
        self.session.headers.update({
            "User-Agent": "CatBreedCrawler/1.0 (test@example.com)" 
        })

    def get_page_info(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves page information including title, extract (summary), URL, and last updated time.
        
        Args:
            title: The title of the page to search for.
            
        Returns:
            A dictionary containing 'title', 'context', 'url', 'updated_at' if found, else None.
        """
        params = {
            "action": "query",
            "format": "json",
            "prop": "extracts|info",
            "inprop": "url|displaytitle",
            "exintro": True,
            "explaintext": True,
            "redirects": 1,
            "titles": title
        }

        try:
            response = self.session.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get("query", {}).get("pages", {})
            if not pages:
                return None
            
            # The API returns pages keyed by page ID. -1 indicates missing.
            for page_id, page_data in pages.items():
                if page_id == "-1":
                    return None
                
                return {
                    "title": page_data.get("title"),
                    "context": page_data.get("extract"),
                    "url": page_data.get("fullurl"),
                    "updated_at": page_data.get("touched")
                }
                
        except requests.RequestException as e:
            print(f"Error fetching data for {title}: {e}")
            return None
            
        return None
