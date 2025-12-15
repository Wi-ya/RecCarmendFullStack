"""
Electric Car Implementation
Concrete class for electric and hybrid vehicles.
"""

from typing import Dict, Optional
from .car import Car


class ElectricCar(Car):
    """
    Electric car implementation.
    Used for electric and hybrid vehicles.
    """
    
    def __init__(self, *args, battery_range: Optional[int] = None, **kwargs):
        """
        Initialize ElectricCar with optional battery range.
        
        Args:
            *args: Arguments passed to parent Car class
            battery_range: Battery range in miles (optional)
            **kwargs: Keyword arguments passed to parent Car class
        """
        super().__init__(*args, **kwargs)
        self.battery_range = battery_range
    
    def get_fuel_type(self) -> str:
        """
        Return fuel type as 'Electric' or 'Hybrid'.
        Polymorphic method - ElectricCar returns 'Hybrid' if body_type contains 'hybrid', else 'Electric'.
        """
        if "hybrid" in self.body_type.lower():
            return "Hybrid"
        return "Electric"

