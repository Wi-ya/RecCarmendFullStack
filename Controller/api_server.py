# -*- coding: utf-8 -*-
"""
ReCarmend API Server
REST API for car recommendation system using AI-powered and filtered search.
"""

import os
import warnings
import requests
import hashlib
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import cohere
from supabase import create_client, Client

# Suppress Pydantic V1 compatibility warning from cohere library
warnings.filterwarnings("ignore", message=".*Pydantic V1.*")

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure CORS - allow requests from frontend
CORS(app, origins=["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:5001"])

# Initialize Supabase client
DB_URL = os.getenv("DB_URL")
DB_API_KEY = os.getenv("DB_API_KEY")

if not DB_URL or not DB_API_KEY:
    raise ValueError(
        "Missing Supabase credentials in .env file. "
        "Please add:\n"
        "DB_URL=https://your-project.supabase.co\n"
        "DB_API_KEY=your-service-role-key\n\n"
        "Get these from: Supabase Dashboard → Settings → API"
    )

try:
    print("Connecting to Supabase database...")
    supabase: Client = create_client(DB_URL, DB_API_KEY)
    print("✅ Connected to Supabase database")
except Exception as e:
    raise ConnectionError(f"Failed to connect to Supabase: {e}")

# Initialize Cohere client
cohere_api_key = os.getenv("COHERE_API_KEY")
if not cohere_api_key:
    raise ValueError(
        "COHERE_API_KEY not found in .env file. "
        "Please create a .env file in the Controller directory with: COHERE_API_KEY=your-api-key"
    )

co = cohere.ClientV2(cohere_api_key)
print("✅ Connected to Cohere API")


def safeInt(x, default=0):
    """Safely convert value to integer."""
    try:
        return int(float(str(x).replace(",", "")))
    except:
        return default


