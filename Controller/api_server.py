# -*- coding: utf-8 -*-
"""
ReCarmend API Server
REST API for car recommendation system using AI-powered and filtered search.
Uses object-oriented service layer for abstraction.
"""

import os
import sys
import warnings
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import services from their respective locations
from Cohere import CohereAPI
from Pexels import PexelsAPI
from Database_Model_Connection import SupabaseService
from Controller.services import BackendService

# Suppress Pydantic V1 compatibility warning from cohere library
warnings.filterwarnings("ignore", message=".*Pydantic V1.*")

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure CORS - allow requests from frontend
CORS(app, origins=["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:5001"])

# Initialize service layer
print("Initializing service layer...")
try:
    # Initialize individual services and pass them to BackendService
    # BackendService will use these services - api_server doesn't need direct access
    backend_service = BackendService(
        cohere_api=CohereAPI(),
        supabase_service=SupabaseService(),
        pexels_api=PexelsAPI()
    )
    print("✅ Service layer initialized successfully")
    print(f"   - BackendService: {backend_service.__class__.__name__}")
    print(f"   - CohereAPI: {backend_service.cohere_api.__class__.__name__}")
    print(f"   - SupabaseService: {backend_service.supabase_service.__class__.__name__}")
    print(f"   - PexelsAPI: {backend_service.pexels_api.__class__.__name__}")
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
        
        # Get last_id for pagination if provided
        last_id = data.get('last_id')
        if last_id is not None:
            try:
                last_id = int(last_id)
            except (ValueError, TypeError):
                last_id = None
        
        # Perform AI search using BackendService
        search_result = backend_service.ai_search(query, last_id=last_id)
        
        # Check if there was an error
        if isinstance(search_result, dict) and 'error' in search_result:
            return jsonify(search_result), 400
        
        # Extract results and last_id from response
        cars = search_result.get('results', [])
        last_car_id = search_result.get('last_id')
        
        # Check if there are more results (if we got 10 results, there might be more)
        has_more = len(cars) == 10
        
        # Format response
        response_data = {
            "cars": cars,
            "count": len(cars),
            "query": query,
            "hasMore": has_more,
            "totalCount": len(cars)
        }
        
        if last_car_id is not None:
            response_data["last_id"] = last_car_id
        
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
        
        # Get last_id for pagination if provided
        last_id = data.get('last_id')
        if last_id is not None:
            try:
                last_id = int(last_id)
            except (ValueError, TypeError):
                last_id = None
        
        # Search database using BackendService
        results, has_more, total_count, last_car_id = backend_service.filtered_search(
            filters, 
            return_has_more=True,
            last_id=last_id
        )
        
        # Format response
        response_data = {
            "cars": results,
            "count": len(results),
            "hasMore": has_more,
            "totalCount": total_count
        }
        
        if last_car_id is not None:
            response_data["last_id"] = last_car_id
        
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


