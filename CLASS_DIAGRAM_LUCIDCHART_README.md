# Class Diagram for Lucidchart

## How to Import

1. **Lucidchart supports PlantUML** - Copy the contents of `CLASS_DIAGRAM_LUCIDCHART.txt`
2. Go to Lucidchart → More Shapes → Software → UML
3. You can also:
   - Use PlantUML online editor (http://www.plantuml.com/plantuml/uml/) to generate an image
   - Import directly into Lucidchart if it supports PlantUML import
   - Use the text to manually create the diagram

## Alternative: Manual Import Format

If Lucidchart doesn't support PlantUML directly, here's a simpler format:

### Classes:

**Car (Abstract)**
- Attributes: make, model, year, price, mileage, body_type, color, url
- Methods: __init__, get_fuel_type() (abstract), to_dict()

**GasCar extends Car**
- Methods: get_fuel_type() → "Gas"

**ElectricCar extends Car**
- Attributes: battery_range
- Methods: __init__, get_fuel_type() → "Electric" or "Hybrid"

**CohereAPI**
- Attributes: client, api_key
- Methods: __init__, parse_car_query(), _extract_response_text(), _parse_response()

**PexelsAPI**
- Attributes: api_key, base_url
- Methods: __init__, get_car_image_url(), get_fallback_image(), _search_pexels(), _filter_car_photos()

**SupabaseService**
- Attributes: client, db_url
- Methods: __init__, search_cars(), get_all_cars(), sortDB(), clear_table(), reset_id_sequence(), upload_data(), upload_all_listings(), _prepare_data()

**BackendService**
- Attributes: cohere_api, supabase_service, pexels_api
- Methods: __init__, ai_search(), filtered_search(), format_car_results(), get_color_hex(), _create_car_from_dict(), _safe_int()

**FrontendService**
- Attributes: api_url, name
- Methods: __init__, search_cars(), search_cars_with_filters(), normalize_car(), render_car_cards(), get_name()
- Note: Represents the Frontend/View component (actual implementation is TypeScript/React)

**api_server (Flask App)**
- Attributes: app, backend_service
- Methods: search(), filtered_search(), get_all_cars(), health_check()

**Scraper (Abstract)**
- Methods: scrapeWebsite() (abstract), get_scraper_name() (abstract)

**CarPagesScraper extends Scraper**
- Attributes: data_dir, driver, all_rows, category_rows
- Methods: __init__, scrapeWebsite(), get_scraper_name(), _create_driver(), _scrape_carpages_ca(), _navigate_category(), _navigate_page(), _extract_data_from_listing(), _normalize_color(), _cookie_handler(), _no_location_options(), _bypass_captcha(), _write_rows_to_csv(), _save_to_csv()

**ScrapingController**
- Attributes: scrapers (dict[str, Scraper])
- Methods: __init__, scrape_all_websites(), scrape_website(), get_available_scrapers()

**DataMaintenance**
- Attributes: controller (ScrapingController), last_run (Optional[datetime])
- Methods: __init__, run_weekly_update(), schedule_weekly_updates(), run_scheduler(), run_manual_update()

### Relationships:

- GasCar → Car (inheritance)
- ElectricCar → Car (inheritance)
- BackendService → CohereAPI (composition/uses)
- BackendService → SupabaseService (composition/uses)
- BackendService → PexelsAPI (composition/uses)
- BackendService → Car (creates via factory)
- api_server → BackendService (composition/uses)
- api_server → FrontendService (sends responses)
- CarPagesScraper → Scraper (implements/extends)
- ScrapingController → Scraper (composition/uses)
- DataMaintenance → ScrapingController (composition/uses)
- DataMaintenance → SupabaseService (uploads data)

