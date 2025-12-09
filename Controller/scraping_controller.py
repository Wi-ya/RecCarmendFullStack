"""
Scraping Controller
Orchestrates scraping operations using scrapers from the Webscraping module.
This demonstrates how Controllers use the Scraper interface.
"""
import os
import sys

# Add parent directory to path to import from Webscraping
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from Webscraping.scraper_interface import Scraper
from Webscraping.carpages_scraper import CarPagesScraper
# Future scrapers can be imported here:
# from Webscraping.autotrader_scraper import AutoTraderScraper
# from Webscraping.kijiji_scraper import KijijiScraper


class ScrapingController:
    """
    Controller that manages scraping operations.
    Uses the Scraper interface to work with any scraper implementation.
    Scrapers create CSV files directly - they don't return data.
    """
    
    def __init__(self):
        """Initialize the controller with available scrapers."""
        self.scrapers: dict[str, Scraper] = {
            "carpages": CarPagesScraper(),
            # Add more scrapers here as they're implemented:
            # "autotrader": AutoTraderScraper(),
            # "kijiji": KijijiScraper(),
        }
    
    def scrape_all_websites(self) -> None:
        """
        Run all available scrapers.
        Each scraper creates CSV files directly - no return values.
        """
        for scraper_name, scraper in self.scrapers.items():
            print(f"\n{'='*60}")
            print(f"Starting {scraper.get_scraper_name()} scraper...")
            print(f"{'='*60}\n")
            
            try:
                scraper.scrapeWebsite()
                print(f"\n✅ {scraper.get_scraper_name()} completed successfully")
            except Exception as e:
                print(f"\n❌ {scraper.get_scraper_name()} failed: {e}")
    
    def scrape_website(self, scraper_name: str) -> None:
        """
        Run a specific scraper by name.
        The scraper creates CSV files directly - no return value.
        
        Args:
            scraper_name: Name of the scraper (e.g., "carpages")
        """
        if scraper_name not in self.scrapers:
            print(f"❌ Scraper '{scraper_name}' not found.")
            print(f"   Available scrapers: {', '.join(self.scrapers.keys())}")
            return
        
        scraper = self.scrapers[scraper_name]
        print(f"\nStarting {scraper.get_scraper_name()} scraper...\n")
        
        try:
            scraper.scrapeWebsite()
            print(f"\n✅ {scraper.get_scraper_name()} completed successfully")
        except Exception as e:
            print(f"\n❌ {scraper.get_scraper_name()} failed: {e}")
    
    def get_available_scrapers(self) -> list[str]:
        """Return list of available scraper names."""
        return list(self.scrapers.keys())


# Example usage
if __name__ == "__main__":
    controller = ScrapingController()
    
    # Option 1: Scrape a specific website
    print("Available scrapers:", controller.get_available_scrapers())
    controller.scrape_website("carpages")
    
    # Option 2: Scrape all websites
    # controller.scrape_all_websites()

