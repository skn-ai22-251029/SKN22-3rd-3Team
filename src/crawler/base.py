from abc import ABC, abstractmethod
from typing import Any, List, Dict

class BaseCrawler(ABC):
    """
    Abstract base class for all crawlers.
    This interface ensures consistency and allow for future automation/scheduling.
    """

    @abstractmethod
    def crawl(self) -> List[Dict[str, Any]]:
        """
        Executes the crawling logic.
        
        Returns:
            List[Dict[str, Any]]: A list of collected data dictionaries.
        """
        pass

    @abstractmethod
    def save(self, data: List[Dict[str, Any]], filepath: str):
        """
        Saves the crawled data to a file.
        
        Args:
            data (List[Dict[str, Any]]): The data to save.
            filepath (str): The destination file path.
        """
        pass
