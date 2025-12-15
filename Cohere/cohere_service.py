"""
Cohere API Service
Abstraction layer for Cohere AI natural language processing.
"""

import os
import warnings
import cohere
from typing import Dict, Optional

# Suppress Pydantic V1 compatibility warning from cohere library
warnings.filterwarnings("ignore", message=".*Pydantic V1.*")


class CohereAPI:
    """
    Service class for interacting with Cohere AI API.
    Provides methods for parsing natural language car search queries.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Cohere API client.
        
        Args:
            api_key: Cohere API key. If None, will try to get from environment.
        
        Raises:
            ValueError: If API key is not provided or found in environment.
        """
        if api_key is None:
            api_key = os.getenv("COHERE_API_KEY")
        
        if not api_key:
            raise ValueError(
                "COHERE_API_KEY not found. "
                "Please provide API key or set COHERE_API_KEY environment variable."
            )
        
        self.client = cohere.ClientV2(api_key)
        self.api_key = api_key
    
    def parse_car_query(self, user_prompt: str) -> Dict[str, any]:
        """
        Parse a natural language car search query into structured parameters.
        
        Args:
            user_prompt: User's natural language description of desired car.
        
        Returns:
            Dictionary containing parsed parameters:
            {
                'maximumPrice': int,
                'maximumMileage': int,
                'minYear': int,
                'maxYear': int,
                'color': str or None,
                'make': str or None,
                'model': str or None,
                'carType': str or None
            }
        
        Raises:
            Exception: If API call fails or response cannot be parsed.
        """
        # Enhanced prompt for Cohere
        enhanced_prompt = (
            user_prompt + 
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
        
        try:
            response = self.client.chat(
                model="command-a-03-2025",
                messages=[{"role": "user", "content": enhanced_prompt}]
            )
            
            # Handle Cohere API response - check different possible response formats
            raw_text = self._extract_response_text(response)
            
            # Check if response indicates non-car related query
            if "does not relate to cars" in raw_text.lower():
                return {"error": "Your query does not relate to cars. Please try again with a car-related search."}
            
            # Parse the response into structured format
            return self._parse_response(raw_text)
            
        except Exception as e:
            print(f"Error in Cohere API call: {e}")
            raise Exception(f"Cohere API error: {str(e)}")
    
    def _extract_response_text(self, response) -> str:
        """
        Extract text from Cohere API response, handling different response formats.
        
        Args:
            response: Cohere API response object.
        
        Returns:
            Extracted text string.
        """
        try:
            if hasattr(response, 'text'):
                return response.text
            elif hasattr(response, 'message') and hasattr(response.message, 'content'):
                if isinstance(response.message.content, list) and len(response.message.content) > 0:
                    content_item = response.message.content[0]
                    return content_item.text if hasattr(content_item, 'text') else str(content_item)
                else:
                    return str(response.message.content)
            else:
                return str(response)
        except Exception as e:
            print(f"Error parsing Cohere response: {e}")
            return ""
    
    def _parse_response(self, raw_text: str) -> Dict[str, any]:
        """
        Parse Cohere response text into structured dictionary.
        
        Args:
            raw_text: Raw text response from Cohere API.
        
        Returns:
            Dictionary with parsed parameters.
        """
        def safe_int(value, default=0):
            """Safely convert value to integer."""
            try:
                return int(float(str(value).replace(",", "")))
            except:
                return default
        
        parsed = {}
        for line in raw_text.split("\n"):
            if ":" in line:
                key, value = map(str.strip, line.split(":", 1))
                parsed[key.strip()] = value.strip()
        
        return {
            'maximumPrice': safe_int(parsed.get("Maximum Price", 0)),
            'maximumMileage': safe_int(parsed.get("Maximum Mileage", 0)),
            'minYear': safe_int(parsed.get("Minimum Year", 0)),
            'maxYear': safe_int(parsed.get("Maximum Year", 2026)),
            'color': parsed.get("Color", "Null") if parsed.get("Color", "Null").lower() != "null" else None,
            'make': parsed.get("Make", "Null") if parsed.get("Make", "Null").lower() != "null" else None,
            'model': parsed.get("Model", "Null") if parsed.get("Model", "Null").lower() != "null" else None,
            'carType': parsed.get("Car type", "Null") if parsed.get("Car type", "Null").lower() != "null" else None,
        }

