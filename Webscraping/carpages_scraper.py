"""
carpages.ca Scraper Implementation
Implements the Scraper interface to scrape car listings from carpages.ca website.
"""
import csv
import os
import random
import time
from collections import defaultdict
from time import sleep

from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import undetected_chromedriver as uc

from scraper_interface import Scraper


class CarPagesScraper(Scraper):
     # Implements the Scraper Interface
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the CarPages scraper.
        Passes directory to save CSV files.
        """
        if data_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_parent = os.path.dirname(current_dir)
            data_dir = os.path.join(project_parent, "data")
        
        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        self.driver = None
        self.all_rows = []
        self.category_rows = defaultdict(list)
    
    def get_scraper_name(self) -> str:
        """Return the name of this scraper."""
        return "CarPages"
    
    def scrapeWebsite(self) -> None:
        
        #Main scraping method - implements the Scraper interface.
        
        self.all_rows = []
        self.category_rows = defaultdict(list)
        
        # Create driver
        self.driver = self._create_driver()
        
        try:
            # Perform the actual scraping
            self._scrape_carpages_ca()
        finally:
            if self.driver:
                self.driver.quit()
        
        # Save to CSV files
        if self.all_rows:
            self._save_to_csv()
            print(f"Saved {len(self.all_rows)} listings to all_listings.csv and {len(self.category_rows)} category files.")
        else:
            print("No listings scraped; CSVs not written.")
    
    def _create_driver(self):
        """Create a new Chrome driver. Used when restarting browser between categories to reset cache."""
        driver = uc.Chrome(options=self._no_location_options(), version_main=142)
        driver.set_page_load_timeout(15)
        driver.implicitly_wait(5)
        return driver
    
    def _scrape_carpages_ca(self):
        """Internal method to scrape carpages.ca"""
        # Open webpage and wait to load
        self.driver.get("https://www.carpages.ca")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Handle cookie requests before scraping
        self._cookie_handler(self.driver)
        
        # Get URL links for each category
        category_container = self.driver.find_element(By.CSS_SELECTOR, "div.category-jellybeans")
        categories = category_container.find_elements(By.TAG_NAME, "a")
        raw_urls = [c.get_attribute("href") for c in categories if c.get_attribute("href")]
        
        # Remove duplicates
        category_urls = list(dict.fromkeys(raw_urls))
        visited_urls = set()
        
        # Access each category webpage with intercategory restart
        for idx, category_url in enumerate(category_urls):
            if category_url in visited_urls:
                print(f"Skipping already visited category: {category_url}")
                continue
            
            # Restart browser between categories (except first one)
            if idx > 0:
                print(f"\n >> Restarting browser between categories (cache reset)...")
                self.driver.quit()
                sleep(2)
                self.driver = self._create_driver()
                
                # Re-initialize: go to homepage and handle cookies
                self.driver.get("https://www.carpages.ca")
                try:
                    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                except TimeoutException:
                    pass
                self._cookie_handler(self.driver)
                print(" >> Browser restarted and ready.")
            
            try:
                self._navigate_page.count = 0
                print(f"\n >> Requesting category {idx + 1}/{len(category_urls)}: {category_url}...", end=" ", flush=True)
                self.driver.get(category_url)
                try:
                    WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                except TimeoutException:
                    pass
                print("Done.", flush=True)
                
                self._bypass_captcha(self.driver)
                self._navigate_category(category_url)
                sleep(random.uniform(2, 4))
                visited_urls.add(category_url)
                
            except TimeoutException:
                print("Page load timed out! Forcing stop to continue scraping.")
                self.driver.execute_script("window.stop();")
                self._bypass_captcha(self.driver)
                self._navigate_category(category_url)
                visited_urls.add(category_url)
                
            except Exception as e:
                print(f"Skip {category_url} because of error: {e}")
                continue
    
    def _navigate_category(self, category_url):
        """Navigate through pages in the same category and make it restart every 50 pages to reset cache."""
        print(f"Navigating in {self.driver.title}")
        self._navigate_page.count = 0
        
        INTRACATEGORY_RESTART_INTERVAL = 50
        
        # Bypass CAPTCHA/Cloudflare challenges
        self._bypass_captcha(self.driver)
        
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
        except TimeoutException:
            print(" >> Warning: Page header not found, trying to continue...")
        
        # Get body_type once at the start, Normalize it to a consistent format.
        try:
            header_text = self.driver.find_element(By.TAG_NAME, "h1").text
            if "New and Used" in header_text:
                body_type = header_text.replace("New and Used ", "").replace(" for Sale", "")
            else:
                body_type = header_text
            if body_type == "Cars":
                body_type = "hybrid"
            elif "Hatchbacks" in body_type:
                body_type = "Hatchback"
            elif "SUV" in body_type:
                body_type = "SUV"
            elif "Minivan" in body_type:
                body_type = "Minivan"
            else:
                body_type = body_type[:-1]
        except Exception as e:
            print(f" >> Error extracting body_type: {e}")
            return
        
        # Scrape the first page
        last_container = self._navigate_page(body_type)
        if last_container is None:
            print(" >> Failed to load first page, skipping category.")
            return
        
        last_url = self.driver.current_url
        
        while True:
            try:
                # Intracategory restart
                if self._navigate_page.count > 0 and self._navigate_page.count % INTRACATEGORY_RESTART_INTERVAL == 0:
                    current_page_url = self.driver.current_url
                    print(f"\n >> Intracategory restart at page {self._navigate_page.count} (cache reset)...")
                    self.driver.quit()
                    sleep(2)
                    self.driver = self._create_driver()
                    
                    self.driver.get(current_page_url)
                    try:
                        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    except TimeoutException:
                        pass
                    self._bypass_captcha(self.driver)
                    self._cookie_handler(self.driver)
                    print(" >> Browser restarted, continuing from same page.")
                    
                    try:
                        last_container = self.driver.find_element(By.CSS_SELECTOR, "div[class*='tw:laptop:col-span-8']")
                    except Exception:
                        last_container = None
                
                try:
                    self._bypass_captcha(self.driver)
                except Exception:
                    pass
                
                # Try to move to next page
                next_link = self.driver.find_elements(By.LINK_TEXT, "→")
                proceed_to_next = False
                
                if next_link:
                    next_btn = next_link[0]
                    btn_class = next_btn.get_attribute("class") or ""
                    
                    if "disabled" not in btn_class and next_btn.is_enabled():
                        proceed_to_next = True
                
                if proceed_to_next:
                    prev_url = self.driver.current_url
                    try:
                        page_indicator = self.driver.find_element(By.CSS_SELECTOR, "span[class*='tw:font-bold']")
                        prev_page_text = page_indicator.text
                    except Exception:
                        prev_page_text = None
                    
                    try:
                        old_container = self.driver.find_element(By.CSS_SELECTOR, "div[class*='tw:laptop:col-span-8']")
                    except Exception:
                        old_container = None
                    
                    next_link[0].click()
                    
                    try:
                        def page_has_changed(driver):
                            if driver.current_url != prev_url:
                                return True
                            if old_container:
                                try:
                                    _ = old_container.tag_name
                                except:
                                    return True
                            if prev_page_text:
                                try:
                                    new_indicator = driver.find_element(By.CSS_SELECTOR, "span[class*='tw:font-bold']")
                                    if new_indicator.text != prev_page_text:
                                        return True
                                except:
                                    pass
                            return False
                        
                        WebDriverWait(self.driver, 4).until(page_has_changed)
                        WebDriverWait(self.driver, 3).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='tw:laptop:col-span-8']"))
                        )
                        print(" >> Page loaded successfully.")
                        
                        current_url = self.driver.current_url
                        if current_url != last_url or last_container is None:
                            last_container = self._navigate_page(body_type)
                            if last_container:
                                last_url = current_url
                    except TimeoutException:
                        try:
                            test_container = self.driver.find_element(By.CSS_SELECTOR, "div[class*='tw:laptop:col-span-8']")
                            current_url = self.driver.current_url
                            
                            page_changed = False
                            if prev_page_text:
                                try:
                                    new_indicator = self.driver.find_element(By.CSS_SELECTOR, "span[class*='tw:font-bold']")
                                    if new_indicator.text != prev_page_text:
                                        page_changed = True
                                except:
                                    pass
                            
                            if current_url != last_url or page_changed:
                                print(" >> Timeout on wait but content available, scraping...")
                                last_container = self._navigate_page(body_type)
                                if last_container:
                                    last_url = current_url
                            else:
                                print(" >> Page appears unchanged, continuing...")
                        except Exception:
                            print(" >> Page not ready yet, will retry...")
                            sleep(0.5)
                
                else:
                    print("No link found. Must be last page of category.")
                    rows_for_category = self.category_rows.get(body_type, [])
                    if rows_for_category:
                        # Randomize order before saving
                        randomized_category_rows = rows_for_category.copy()
                        random.shuffle(randomized_category_rows)
                        safe_name = body_type.lower().replace(" ", "_")
                        filename = f"car_listings_{safe_name}.csv"
                        filepath = os.path.join(self.data_dir, filename)
                        self._write_rows_to_csv(randomized_category_rows, filepath=filepath)
                        print(f"Saved {len(rows_for_category)} listings to {filepath}")
                    return
                    
            except Exception as e:
                print(f"Skip page because of error: {e}")
                return
    
    def _navigate_page(self, body_type):
        """Navigate a single page and extract listings"""
        if not hasattr(self._navigate_page, "count"):
            self._navigate_page.count = 0
        
        try:
            self._bypass_captcha(self.driver)
        except Exception:
            pass
        
        try:
            page_car_listing_container = WebDriverWait(self.driver, 8).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='tw:laptop:col-span-8']"))
            )
            self._navigate_page.count += 1
            print(f"Navigating page {self._navigate_page.count} in {self.driver.title}")
            
            car_listings = page_car_listing_container.find_elements(By.CSS_SELECTOR,
                    "div[class*='tw:flex'][class*='tw:p-6']")
            if not car_listings:
                print("No car listing found.")
            else:
                print(f"Found {len(car_listings)} car listings on this page.")
                for car_listing in car_listings:
                    self._extract_data_from_listing(car_listing, body_type)
            return page_car_listing_container
        except (NoSuchElementException, TimeoutException):
            return None
        except Exception as e:
            print(f"(Error navigating page: {e})")
            return None
    
    def _extract_data_from_listing(self, car_listing, body_type):
        """Extract data from a single car listing"""
        listing_header = car_listing.find_element(By.TAG_NAME, "h4").text
        year = listing_header.split(" ")[0]
        make = listing_header.split(" ")[1]
        model = listing_header.split(" ")[2]
        href_link = car_listing.find_element(By.TAG_NAME, "a").get_attribute("href")
        price = car_listing.find_element(By.CSS_SELECTOR,
                                         "span[class*='tw:font-bold tw:text-xl']").text
        
        # Skip listing if price says "CALL", since there is no point to scraping it.
        if price.upper().strip() == "CALL":
            return
        
        price_clean = price.replace("$", "").replace(",", "").strip()
        try:
            price = int(round(float(price_clean)))
        except (ValueError, TypeError):
            price = 0
        
        mileage_header_box = car_listing.find_element(By.CSS_SELECTOR,
                        "div[class*='tw:col-span-full tw:mobile-lg:col-span-6 tw:laptop:col-span-4']")
        mileage_box = mileage_header_box.find_element(By.CSS_SELECTOR,
                                                  "div[class*='tw:text-gray-500']")
        raw_mileage = mileage_box.text
        car_mileage = 0
        
        # Extract mileage, check if mileage exists, sometimes mileage is listed as "CALL" so we skip it.
        if "CALL" not in raw_mileage and raw_mileage.strip() != "":
            mileage_number_list = mileage_box.find_elements(By.CLASS_NAME, "number")
            temp_mileage = ""
            for num in mileage_number_list:
                temp_mileage += num.text
            
            clean_mileage = temp_mileage.replace(",", "").strip()
            if clean_mileage.isdigit():
                car_mileage = int(round(float(clean_mileage)))
        
        color_raw = car_listing.find_element(By.CSS_SELECTOR,
                                         "span[class*='tw:text-sm tw:font-bold']").text
        color = self._normalize_color(color_raw)
        
        row = {
            "year": year,
            "make": make,
            "model": model,
            "price": price,
            "mileage": car_mileage,
            "color": color,
            "url": href_link,
            "body_type": body_type
        }
        self.all_rows.append(row)
        self.category_rows[body_type].append(row)
    
    def _normalize_color(self, raw_color):
        """Normalize color to basic color term"""
        color_str = (raw_color or "").lower()
        basic_colors = [
            "black", "white", "red", "blue", "green", "yellow",
            "orange", "purple", "pink", "brown", "beige", "gray",
            "grey", "silver", "gold"
        ]
        
        for base in basic_colors:
            if base in color_str:
                if base in ("gray", "grey"):
                    return "gray"
                return base
        
        return raw_color.split()[0].lower() if raw_color else "Other"
    
    def _cookie_handler(self, driver):
        """Handle cookie consent banner, that shows up when you first visit the website."""
        try:
            print("Checking for cookie banner...")
            cookie_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(., 'Consent')] | //div[contains(text(), 'Consent') \
                    and @role='button']"))
            )
            cookie_btn.click()
            print("Cookie banner dismissed.")
            sleep(1)
        except Exception as e:
            print(f"Cookie banner skipped or not found. Details: {e}")
    
    def _no_location_options(self):
        """Create Chrome options with location/notification blocking, and running in the background."""
        chrome_options = Options()
        prefs = {
            "profile.default_content_setting_values.geolocation": 2,
            "profile.default_content_setting_values.notifications": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.page_load_strategy = 'none'
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--window-size=1920,1080")
        return chrome_options
    
    def _bypass_captcha(self, driver):
        """Handle CAPTCHA/Cloudflare challenges"""
        suspicious_titles = ["Just a moment", "Security Check", "Access denied", "Attention Required",
                             "Checking your browser", "reCAPTCHA", "Cloudflare"]
        accurate_titles = ["New and Used", "Carpages.ca"]
        
        max_wait = 10
        start_time = time.time()
        sound_played = False
        
        while True:
            current_title = driver.title
            different_page = any(t in current_title for t in suspicious_titles)\
                             or not any(t in current_title for t in accurate_titles)
            
            if not different_page:
                return
            
            elapsed = time.time() - start_time
            
            if elapsed >= max_wait:
                if not sound_played:
                    try:
                        os.system('afplay /System/Library/Sounds/Glass.aiff')
                        sound_played = True
                    except Exception:
                        pass
                
                print("\n" + "!" * 50)
                print(f"!!! STUCK ON: {current_title} !!!")
                print("Auto-redirect failed. Please solve manually in browser.")
                print("!" * 50 + "\n")
                
                input("Press Enter to resume script...")
                return
            
            if elapsed > 3:
                print(f" >> Waiting for page redirect: ({int(elapsed)}s)")
            time.sleep(1)
    
    def _write_rows_to_csv(self, rows, filepath="car_listings.csv"):
        """Write rows to a CSV file"""
        fieldnames = ["year", "make", "model", "price", "mileage", "color", "url", "body_type"]
        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    
    def _save_to_csv(self):
        """Save all scraped data to CSV files, with randomized order"""
        # Randomize order of all rows before saving
        randomized_all_rows = self.all_rows.copy()
        random.shuffle(randomized_all_rows)
        main_csv_path = os.path.join(self.data_dir, "all_listings.csv")
        self._write_rows_to_csv(randomized_all_rows, filepath=main_csv_path)
        
        fieldnames = ["year", "make", "model", "price", "mileage", "color", "url", "body_type"]
        for category, rows in self.category_rows.items():
            # Randomize order of category rows before saving
            randomized_rows = rows.copy()
            random.shuffle(randomized_rows)
            safe_name = category.lower().replace(" ", "_")
            filename = f"car_listings_{safe_name}.csv"
            filepath = os.path.join(self.data_dir, filename)
            with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(randomized_rows)

