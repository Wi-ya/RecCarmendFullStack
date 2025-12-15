# Sequence Diagram Method Mapping

## Method Verification: Sequence Diagram → Code

### ✅ Verified Methods

1. **User → FrontendService**
   - Diagram: `searchCars("red SUV under $30k")`
   - Code: `FrontendService.search_cars(query: str, ...)`
   - Status: ✅ EXISTS

2. **FrontendService → BackendService**
   - Diagram: `POST /api/search {query: "red SUV under $30k"}`
   - Code: Flask route calls `BackendService.ai_search(user_query: str)`
   - Status: ✅ EXISTS

3. **BackendService → CohereAPI**
   - Diagram: `co.chat(messages)`
   - Code: `CohereAPI.parse_car_query(user_prompt: str)` → internally calls `self.client.chat()`
   - Status: ✅ EXISTS (internal implementation)

4. **CohereAPI → BackendService**
   - Diagram: Returns `parsed_params {make: null, price: 30000, bodyType: "SUV", color: "red"}`
   - Code: `parse_car_query()` returns dict with parsed parameters
   - Status: ✅ EXISTS

5. **BackendService → SupabaseService**
   - Diagram: `sortDB(...)`
   - Code: `SupabaseService.search_cars(...)`
   - Status: ⚠️ NAME MISMATCH (functionality exists, but method name differs)

6. **SupabaseService → BackendService**
   - Diagram: Returns `cars[] [{id: 1, make: "Toyota", ...}]`
   - Code: `search_cars()` returns list of car dictionaries
   - Status: ✅ EXISTS

7. **BackendService → PexelsAPI (in loop)**
   - Diagram: `get_car_image_url(...)`
   - Code: `PexelsAPI.get_car_image_url(make, model, year, color)`
   - Status: ✅ EXISTS

8. **PexelsAPI → BackendService**
   - Diagram: Returns `image_url`
   - Code: `get_car_image_url()` returns str (image URL)
   - Status: ✅ EXISTS

9. **BackendService self-call**
   - Diagram: `format_car_results(cars)`
   - Code: `BackendService.format_car_results(cars: List[Dict])`
   - Status: ✅ EXISTS

10. **BackendService → FrontendService**
    - Diagram: `jsonify(response_data)`
    - Code: Flask route returns `jsonify(response_data)`
    - Status: ✅ EXISTS (handled by Flask route)

11. **FrontendService self-call**
    - Diagram: `normalizeCar(car)`
    - Code: `FrontendService.normalize_car(car: Dict)`
    - Status: ✅ EXISTS

## Issues Found

### Issue 1: Method Name Mismatch
- **Diagram shows**: `sortDB(...)`
- **Code has**: `SupabaseService.search_cars(...)`
- **Solution**: Add `sortDB()` as an alias method in SupabaseService for diagram consistency

