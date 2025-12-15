import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import scrapers - works both as module and script
try:
    from Webscraping.scraper_interface import Scraper
    from Webscraping.carpages_scraper import CarPagesScraper
except ImportError:
    try:
from ..Webscraping.scraper_interface import Scraper
from ..Webscraping.carpages_scraper import CarPagesScraper
    except ImportError:
        raise ImportError("Could not import Webscraping module. Make sure the project structure is correct.")

# Future scrapers can be imported here:



class ScrapingController:
    """
    Controller that manages scraping operations.
    Uses the Scraper interface to work with any scraper implementation.
    Scrapers create CSV files directly - they don't return data.
    """
    
    def __init__(self):
        """Initialize the controller with available scrapers. All scrapers are imported from the Webscraping module."""
        self.scrapers: dict[str, Scraper] = {
            "carpages": CarPagesScraper(),
            # Add more scrapers here if they're implemented
            # Feature for extendibility and modularity.
        }
    
    def scrape_all_websites(self) -> None:
        """
        Run all available scrapers.
        Each scraper creates CSV files directly - no return values.
        """
        for scraper_name, scraper in self.scrapers.items():

            print(f"Starting {scraper.get_scraper_name()} scraper...")
  
            
            try:
                scraper.scrapeWebsite()
                print(f"{scraper.get_scraper_name()} completed successfully")
            except Exception as e:
                print(f"{scraper.get_scraper_name()} failed: {e}")
    
    def scrape_website(self, scraper_name: str) -> None:
        """
        Run a specific scraper by name.
        The scraper creates CSV files directly - no return value.
        """
        if scraper_name not in self.scrapers:
            print(f"Scraper '{scraper_name}' not found.")
            print(f"Available scrapers: {', '.join(self.scrapers.keys())}")
            return
        
        scraper = self.scrapers[scraper_name]
        print(f"\nStarting {scraper.get_scraper_name()} scraper...\n")
        
        try:
            scraper.scrapeWebsite()
            print(f"{scraper.get_scraper_name()} completed successfully")
        except Exception as e:
            print(f"{scraper.get_scraper_name()} failed: {e}")
    
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

