"""
Frontend Service
Represents the frontend/UI component in the system architecture.
This class is used for sequence diagrams to show the frontend as an object.
"""

from typing import Dict, List, Optional, Any, Union


class FrontendService:
    """
    Service class representing the Frontend/View component.
    This is a representation of the React frontend for sequence diagram purposes.
    The actual frontend is implemented in TypeScript (View/src/).
    """
    
    def __init__(self, api_url: str = "http://localhost:5001"):
        """
        Initialize FrontendService.
        
        Args:
            api_url: URL of the backend API
        """
        self.api_url = api_url
        self.name = "Frontend (React/Vite)"
    
    def search_cars(
        self, 
        query: str, 
        filters: Optional[Dict] = None,
        last_id: Optional[Union[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Perform AI-powered car search using natural language query.
        This represents the frontend calling the backend API.
        
        Args:
            query: Natural language description of desired car
            filters: Optional filter criteria
            last_id: Optional cursor for pagination
        
        Returns:
            Dictionary with search results
        """
        # This is a representation - actual implementation is in TypeScript
        # In sequence diagrams, this shows: Frontend → Backend
        return {
            "method": "POST",
            "endpoint": f"{self.api_url}/api/search",
            "body": {"query": query, "last_id": last_id}
        }
    
    def search_cars_with_filters(
        self,
        filters: Dict,
        query: Optional[str] = None,
        last_id: Optional[Union[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Perform filter-based car search.
        This represents the frontend calling the backend API.
        
        Args:
            filters: Filter criteria
            query: Optional search query
            last_id: Optional cursor for pagination
        
        Returns:
            Dictionary with search results
        """
        # This is a representation - actual implementation is in TypeScript
        # In sequence diagrams, this shows: Frontend → Backend
        return {
            "method": "POST",
            "endpoint": f"{self.api_url}/api/search/filtered",
            "body": {"filters": filters, "last_id": last_id}
        }
    
    def normalize_car(self, car: Dict) -> Dict:
        """
        Normalize car data from API to match frontend Car interface.
        This represents frontend processing of backend responses.
        
        Args:
            car: Raw car data from backend
        
        Returns:
            Normalized car object
        """
        # This is a representation - actual implementation is in TypeScript
        # In sequence diagrams, this shows: Frontend → Frontend (self-call)
        return {
            "id": str(car.get("id", "")),
            "make": car.get("make", "Unknown"),
            "model": car.get("model", "Unknown"),
            "year": car.get("year", 0),
            "price": car.get("price", 0),
            "mileage": car.get("mileage", 0),
            "fuelType": car.get("fuel_type") or car.get("fuelType", ""),
            "bodyType": car.get("body_type") or car.get("bodyType", "Unknown"),
            "color": car.get("color", "Unknown"),
            "image": car.get("imageUrl") or car.get("image", ""),
            "location": car.get("location", "Unknown"),
            "url": car.get("url") or car.get("listing_url"),
            "colorHex": car.get("colorHex") or car.get("color_hex")
        }
    
    def render_car_cards(self, cars: List[Dict]) -> None:
        """
        Render car cards in the user interface.
        This represents the frontend displaying results to the user.
        
        Args:
            cars: List of normalized car objects
        """
        # This is a representation - actual implementation is in TypeScript
        # In sequence diagrams, this shows: Frontend displays results (END - no return arrow)
        pass
    
    def get_name(self) -> str:
        """
        Get the name/identifier of this service.
        
        Returns:
            Service name
        """
        return self.name

