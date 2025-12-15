# Webscraping

Web scraping module for collecting car listings.

**Main Files:**
- `scraper_interface.py` - Abstract base class for scrapers
- `carpages_scraper.py` - CarPages.ca scraper implementation

**What it does:**
- Scrapes car listings from websites (CarPages.ca)
- Saves data to CSV files in the `data/` folder
- Uses Selenium for browser automation and moving through pages and categories
- Extensible design for adding more scrapers
