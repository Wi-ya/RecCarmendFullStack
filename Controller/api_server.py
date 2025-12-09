# -*- coding: utf-8 -*-
"""
ReCarmend API Server
REST API for car recommendation system using AI-powered and filtered search.
"""

import os
import warnings
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
CORS(app, origins=["http://localhost:8080", "http://127.0.0.1:8080"])

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


def sortDB(maximumPrice, maximumMileage, color, make, model, minYear, maxYear, carType):
    """
    Query the database for cars matching the specified criteria.
    Returns up to 10 matching results.
    """
    userDB = []
    
    # Normalize input values
    color = color.lower() if color and color.lower() not in ["null", "", None] else None
    make = make.lower() if make and make.lower() not in ["null", "", None] else None
    model = model.lower() if model and model.lower() not in ["null", "", None] else None
    carType = carType.lower() if carType and carType.lower() not in ["null", "", None] else None
    
    # Build the query with filters
    query = supabase.table('CarListings').select('*')
    
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
                return response.data
        except Exception as e:
            # If body_type fails, try carType column
            try:
                query_with_cartype = query.ilike('carType', f'%{carType}%')
                response = query_with_cartype.limit(10).execute()
                if response.data and len(response.data) > 0:
                    return response.data
            except Exception as e2:
                # If both fail, continue without carType filter
                print(f"Warning: Could not filter by car type '{carType}', showing all types")
    
    # Execute query (either no carType filter, or carType filter failed)
    try:
        response = query.limit(10).execute()
        userDB = response.data if response.data else []
    except Exception as e:
        print(f"Error querying database: {e}")
        return []
    
    return userDB


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
        results = sortDB(maximumPrice, maximumMileage, color, make, model, minYear, maxYear, carType)
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
        
        # Format response
        return jsonify({
            "cars": results,
            "count": len(results),
            "query": query
        }), 200
        
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
        results = sortDB(maximumPrice, maximumMileage, color, make, model, minYear, maxYear, carType)
        
        # Format response
        return jsonify({
            "cars": results,
            "count": len(results)
        }), 200
        
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
        
        return jsonify({
            "cars": cars,
            "count": len(cars)
        }), 200
        
    except Exception as e:
        print(f"Error in /api/cars: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


if __name__ == '__main__':
    print("🚀 Starting ReCarmend API Server...")
    print("📡 API will be available at http://localhost:5000")
    print("📝 Endpoints:")
    print("   - POST /api/search - AI-powered search")
    print("   - POST /api/search/filtered - Filter-based search")
    print("   - GET /api/cars - Get all cars")
    print("   - GET /api/health - Health check")
    app.run(debug=True, host='0.0.0.0', port=5000)


