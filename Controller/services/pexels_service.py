"""
Pexels API Service
Abstraction layer for fetching car images from Pexels API.
"""

import os
import requests
import hashlib
from typing import Optional


class PexelsAPI:
    """
    Service class for interacting with Pexels API to fetch car images.
    Provides methods for searching and retrieving car images.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Pexels API client.
        
        Args:
            api_key: Pexels API key. If None, will try to get from environment.
        """
        if api_key is None:
            api_key = os.getenv("PEXELS_API_KEY")
        
        self.api_key = api_key
        self.base_url = "https://api.pexels.com/v1/search"
    
    def get_car_image_url(
        self, 
        make: str, 
        model: str, 
        year: Optional[int] = None, 
        color: Optional[str] = None
    ) -> str:
        """
        Fetch a car image URL using Pexels API or return fallback image.
        
        Args:
            make: Car manufacturer (e.g., "Toyota", "Ford")
            model: Car model (e.g., "Camry", "F-150")
            year: Car year (e.g., 2020)
            color: Car color (optional, e.g., "red", "blue")
        
        Returns:
            Image URL string (either from Pexels or fallback).
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
                return self.get_fallback_image(make, model, year)
            
            # Try Pexels API if key is available
            if self.api_key:
                image_url = self._search_pexels(make, model, year, color)
                if image_url:
                    return image_url
            
            # Fallback to generic car images
            return self.get_fallback_image(make, model, year)
            
        except Exception as e:
            print(f"Error fetching car image for {make} {model}: {e}")
            return self.get_fallback_image(make, model, year)
    
    def _search_pexels(
        self, 
        make: str, 
        model: str, 
        year: Optional[int] = None, 
        color: Optional[str] = None
    ) -> Optional[str]:
        """
        Search Pexels API for car images.
        
        Args:
            make: Car manufacturer
            model: Car model
            year: Car year (optional)
            color: Car color (optional)
        
        Returns:
            Image URL if found, None otherwise.
        """
        # Build query - ALWAYS include "car" and exclude motorcycles/models
        best_query = None
        if year and year > 0:
            if color:
                best_query = f"{year} {make} {model} {color} automobile car vehicle"
            else:
                best_query = f"{year} {make} {model} automobile car vehicle"
        else:
            best_query = f"{make} {model} automobile car vehicle"
        
        try:
            headers = {"Authorization": self.api_key}
            search_params = {
                "query": best_query,
                "per_page": 15,  # Get more results to filter from
                "orientation": "landscape"
            }
            
            response = requests.get(
                self.base_url, 
                params=search_params, 
                headers=headers, 
                timeout=3
            )
            
            if response.status_code == 200:
                data = response.json()
                photos = data.get("photos", [])
                if photos and len(photos) > 0:
                    # Filter for car-specific images
                    car_photos = self._filter_car_photos(photos, make, model)
                    
                    if car_photos:
                        # Use hash to consistently pick different images for different cars
                        car_hash = int(hashlib.md5(f"{make}{model}{year}{color}".encode()).hexdigest(), 16)
                        photo_index = car_hash % len(car_photos)
                        image_url = car_photos[photo_index]["src"]["large"]
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
        
        return None
    
    def _filter_car_photos(self, photos: list, make: str, model: str) -> list:
        """
        Filter photos to only include car-specific images.
        
        Args:
            photos: List of photo objects from Pexels API
            make: Car manufacturer
            model: Car model
        
        Returns:
            Filtered list of car photos.
        """
        exclude_keywords = [
            "motorcycle", "bike", "bicycle", "scooter", "model", 
            "person", "people", "portrait", "fashion", "woman", 
            "man", "girl", "boy"
        ]
        
        car_keywords = [
            "car", "automobile", "vehicle", "sedan", "suv", "coupe", 
            "convertible", "hatchback", "sports car", "luxury car"
        ]
        
        car_photos = []
        for photo in photos:
            alt_text = photo.get("alt", "").lower()
            url = photo.get("url", "").lower()
            
            # Skip if it contains excluded keywords
            if any(excluded in alt_text or excluded in url for excluded in exclude_keywords):
                continue
            
            # Must contain car-related keywords
            if any(keyword in alt_text for keyword in car_keywords):
                car_photos.append(photo)
            # Also accept if make/model is mentioned
            elif make.lower() in alt_text and model.lower() in alt_text:
                car_photos.append(photo)
        
        if car_photos:
            return car_photos
        else:
            # If no strict matches, use all photos but log a warning
            print(f"⚠️ No strict car matches for {make} {model}, using all results")
            return photos
    
    def get_fallback_image(self, make: str, model: str, year: Optional[int] = None) -> str:
        """
        Get a fallback car image when API search fails.
        
        Args:
            make: Car manufacturer
            model: Car model
            year: Car year (optional)
        
        Returns:
            Fallback image URL.
        """
        fallback_images = [
            "https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop",
            "https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop",
            "https://images.pexels.com/photos/1592384/pexels-photo-1592384.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop",
            "https://images.pexels.com/photos/1149137/pexels-photo-1149137.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop",
            "https://images.pexels.com/photos/164634/pexels-photo-164634.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop",
            "https://images.pexels.com/photos/3802508/pexels-photo-3802508.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop",
            "https://images.pexels.com/photos/1545743/pexels-photo-1545743.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop",
            "https://images.pexels.com/photos/1719647/pexels-photo-1719647.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop",
            "https://images.pexels.com/photos/358070/pexels-photo-358070.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop",
            "https://images.pexels.com/photos/210019/pexels-photo-210019.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop",
        ]
        
        # Use a consistent fallback based on make/model/year hash for variety
        car_hash = int(hashlib.md5(f"{make}{model}{year}".encode()).hexdigest(), 16)
        selected_image = fallback_images[car_hash % len(fallback_images)]
        print(f"⚠️ Using fallback image for {year} {make} {model} (no specific image found)")
        return selected_image

