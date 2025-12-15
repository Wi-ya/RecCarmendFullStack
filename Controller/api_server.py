# -*- coding: utf-8 -*-
"""
ReCarmend API Server
REST API for car recommendation system using AI-powered and filtered search.
Uses object-oriented service layer for abstraction.
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from services import BackendService, CohereAPI, SupabaseService, PexelsAPI, FrontendService

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure CORS - allow requests from frontend
CORS(app, origins=["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:5001"])

# Initialize service layer
print("Initializing service layer...")
try:
    # Initialize individual services
    cohere_api = CohereAPI()
    supabase_service = SupabaseService()
    pexels_api = PexelsAPI()
    frontend_service = FrontendService()  # Represents the frontend/UI component
    
    # Initialize main backend service that orchestrates all services
    backend_service = BackendService(
        cohere_api=cohere_api,
        supabase_service=supabase_service,
        pexels_api=pexels_api
    )
    print("✅ Service layer initialized successfully")
    print(f"   - CohereAPI: {cohere_api.__class__.__name__}")
    print(f"   - SupabaseService: {supabase_service.__class__.__name__}")
    print(f"   - PexelsAPI: {pexels_api.__class__.__name__}")
    print(f"   - FrontendService: {frontend_service.get_name()}")
    print(f"   - BackendService: {backend_service.__class__.__name__}")
except Exception as e:
    raise ConnectionError(f"Failed to initialize service layer: {e}")


# All business logic has been moved to service classes
# The backend_service instance handles all operations


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
        
        # Perform AI search using BackendService
        results = backend_service.ai_search(query)
        
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
        
        # Search database using BackendService
        results, has_more, total_count = backend_service.filtered_search(filters, return_has_more=True)
        
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
        
        # Get all cars from SupabaseService
        cars = backend_service.supabase_service.get_all_cars(limit)
        
        # Format results: filter out 'gas'/'unknown', add color hex codes, and add images
        formatted_cars = backend_service.format_car_results(cars)
        
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


