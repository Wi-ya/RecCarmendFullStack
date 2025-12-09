"""
AutoTrader Scraper Template
Example of how to create a new scraper that implements the Scraper interface.
Replace this with actual AutoTrader scraping logic.
"""
from scraper_interface import Scraper


class AutoTraderScraper(Scraper):
    """
    Scraper for AutoTrader website.
    Implements the Scraper interface.
    
    TODO: Implement actual scraping logic for AutoTrader
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the AutoTrader scraper.
        
        Args:
            data_dir: Directory to save CSV files. If None, uses ../data
        """
        self.data_dir = data_dir
        # TODO: Set up any AutoTrader-specific configuration here
    
    def get_scraper_name(self) -> str:
        """Return the name of this scraper."""
        return "AutoTrader"
    
    def scrapeWebsite(self) -> None:
        """
        Scrape AutoTrader and save results to CSV files.
        Implements the Scraper interface.
        """
        # TODO: Implement AutoTrader scraping logic here
        # Example structure:
        # 1. Navigate to AutoTrader website
        # 2. Handle cookies/captcha if needed
        # 3. Navigate through pages
        # 4. Extract car listings
        # 5. Save to CSV files with keys:
        #    ['year', 'make', 'model', 'price', 'mileage', 'color', 'url', 'body_type']
        
        print("⚠️  AutoTrader scraper not yet implemented")

