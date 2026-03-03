# -*- coding: utf-8 -*-
"""
ReCarmend API Server
REST API for car recommendation system using AI-powered and filtered search.
Uses object-oriented service layer for abstraction.
Request/response validated via Controller.services.schemas (Pydantic).
"""

import os
import sys
import warnings
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pydantic import ValidationError

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load .env from project root only
load_dotenv(project_root / ".env")

# Import services from their respective locations
from Cohere import CohereAPI
from Pexels import PexelsAPI
from Database_Model_Connection import SupabaseService
from Controller.services import BackendService
from Controller.services.schemas import (
    SearchRequest,
    FilteredSearchRequest,
    SearchResponse,
    CarsListResponse,
    CarResponse,
    HealthResponse,
    ErrorResponse,
)

# Suppress Pydantic V1 compatibility warning from cohere library
warnings.filterwarnings("ignore", message=".*Pydantic V1.*")

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


def _validation_error_response(exc: ValidationError):
    """Return 422 JSON for Pydantic validation errors."""
    errors = [{"loc": e["loc"], "msg": e["msg"]} for e in exc.errors()]
    return jsonify({"error": "Validation failed", "details": errors}), 422


# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    body = HealthResponse(status="healthy", message="ReCarmend API is running")
    return jsonify(body.model_dump()), 200


@app.route('/api/search', methods=['POST'])
def search():
    """
    AI-powered search endpoint.
    Request body: SearchRequest (query: str, optional last_id: int).
    Response: SearchResponse (cars, count, query, hasMore, last_id?, message?).
    """
    try:
        data = request.get_json()
        if data is None:
            return jsonify(ErrorResponse(error="Request body must be JSON").model_dump()), 400
        try:
            req = SearchRequest.model_validate(data)
        except ValidationError as e:
            return _validation_error_response(e)
        query = req.query.strip()
        if not query:
            return jsonify(ErrorResponse(error="Query cannot be empty").model_dump()), 400

        search_result = backend_service.ai_search(query, last_id=req.last_id)
        if isinstance(search_result, dict) and "error" in search_result:
            return jsonify(ErrorResponse(error=search_result["error"]).model_dump()), 400

        cars = search_result.get("results", [])
        last_car_id = search_result.get("last_id")
        has_more = len(cars) == 10

        car_responses = [CarResponse.model_validate(c) for c in cars]
        body = SearchResponse(
            cars=car_responses,
            count=len(car_responses),
            query=query,
            hasMore=has_more,
            totalCount=len(car_responses),
            last_id=last_car_id,
            message="Showing 10 results. More cars available - search again to see more." if has_more else None,
        )
        return jsonify(body.model_dump(exclude_none=True)), 200
    except Exception as e:
        print(f"Error in /api/search: {e}")
        return jsonify(ErrorResponse(error=f"Internal server error: {str(e)}").model_dump()), 500


@app.route('/api/search/filtered', methods=['POST'])
def filtered_search():
    """
    Filter-based search endpoint.
    Request body: FilteredSearchRequest (filters: FilterSchema, optional last_id: int).
    Response: SearchResponse (cars, count, hasMore, totalCount, last_id?, message?).
    """
    try:
        data = request.get_json()
        if data is None:
            return jsonify(ErrorResponse(error="Request body must be JSON").model_dump()), 400
        try:
            req = FilteredSearchRequest.model_validate(data)
        except ValidationError as e:
            return _validation_error_response(e)

        filters_dict = req.filters.model_dump(exclude_none=True)
        results, has_more, total_count, last_car_id = backend_service.filtered_search(
            filters_dict,
            return_has_more=True,
            last_id=req.last_id,
        )

        car_responses = [CarResponse.model_validate(c) for c in results]
        body = SearchResponse(
            cars=car_responses,
            count=len(car_responses),
            hasMore=has_more,
            totalCount=total_count,
            last_id=last_car_id,
            message=f"Showing 10 of {total_count} results. Search again to see more cars." if has_more else None,
        )
        return jsonify(body.model_dump(exclude_none=True)), 200
    except Exception as e:
        print(f"Error in /api/search/filtered: {e}")
        return jsonify(ErrorResponse(error=f"Internal server error: {str(e)}").model_dump()), 500


@app.route('/api/cars', methods=['GET'])
def get_cars():
    """
    Get all cars (for testing/debugging).
    Query params: limit (optional, default 10, max 100).
    Response: CarsListResponse (cars, count).
    """
    try:
        limit = request.args.get("limit", 10, type=int)
        if limit is None or limit < 1:
            limit = 10
        limit = min(limit, 100)
        cars = backend_service.supabase_service.get_all_cars(limit)
        formatted_cars = backend_service.format_car_results(cars)
        car_responses = [CarResponse.model_validate(c) for c in formatted_cars]
        body = CarsListResponse(cars=car_responses, count=len(car_responses))
        return jsonify(body.model_dump()), 200
    except Exception as e:
        print(f"Error in /api/cars: {e}")
        return jsonify(ErrorResponse(error=f"Internal server error: {str(e)}").model_dump()), 500


if __name__ == '__main__':
    print("🚀 Starting ReCarmend API Server...")
    print("📡 API will be available at http://localhost:5001")
    print("📝 Endpoints:")
    print("   - POST /api/search - AI-powered search")
    print("   - POST /api/search/filtered - Filter-based search")
    print("   - GET /api/cars - Get all cars")
    print("   - GET /api/health - Health check")
    app.run(debug=True, host='0.0.0.0', port=5001)


