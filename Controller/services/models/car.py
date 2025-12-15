"""
Car Abstract Base Class
Defines the interface for all car types.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional


class Car(ABC):
    """
    Abstract base class for Car objects.
    Defines common interface for all car types.
    """
    
    def __init__(
        self,
        make: str,
        model: str,
        year: int,
        price: float,
        mileage: int,
        body_type: str,
        color: str,
        url: Optional[str] = None
    ):
        """
        Initialize a Car object.
        
        Args:
            make: Car manufacturer
            model: Car model
            year: Manufacturing year
            price: Price in dollars
            mileage: Mileage in miles
            body_type: Body type (SUV, Sedan, etc.)
            color: Car color
            url: Listing URL (optional)
        """
        self.make = make
        self.model = model
        self.year = year
        self.price = price
        self.mileage = mileage
        self.body_type = body_type
        self.color = color
        self.url = url
    
    @abstractmethod
    def get_fuel_type(self) -> str:
        """
        Get the fuel type of this car.
        Polymorphic method - each car type returns different fuel type.
        
        Returns:
            Fuel type string:
            - For GasCar: "Gas"
            - For ElectricCar: "Electric" or "Hybrid"
        """
        pass
    
    def to_dict(self) -> Dict:
        """
        Convert car object to dictionary format.
        Useful for API responses and frontend.
        Uses polymorphic get_fuel_type() to determine fuel type.
        
        Returns:
            Dictionary representation of the car with fuelType from polymorphism
        """
        return {
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "price": self.price,
            "mileage": self.mileage,
            "fuelType": self.get_fuel_type(),  # Polymorphic - Gas vs Electric/Hybrid
            "bodyType": self.body_type,
            "color": self.color,
            "url": self.url
        }
