"""
Supabase Service
Abstraction layer for database operations using Supabase.
"""

import os
from typing import Dict, List, Optional, Tuple
from supabase import create_client, Client


class SupabaseService:
    """
    Service class for interacting with Supabase database.
    Provides methods for querying car listings.
    """
    
    def __init__(self, db_url: Optional[str] = None, db_api_key: Optional[str] = None):
        """
        Initialize Supabase client.
        
        Args:
            db_url: Supabase project URL. If None, will try to get from environment.
            db_api_key: Supabase API key. If None, will try to get from environment.
        
        Raises:
            ValueError: If credentials are not provided or found in environment.
            ConnectionError: If connection to Supabase fails.
        """
        if db_url is None:
            db_url = os.getenv("DB_URL")
        if db_api_key is None:
            db_api_key = os.getenv("DB_API_KEY")
        
        if not db_url or not db_api_key:
            raise ValueError(
                "Missing Supabase credentials. "
                "Please provide DB_URL and DB_API_KEY or set them as environment variables."
            )
        
        try:
            print("Connecting to Supabase database...")
            self.client: Client = create_client(db_url, db_api_key)
            self.db_url = db_url
            print("✅ Connected to Supabase database")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Supabase: {e}")
    
    def search_cars(
        self,
        maximum_price: Optional[int] = None,
        maximum_mileage: Optional[int] = None,
        color: Optional[str] = None,
        make: Optional[str] = None,
        model: Optional[str] = None,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        car_type: Optional[str] = None,
        limit: int = 10,
        return_has_more: bool = False
    ):
        """
        Search for cars matching the specified criteria.
        
        Args:
            maximum_price: Maximum price filter
            maximum_mileage: Maximum mileage filter
            color: Color filter (case-insensitive partial match)
            make: Make filter (case-insensitive partial match)
            model: Model filter (case-insensitive partial match)
            min_year: Minimum year filter
            max_year: Maximum year filter
            car_type: Car type/body type filter (case-insensitive partial match)
            limit: Maximum number of results to return (default: 10)
            return_has_more: If True, returns tuple with has_more and total_count
        
        Returns:
            If return_has_more is False: List of car dictionaries
            If return_has_more is True: Tuple of (results, has_more, total_count)
        """
        # Normalize input values
        color = color.lower() if color and color.lower() not in ["null", "", None] else None
        make = make.lower() if make and make.lower() not in ["null", "", None] else None
        model = model.lower() if model and model.lower() not in ["null", "", None] else None
        car_type = car_type.lower() if car_type and car_type.lower() not in ["null", "", None] else None
        
        # Build the query with filters
        query = self.client.table('CarListings').select('*', count='exact')
        
        # Apply numeric filters
        if maximum_price and maximum_price > 0:
            query = query.lte('price', maximum_price)
        if maximum_mileage and maximum_mileage > 0:
            query = query.lte('mileage', maximum_mileage)
        if min_year and min_year > 0:
            query = query.gte('year', min_year)
        if max_year and max_year > 0:
            query = query.lte('year', max_year)
        
        # Apply text filters (case-insensitive search)
        if color:
            query = query.ilike('color', f'%{color}%')
        if make:
            query = query.ilike('make', f'%{make}%')
        if model:
            query = query.ilike('model', f'%{model}%')
        
        # Handle carType - try both possible column names
        if car_type:
            try:
                query_with_cartype = query.ilike('body_type', f'%{car_type}%')
                response = query_with_cartype.limit(limit).execute()
                if response.data and len(response.data) > 0:
                    results = response.data
                    if return_has_more:
                        total_count = response.count if hasattr(response, 'count') else len(results)
                        has_more = total_count > limit
                        return results, has_more, total_count
                    return results
            except Exception as e:
                # If body_type fails, try carType column
                try:
                    query_with_cartype = query.ilike('carType', f'%{car_type}%')
                    response = query_with_cartype.limit(limit).execute()
                    if response.data and len(response.data) > 0:
                        results = response.data
                        if return_has_more:
                            total_count = response.count if hasattr(response, 'count') else len(results)
                            has_more = total_count > limit
                            return results, has_more, total_count
                        return results
                except Exception as e2:
                    # If both fail, continue without carType filter
                    print(f"Warning: Could not filter by car type '{car_type}', showing all types")
        
        # Execute query (either no carType filter, or carType filter failed)
        try:
            response = query.limit(limit).execute()
            results = response.data if response.data else []
            
            if return_has_more:
                total_count = response.count if hasattr(response, 'count') else len(results)
                has_more = total_count > limit
                return results, has_more, total_count
            
            return results
        except Exception as e:
            print(f"Error querying database: {e}")
            if return_has_more:
                return [], False, 0
            return []
    
    def get_all_cars(self, limit: int = 10) -> List[Dict]:
        """
        Get all cars from the database (for testing/debugging).
        
        Args:
            limit: Maximum number of results to return
        
        Returns:
            List of car dictionaries
        """
        try:
            response = self.client.table('CarListings').select('*').limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting all cars: {e}")
            return []
    
    def sortDB(
        self,
        maximum_price: Optional[int] = None,
        maximum_mileage: Optional[int] = None,
        color: Optional[str] = None,
        make: Optional[str] = None,
        model: Optional[str] = None,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        car_type: Optional[str] = None,
        return_has_more: bool = False
    ):
        """
        Alias method for search_cars() to match sequence diagram naming.
        This method calls search_cars() internally.
        
        Args:
            maximum_price: Maximum price filter
            maximum_mileage: Maximum mileage filter
            color: Color filter
            make: Make filter
            model: Model filter
            min_year: Minimum year filter
            max_year: Maximum year filter
            car_type: Car type/body type filter
            return_has_more: If True, returns tuple with has_more and total_count
        
        Returns:
            If return_has_more is False: List of car dictionaries
            If return_has_more is True: Tuple of (results, has_more, total_count)
        """
        return self.search_cars(
            maximum_price=maximum_price,
            maximum_mileage=maximum_mileage,
            color=color,
            make=make,
            model=model,
            min_year=min_year,
            max_year=max_year,
            car_type=car_type,
            limit=10,
            return_has_more=return_has_more
        )