def get_car_image_url(make, model, year=None, color=None):
    """
    Fetch a car image using Pexels API (free, easy setup) or fallback to placeholder.
    Returns image URL or default car image if not found.
    
    NOTE: This function is called only for the 10 cars returned from the database query,
    not for all cars in the database. This ensures efficient image fetching.
    
    Setup: Get free API key from https://www.pexels.com/api/ (takes 30 seconds)
    Add to .env: PEXELS_API_KEY=your_key_here
    
    Args:
        make: Car manufacturer (e.g., "Toyota", "Ford")
        model: Car model (e.g., "Camry", "F-150")
        year: Car year (e.g., 2020)
        color: Car color (optional, e.g., "red", "blue")
    """
    try:
        # Clean and validate inputs
        make = str(make).strip() if make else ""
        model = str(model).strip() if model else ""
        year = int(year) if year and str(year).isdigit() else None
        color = str(color).strip().lower() if color else None
        
        # Skip if essential info is missing
        if not make or not model:
            print(f"Skipping image search - missing make or model: make={make}, model={model}")
            return get_fallback_image(make, model, year)
        
        # Try Pexels API first (free, 200 requests/hour, easy signup)
        # OPTIMIZED: Only try 1 query to conserve API calls, but make it VERY specific for cars only
        pexels_key = os.getenv("PEXELS_API_KEY")
        if pexels_key:
            # Build ONLY the most specific query - ALWAYS include "car" and exclude motorcycles/models
            # Format: "year make model color automobile car" - multiple car keywords to be explicit
            best_query = None
            if year and year > 0:
                if color:
                    # Most specific: year + make + model + color + multiple car keywords
                    best_query = f"{year} {make} {model} {color} automobile car vehicle"
                else:
                    # Specific: year + make + model + multiple car keywords
                    best_query = f"{year} {make} {model} automobile car vehicle"
            else:
                # Fallback: make + model + multiple car keywords (no year)
                best_query = f"{make} {model} automobile car vehicle"
            
            # Only try ONE query to save API calls
            try:
                pexels_search = "https://api.pexels.com/v1/search"
                headers = {"Authorization": pexels_key}
                search_params = {
                    "query": best_query,
                    "per_page": 15,  # Get more results to filter from
                    "orientation": "landscape"
                }
                
                response = requests.get(pexels_search, params=search_params, headers=headers, timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    photos = data.get("photos", [])
                    if photos and len(photos) > 0:
                        # STRICT filtering: Only accept images that are clearly cars
                        # Exclude: motorcycles, people/models, bikes, trucks (unless it's a pickup truck)
                        car_photos = []
                        exclude_keywords = ["motorcycle", "bike", "bicycle", "scooter", "model", "person", "people", "portrait", "fashion", "woman", "man", "girl", "boy"]
                        
                        for photo in photos:
                            alt_text = photo.get("alt", "").lower()
                            url = photo.get("url", "").lower()
                            photographer = photo.get("photographer", "").lower()
                            
                            # Skip if it contains excluded keywords (motorcycles, people, etc.)
                            if any(excluded in alt_text or excluded in url for excluded in exclude_keywords):
                                continue
                            
                            # Must contain car-related keywords
                            car_keywords = ["car", "automobile", "vehicle", "sedan", "suv", "coupe", "convertible", "hatchback", "sports car", "luxury car"]
                            if any(keyword in alt_text for keyword in car_keywords):
                                car_photos.append(photo)
                            # Also accept if make/model is mentioned (likely a car)
                            elif make.lower() in alt_text and model.lower() in alt_text:
                                car_photos.append(photo)
                        
                        # Use car-specific photos if available
                        if car_photos:
                            photos_to_use = car_photos
                        else:
                            # If no strict matches, use all photos but log a warning
                            photos_to_use = photos
                            print(f"⚠️ No strict car matches for {make} {model}, using all results")
                        
                        # Use hash of make+model+year to consistently pick different images for different cars
                        car_hash = int(hashlib.md5(f"{make}{model}{year}{color}".encode()).hexdigest(), 16)
                        photo_index = car_hash % len(photos_to_use)
                        image_url = photos_to_use[photo_index]["src"]["large"]
                        print(f"✅ Found CAR image for {year} {make} {model} ({color or 'any color'}) using query: '{best_query}'")
                        return image_url
                elif response.status_code == 401:
                    print(f"Pexels API key invalid. Check your PEXELS_API_KEY in .env")
                elif response.status_code == 429:
                    print(f"⚠️ Pexels rate limit reached. Using fallback images for remaining cars.")
                else:
                    print(f"Pexels API returned status {response.status_code} for query: '{best_query}'")
            except requests.exceptions.Timeout:
                print(f"Pexels API timeout for query: '{best_query}'")
            except Exception as e:
                print(f"Pexels API error for query '{best_query}': {e}")
        
        # Fallback to generic car images
        return get_fallback_image(make, model, year)
        
    except Exception as e:
        print(f"Error fetching car image for {make} {model}: {e}")
        return get_fallback_image(make, model, year)


def get_fallback_image(make, model, year):
    """Get a fallback car image when API search fails."""
    # Fallback: Use direct image URLs with more variety
    # These are free stock car images that work without API calls
    fallback_images = [
        "https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop",  # BMW
        "https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop",  # Red car
        "https://images.pexels.com/photos/1592384/pexels-photo-1592384.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop",  # White car
        "https://images.pexels.com/photos/1149137/pexels-photo-1149137.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop",  # Black car
        "https://images.pexels.com/photos/164634/pexels-photo-164634.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop",  # Sports car
        "https://images.pexels.com/photos/3802508/pexels-photo-3802508.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop",  # SUV
        "https://images.pexels.com/photos/1545743/pexels-photo-1545743.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop",  # Sedan
        "https://images.pexels.com/photos/1719647/pexels-photo-1719647.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop",  # Luxury car
        "https://images.pexels.com/photos/358070/pexels-photo-358070.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop",  # Convertible
        "https://images.pexels.com/photos/210019/pexels-photo-210019.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop",  # Classic car
    ]
    # Use a consistent fallback based on make/model/year hash for variety
    car_hash = int(hashlib.md5(f"{make}{model}{year}".encode()).hexdigest(), 16)
    selected_image = fallback_images[car_hash % len(fallback_images)]
    print(f"⚠️ Using fallback image for {year} {make} {model} (no specific image found)")
    return selected_image


def format_car_results(cars):
    """
    Format car results by:
    1. Filtering out 'gas' and 'unknown' values
    2. Adding color hex code for visualization
    3. Adding car image URLs
    
    IMPORTANT: This function should only be called on the limited results (max 10 cars)
    returned from the database query, not on all cars in the database.
    """
    if not cars:
        return []
    
    # Log how many cars we're processing (should be max 10)
    print(f"Formatting {len(cars)} car(s) - fetching images for these cars only")
    
    formatted_cars = []
    for car in cars:
        if not isinstance(car, dict):
            continue
        
        # Create a copy to avoid modifying original
        formatted_car = car.copy()
        
        # Remove or filter out 'gas' and 'unknown' values
        for key, value in formatted_car.items():
            if isinstance(value, str):
                value_lower = value.lower()
                # Filter out 'gas' and 'unknown' - set to None or remove
                if value_lower in ['gas', 'unknown', 'null', '']:
                    formatted_car[key] = None
                # Also filter if it's part of a field name (e.g., "fuel_type": "gas")
                elif key.lower() in ['fuel', 'fuel_type', 'fueltype'] and value_lower == 'gas':
                    formatted_car[key] = None
        
        # Add color hex code for visualization
        if 'color' in formatted_car and formatted_car['color']:
            formatted_car['colorHex'] = get_color_hex(formatted_car['color'])
        else:
            formatted_car['colorHex'] = None
        
        # Fetch and add car image URL (only for the cars being returned)
        make = formatted_car.get('make', '')
        model = formatted_car.get('model', '')
        year = formatted_car.get('year')
        color = formatted_car.get('color')
        
        if make and model:
            # Only fetch image for this specific car (one of the 10 being returned)
            # Pass color to help find more specific images
            image_url = get_car_image_url(make, model, year, color)
            formatted_car['imageUrl'] = image_url
        else:
            # Default car image if make/model not available
            formatted_car['imageUrl'] = get_fallback_image(make or "car", model or "vehicle", year)
        
        formatted_cars.append(formatted_car)
    
    return formatted_cars


def get_color_hex(color_name):
    """Map color name to hex code for visualization."""
    if not color_name:
        return None
    
    color_map = {
        'black': '#000000',
        'white': '#FFFFFF',
        'red': '#FF0000',
        'blue': '#0000FF',
        'green': '#008000',
        'yellow': '#FFFF00',
        'orange': '#FFA500',
        'purple': '#800080',
        'pink': '#FFC0CB',
        'brown': '#A52A2A',
        'beige': '#F5F5DC',
        'gray': '#808080',
        'grey': '#808080',
        'silver': '#C0C0C0',
        'gold': '#FFD700',
        'tan': '#D2B48C',
        'burgundy': '#800020',
        'navy': '#000080',
        'teal': '#008080',
        'maroon': '#800000',
    }
    
    color_lower = str(color_name).lower().strip()
    # Check for exact match first
    if color_lower in color_map:
        return color_map[color_lower]
    
    # Check if color name contains any of the mapped colors
    for mapped_color, hex_code in color_map.items():
        if mapped_color in color_lower:
            return hex_code
    
    # Default to a neutral gray if no match
    return '#808080'


def sortDB(maximumPrice, maximumMileage, color, make, model, minYear, maxYear, carType, return_has_more=False):
    """
    Query the database for cars matching the specified criteria.
    Returns up to 10 matching results.
    
    IMPORTANT: This function limits results to 10 cars BEFORE fetching images.
    Images are only fetched for the 10 cars returned, not for all cars in the database.
    
    Args:
        return_has_more: If True, returns tuple (results, has_more, total_count)
    """
    userDB = []
    
    # Normalize input values
    color = color.lower() if color and color.lower() not in ["null", "", None] else None
    make = make.lower() if make and make.lower() not in ["null", "", None] else None
    model = model.lower() if model and model.lower() not in ["null", "", None] else None
    carType = carType.lower() if carType and carType.lower() not in ["null", "", None] else None
    
    # Build the query with filters
    query = supabase.table('CarListings').select('*', count='exact')
    
    # Apply numeric filters
    if maximumPrice and maximumPrice > 0:
        query = query.lte('price', maximumPrice)
    if maximumMileage and maximumMileage > 0:
        query = query.lte('mileage', maximumMileage)
    if minYear and minYear > 0:
        query = query.gte('year', minYear)
    if maxYear and maxYear > 0:
        query = query.lte('year', maxYear)
    
    # Apply text filters (case-insensitive search)
    if color:
        query = query.ilike('color', f'%{color}%')
    if make:
        query = query.ilike('make', f'%{make}%')
    if model:
        query = query.ilike('model', f'%{model}%')
    
    # Handle carType - try both possible column names
    if carType:
        # Try body_type column first (most likely column name)
        try:
            query_with_cartype = query.ilike('body_type', f'%{carType}%')
            response = query_with_cartype.limit(10).execute()
            if response.data and len(response.data) > 0:
                results = format_car_results(response.data)
                if return_has_more:
                    total_count = response.count if hasattr(response, 'count') else len(response.data)
                    has_more = total_count > 10
                    return results, has_more, total_count
                return results
        except Exception as e:
            # If body_type fails, try carType column
            try:
                query_with_cartype = query.ilike('carType', f'%{carType}%')
                response = query_with_cartype.limit(10).execute()
                if response.data and len(response.data) > 0:
                    results = format_car_results(response.data)
                    if return_has_more:
                        total_count = response.count if hasattr(response, 'count') else len(response.data)
                        has_more = total_count > 10
                        return results, has_more, total_count
                    return results
            except Exception as e2:
                # If both fail, continue without carType filter
                print(f"Warning: Could not filter by car type '{carType}', showing all types")
    
    # Execute query (either no carType filter, or carType filter failed)
    try:
        response = query.limit(10).execute()
        userDB = response.data if response.data else []
        
        # Check if there are more results
        if return_has_more:
            total_count = response.count if hasattr(response, 'count') else len(userDB)
            has_more = total_count > 10
            results = format_car_results(userDB)
            return results, has_more, total_count
        
        # Format results: filter out 'gas'/'unknown', add color hex codes, and add images
        return format_car_results(userDB)
    except Exception as e:
        print(f"Error querying database: {e}")
        if return_has_more:
            return [], False, 0
        return []


def aiSearch(prompt):
    """
    Use Cohere AI to parse user's natural language query and search for cars.
    """
    try:
        # Enhanced prompt for Cohere
        enhanced_prompt = (
            prompt + 
            " Please take the prompt above and isolate the desired model, make, year range, "
            "maximum price, color, maximum mileage, and car type. "
            "If the prompt given does not relate to cars please ignore the prompt entirely and "
            "print nothing more than 'this prompt does not relate to cars'. "
            "If an exact color is not specified please return it as null, a color should be given "
            "if it is a very general color ex(red orange yellow green blue, black, white, silver "
            "NOT matte black or platinum silver) if the given prompt does not include information "
            "for Color, Make or Model and car types please return it as 'null'. "
            "If the prompt does not specify an exact number for miles or price use judgement of what "
            "the prompt seems to want and give a number for example if asked for a car with low mileage "
            "do NOT return 'low mileage' return something like 5000. "
            "If multiple makes are given please select only 1. "
            "Possible car types are Convertible, Coupe, Hatchback, hybrid, Sedan, SUV, Minivan, Pickup Truck, "
            "if one of these is not specified please return null. "
            "If it does not include information for Maximum Price, Maximum Mileage, or Min year please "
            "return it as 0, for max year please return the current year(2026). "
            "Do not include any additional text. The current year is 2026. "
            "Please format the output as: "
            "Maximum Price: Maximum Mileage: Car type: Color: Make: Model: Minimum Year: Maximum Year:"
        )
        
        response = co.chat(
            model="command-a-03-2025",
            messages=[{"role": "user", "content": enhanced_prompt}]
        )
        
        # Handle Cohere API response - check different possible response formats
        try:
            if hasattr(response, 'text'):
                rawText = response.text
            elif hasattr(response, 'message') and hasattr(response.message, 'content'):
                if isinstance(response.message.content, list) and len(response.message.content) > 0:
                    rawText = response.message.content[0].text if hasattr(response.message.content[0], 'text') else str(response.message.content[0])
                else:
                    rawText = str(response.message.content)
            else:
                rawText = str(response)
        except Exception as e:
            print(f"Error parsing Cohere response: {e}")
            rawText = ""
        
        # Check if response indicates non-car related query
        if "does not relate to cars" in rawText.lower():
            return {"error": "Your query does not relate to cars. Please try again with a car-related search."}
        
        # Parse the response
        parsed = {}
        for line in rawText.split("\n"):
            if ":" in line:
                key, value = map(str.strip, line.split(":", 1))
                parsed[key.strip()] = value.strip()
        
        maximumPrice = safeInt(parsed.get("Maximum Price", 0))
        maximumMileage = safeInt(parsed.get("Maximum Mileage", 0))
        minYear = safeInt(parsed.get("Minimum Year", 0))
        maxYear = safeInt(parsed.get("Maximum Year", 2026))
        
        color = parsed.get("Color", "Null")
        make = parsed.get("Make", "Null")
        model = parsed.get("Model", "Null")
        carType = parsed.get("Car type", "Null")
        
        # Search database with parsed parameters
        # Note: aiSearch doesn't return has_more info, but the API endpoints will handle it
        results = sortDB(maximumPrice, maximumMileage, color, make, model, minYear, maxYear, carType, return_has_more=False)
        return results
        
    except Exception as e:
        print(f"Error in AI search: {e}")
        return {"error": f"AI search failed: {str(e)}"}


# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "message": "ReCarmend API is running"})


@app.route('/api/search', methods=['POST'])
def search():
    """
    AI-powered search endpoint.
    Accepts: { "query": "user's natural language description" }
    Returns: { "cars": [...], "count": 10, "query": "original query" }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({"error": "Missing 'query' field in request body"}), 400
        
        query = data['query'].strip()
        
        if not query:
            return jsonify({"error": "Query cannot be empty"}), 400
        
        # Perform AI search
        results = aiSearch(query)
        
        # Check if there was an error
        if isinstance(results, dict) and 'error' in results:
            return jsonify(results), 400
        
        # For AI search, we can't easily get the total count without re-parsing
        # So we'll check if we got exactly 10 results (likely means there are more)
        has_more = len(results) == 10
        total_count = len(results)
        
        # Format response
        response_data = {
            "cars": results,
            "count": len(results),
            "query": query,
            "hasMore": has_more,
            "totalCount": total_count
        }
        
        if has_more:
            response_data["message"] = "Showing 10 results. More cars available - search again to see more."
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"Error in /api/search: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route('/api/search/filtered', methods=['POST'])
def filtered_search():
    """
    Filter-based search endpoint.
    Accepts: { 
        "filters": {
            "maxPrice": 35000,
            "maxMileage": 50000,
            "minYear": 2020,
            "maxYear": 2026,
            "bodyTypes": ["SUV"],
            "makes": ["Toyota"],
            "colors": ["Red"],
            "models": ["RAV4"]
        }
    }
    Returns: { "cars": [...], "count": 10 }
    """
    try:
        data = request.get_json()
        
        if not data or 'filters' not in data:
            return jsonify({"error": "Missing 'filters' field in request body"}), 400
        
        filters = data['filters']
        
        # Extract filter values
        maximumPrice = safeInt(filters.get('maxPrice', 0))
        maximumMileage = safeInt(filters.get('maxMileage', 0))
        minYear = safeInt(filters.get('minYear', 0))
        maxYear = safeInt(filters.get('maxYear', 2026))
        
        # Handle multiple values (take first one for now, or join them)
        bodyTypes = filters.get('bodyTypes', [])
        carType = bodyTypes[0] if bodyTypes else None
        
        makes = filters.get('makes', [])
        make = makes[0] if makes else None
        
        models = filters.get('models', [])
        model = models[0] if models else None
        
        colors = filters.get('colors', [])
        color = colors[0] if colors else None
        
        # Search database
        results, has_more, total_count = sortDB(maximumPrice, maximumMileage, color, make, model, minYear, maxYear, carType, return_has_more=True)
        
        # Format response
        response_data = {
            "cars": results,
            "count": len(results),
            "hasMore": has_more,
            "totalCount": total_count
        }
        
        if has_more:
            response_data["message"] = f"Showing 10 of {total_count} results. Search again to see more cars."
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"Error in /api/search/filtered: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route('/api/cars', methods=['GET'])
def get_cars():
    """
    Get all cars (for testing/debugging).
    Optional query params: limit (default: 10)
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        
        response = supabase.table('CarListings').select('*').limit(limit).execute()
        cars = response.data if response.data else []
        
        # Format results: filter out 'gas'/'unknown', add color hex codes, and add images
        formatted_cars = format_car_results(cars)
        
        return jsonify({
            "cars": formatted_cars,
            "count": len(formatted_cars)
        }), 200
        
    except Exception as e:
        print(f"Error in /api/cars: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


if __name__ == '__main__':
    print("🚀 Starting ReCarmend API Server...")
    print("📡 API will be available at http://localhost:5001")
    print("📝 Endpoints:")
    print("   - POST /api/search - AI-powered search")
    print("   - POST /api/search/filtered - Filter-based search")
    print("   - GET /api/cars - Get all cars")
    print("   - GET /api/health - Health check")
    app.run(debug=True, host='0.0.0.0', port=5001)


