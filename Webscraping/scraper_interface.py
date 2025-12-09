"""
Scraper Interface (Abstract Base Class)
All scrapers must implement the scrapeWebsite() method.
Extendability and polymorphism so that same function can be called on different websites.
"""
from abc import ABC, abstractmethod


class Scraper(ABC):

    @abstractmethod
    def scrapeWebsite(self) -> None:
        """
        Scrape data from a website and save results to CSV files.
        This method does not return any data - it only creates CSV files.
        
        Raises:
            Exception: If scraping fails for any reason
        """
        pass
    
    @abstractmethod
    def get_scraper_name(self) -> str:
        """
        Return the name/identifier of this scraper.
        
        Returns:
            str: Name of the scraper (e.g., "CarPages", "AutoTrader")
        """
        pass

