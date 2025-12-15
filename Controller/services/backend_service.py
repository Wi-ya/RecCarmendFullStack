"""
Backend Service
Main service class that orchestrates all external services for car search operations.
"""

import hashlib
from typing import Dict, List, Optional, Tuple
from .cohere_service import CohereAPI
from .pexels_service import PexelsAPI
from .supabase_service import SupabaseService


class BackendService:
    """
    Main backend service that coordinates Cohere AI, Supabase, and Pexels API.
    Provides high-level methods for AI search and filtered search operations.
    """
    
    def __init__(
        self,
        cohere_api: Optional[CohereAPI] = None,
        supabase_service: Optional[SupabaseService] = None,
        pexels_api: Optional[PexelsAPI] = None
    ):
        """
        Initialize BackendService with service dependencies.
        
        Args:
            cohere_api: CohereAPI instance. If None, will create new instance.
            supabase_service: SupabaseService instance. If None, will create new instance.
            pexels_api: PexelsAPI instance. If None, will create new instance.
        """
        self.cohere_api = cohere_api or CohereAPI()
        self.supabase_service = supabase_service or SupabaseService()
        self.pexels_api = pexels_api or PexelsAPI()
    
    def ai_search(self, user_query: str) -> Dict:
        """
        Perform AI-powered car search using natural language query.
        
        Args:
            user_query: Natural language description of desired car.
        
        Returns:
            Dictionary with search results or error message.
        """
        try:
            # Parse query using Cohere AI
            parsed_params = self.cohere_api.parse_car_query(user_query)
            
            # Check for errors
            if isinstance(parsed_params, dict) and 'error' in parsed_params:
                return parsed_params
            
            # Search database with parsed parameters
            results = self.supabase_service.search_cars(
                maximum_price=parsed_params.get('maximumPrice'),
                maximum_mileage=parsed_params.get('maximumMileage'),
                color=parsed_params.get('color'),
                make=parsed_params.get('make'),
                model=parsed_params.get('model'),
                min_year=parsed_params.get('minYear'),
                max_year=parsed_params.get('maxYear'),
                car_type=parsed_params.get('carType'),
                limit=10,
                return_has_more=False
            )
            
            # Format results: add images, color hex codes, filter invalid values
            formatted_results = self.format_car_results(results)
            
            return formatted_results
            
        except Exception as e:
            print(f"Error in AI search: {e}")
            return {"error": f"AI search failed: {str(e)}"}
    
    def filtered_search(
        self,
        filters: Dict,
        return_has_more: bool = True
    ) -> Tuple[List[Dict], bool, int]:
        """
        Perform filter-based car search.
        
        Args:
            filters: Dictionary containing filter criteria:
                - maxPrice: int
                - maxMileage: int
                - minYear: int
                - maxYear: int
                - bodyTypes: List[str] (will use first item)
                - makes: List[str] (will use first item)
                - models: List[str] (will use first item)
                - colors: List[str] (will use first item)
            return_has_more: If True, returns tuple with has_more and total_count
        
        Returns:
            If return_has_more is False: List of formatted car dictionaries
            If return_has_more is True: Tuple of (formatted_results, has_more, total_count)
        """
        # Extract filter values
        maximum_price = self._safe_int(filters.get('maxPrice', 0))
        maximum_mileage = self._safe_int(filters.get('maxMileage', 0))
        min_year = self._safe_int(filters.get('minYear', 0))
        max_year = self._safe_int(filters.get('maxYear', 2026))
        
        # Handle multiple values (take first one)
        body_types = filters.get('bodyTypes', [])
        car_type = body_types[0] if body_types else None
        
        makes = filters.get('makes', [])
        make = makes[0] if makes else None
        
        models = filters.get('models', [])
        model = models[0] if models else None
        
        colors = filters.get('colors', [])
        color = colors[0] if colors else None
        
        # Search database
        results, has_more, total_count = self.supabase_service.search_cars(
            maximum_price=maximum_price,
            maximum_mileage=maximum_mileage,
            color=color,
            make=make,
            model=model,
            min_year=min_year,
            max_year=max_year,
            car_type=car_type,
            limit=10,
            return_has_more=True
        )
        
        # Format results
        formatted_results = self.format_car_results(results)
        
        if return_has_more:
            return formatted_results, has_more, total_count
        else:
            return formatted_results
    
    def format_car_results(self, cars: List[Dict]) -> List[Dict]:
        """
        Format car results by:
        1. Filtering out 'gas' and 'unknown' values
        2. Adding color hex code for visualization
        3. Adding car image URLs
        
        IMPORTANT: This function should only be called on the limited results (max 10 cars)
        returned from the database query, not on all cars in the database.
        
        Args:
            cars: List of car dictionaries from database
        
        Returns:
            List of formatted car dictionaries
        """
        if not cars:
            return []
        
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
                formatted_car['colorHex'] = self.get_color_hex(formatted_car['color'])
            else:
                formatted_car['colorHex'] = None
            
            # Fetch and add car image URL (only for the cars being returned)
            make = formatted_car.get('make', '')
            model = formatted_car.get('model', '')
            year = formatted_car.get('year')
            color = formatted_car.get('color')
            
            if make and model:
                # Only fetch image for this specific car (one of the 10 being returned)
                image_url = self.pexels_api.get_car_image_url(make, model, year, color)
                formatted_car['imageUrl'] = image_url
            else:
                # Default car image if make/model not available
                formatted_car['imageUrl'] = self.pexels_api.get_fallback_image(
                    make or "car", 
                    model or "vehicle", 
                    year
                )
            
            formatted_cars.append(formatted_car)
        
        return formatted_cars
    
    def get_color_hex(self, color_name: str) -> Optional[str]:
        """
        Map color name to hex code for visualization.
        
        Args:
            color_name: Color name string
        
        Returns:
            Hex color code string or None
        """
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
    
    def _safe_int(self, value, default=0) -> int:
        """Safely convert value to integer."""
        try:
            return int(float(str(value).replace(",", "")))
        except:
            return default

