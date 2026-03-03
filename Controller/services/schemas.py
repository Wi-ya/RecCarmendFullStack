"""
API request and response schemas (Pydantic).
Validates request bodies and defines response shape for the REST API.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ----- Request schemas -----


class SearchRequest(BaseModel):
    """Request body for POST /api/search (AI-powered search)."""

    query: str = Field(..., min_length=1, description="Natural language search description")
    last_id: Optional[int] = Field(None, ge=1, description="Cursor for pagination (id of last car from previous page)")


class FilterSchema(BaseModel):
    """Filter criteria for car search. All fields optional."""

    maxPrice: Optional[int] = Field(None, ge=0, description="Maximum price in dollars")
    maxMileage: Optional[int] = Field(None, ge=0, description="Maximum mileage")
    minYear: Optional[int] = Field(None, ge=1900, le=2100, description="Minimum year")
    maxYear: Optional[int] = Field(None, ge=1900, le=2100, description="Maximum year")
    bodyTypes: Optional[list[str]] = Field(None, description="Body types e.g. ['SUV', 'Sedan']")
    makes: Optional[list[str]] = Field(None, description="Makes e.g. ['Toyota']")
    models: Optional[list[str]] = Field(None, description="Models e.g. ['RAV4']")
    colors: Optional[list[str]] = Field(None, description="Colors e.g. ['Red']")


class FilteredSearchRequest(BaseModel):
    """Request body for POST /api/search/filtered."""

    filters: FilterSchema = Field(..., description="Filter criteria")
    last_id: Optional[int] = Field(None, ge=1, description="Cursor for pagination")


# ----- Response schemas -----


class CarResponse(BaseModel):
    """Single car in API responses. Matches backend format_car_results output."""

    id: int | str = Field(..., description="Car or listing id")
    make: str = Field(..., description="Manufacturer")
    model: str = Field(..., description="Model name")
    year: int = Field(..., ge=0, description="Year")
    price: int | float = Field(..., ge=0, description="Price in dollars")
    mileage: int = Field(..., ge=0, description="Mileage")
    fuelType: str = Field(..., description="Gas, Electric, or Hybrid")
    bodyType: str = Field(..., description="e.g. SUV, Sedan")
    color: str = Field(..., description="Color name")
    url: Optional[str] = Field(None, description="Listing URL")
    colorHex: Optional[str] = Field(None, description="Hex color code for UI")
    imageUrl: Optional[str] = Field(None, description="Car image URL")
    image: Optional[str] = Field(None, description="Same as imageUrl for frontend compatibility")

    model_config = ConfigDict(extra="allow")  # Allow extra keys from backend (e.g. location)


class SearchResponse(BaseModel):
    """Response for POST /api/search and POST /api/search/filtered."""

    cars: list[CarResponse] = Field(..., description="List of matching cars")
    count: int = Field(..., ge=0, description="Number of cars returned")
    query: Optional[str] = Field(None, description="Original query (AI search only)")
    hasMore: bool = Field(False, description="Whether more results exist")
    totalCount: Optional[int] = Field(None, ge=0, description="Total matching count (filtered search)")
    last_id: Optional[int] = Field(None, description="Cursor for next page")
    message: Optional[str] = Field(None, description="Optional hint message")


class CarsListResponse(BaseModel):
    """Response for GET /api/cars."""

    cars: list[CarResponse] = Field(..., description="List of cars")
    count: int = Field(..., ge=0, description="Number of cars returned")


class ErrorResponse(BaseModel):
    """Error response for 4xx/5xx."""

    error: str = Field(..., description="Error message")
    message: Optional[str] = Field(None, description="Optional detail")


class HealthResponse(BaseModel):
    """Response for GET /api/health."""

    status: str = Field(..., description="e.g. healthy")
    message: str = Field(..., description="Status message")
