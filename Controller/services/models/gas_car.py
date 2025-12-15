"""
Gas Car Implementation
Concrete class for gas-powered vehicles.
"""

from typing import Dict, Optional
from .car import Car


class GasCar(Car):
    """
    Gas-powered car implementation.
    Used for cars that run on gasoline/petrol.
    """
    
    def get_fuel_type(self) -> str:
        """
        Return fuel type as 'Gas'.
        Polymorphic method - GasCar always returns 'Gas'.
        """
        return "Gas"

