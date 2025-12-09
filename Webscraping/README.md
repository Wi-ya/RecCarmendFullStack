# Webscraping Module Architecture

## Overview

This module implements a **Scraper Interface Pattern** (similar to Java interfaces) that makes the scraping system extensible and maintainable.

## Architecture

```
Webscraping/
├── scraper_interface.py      # Abstract base class (like Java interface)
├── carpages_scraper.py      # CarPages.ca implementation
├── autotrader_scraper.py    # AutoTrader template (to be implemented)
└── main.py                  # Original scraper (can be deprecated)

Controller/
└── scraping_controller.py   # Uses scrapers from Webscraping module
```

## Design Pattern: Interface-Based Scraping

### 1. **Scraper Interface** (`scraper_interface.py`)

Python's equivalent of a Java interface using `abc.ABC`:

```python
class Scraper(ABC):
    @abstractmethod
    def scrapeWebsite(self) -> List[Dict[str, Any]]:
        """All scrapers must implement this method"""
        pass
    
    @abstractmethod
    def get_scraper_name(self) -> str:
        """Return scraper identifier"""
        pass
```

**Benefits:**
- ✅ Ensures all scrapers have the same interface
- ✅ Makes code extensible (easy to add new scrapers)
- ✅ Enables polymorphism (controllers can use any scraper)
- ✅ Improves testability (can mock scrapers easily)

### 2. **Scraper Implementations**

Each scraper class implements the `Scraper` interface:

- **`CarPagesScraper`**: Implements scraping for carpages.ca
- **`AutoTraderScraper`**: Template for AutoTrader (to be implemented)
- **Future scrapers**: Just implement `Scraper` interface

### 3. **Controller Usage**

Controllers in the `Controller/` folder use scrapers:

```python
from Webscraping.carpages_scraper import CarPagesScraper

scraper = CarPagesScraper()
listings = scraper.scrapeWebsite()  # Interface method
```

## Why This Structure?

### ✅ **Separation of Concerns**
- **Webscraping/**: Contains scraping logic (business logic)
- **Controller/**: Orchestrates scraping (coordination layer)
- **Database_Model_Connection/**: Handles data persistence
- **View/**: Handles UI/API endpoints

### ✅ **Extensibility**
To add a new scraper:
1. Create a new file: `Webscraping/new_scraper.py`
2. Implement the `Scraper` interface
3. Add it to `Controller/scraping_controller.py`
4. Done! No need to modify existing code

### ✅ **Testability**
- Can test scrapers independently
- Can mock scrapers in controllers
- Can swap scrapers easily

## Usage Examples

### Using a Scraper Directly

```python
from Webscraping.carpages_scraper import CarPagesScraper

scraper = CarPagesScraper()
listings = scraper.scrapeWebsite()
print(f"Scraped {len(listings)} listings")
```

### Using Controller

```python
from Controller.scraping_controller import ScrapingController

controller = ScrapingController()
listings = controller.scrape_website("carpages")
```

## Adding a New Scraper

1. **Create scraper file**: `Webscraping/new_scraper.py`
   ```python
   from scraper_interface import Scraper
   
   class NewScraper(Scraper):
       def get_scraper_name(self) -> str:
           return "NewScraper"
       
       def scrapeWebsite(self) -> List[Dict[str, Any]]:
           # Your scraping logic here
           return listings
   ```

2. **Add to Controller**: Update `Controller/scraping_controller.py`
   ```python
   from Webscraping.new_scraper import NewScraper
   
   self.scrapers = {
       "carpages": CarPagesScraper(),
       "new": NewScraper(),  # Add here
   }
   ```

3. **Done!** The controller can now use your new scraper.

## Migration from Old Code

The original `main.py` can be kept for reference or gradually migrated:

- **Option 1**: Keep `main.py` as-is (backward compatibility)
- **Option 2**: Refactor `main.py` to use `CarPagesScraper` class
- **Option 3**: Deprecate `main.py` and use controller instead

## Benefits Summary

| Benefit | Description |
|---------|-------------|
| **Extensibility** | Easy to add new scrapers without changing existing code |
| **Maintainability** | Clear separation between scraping logic and orchestration |
| **Testability** | Can test scrapers independently |
| **Polymorphism** | Controllers work with any scraper implementation |
| **Type Safety** | Interface ensures consistent method signatures |

