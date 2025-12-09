/**
 * API Service for ReCarmend
 * Handles all HTTP requests to the backend API
 */

import { Filters } from '@/components/FilterDropdown';

// Get API URL from environment variable, fallback to localhost
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export interface Car {
  id: string;
  make: string;
  model: string;
  year: number;
  price: number;
  mileage: number;
  fuelType: string;
  bodyType: string;
  color: string;
  image: string;
  location: string;
  url?: string;
}

export interface SearchResponse {
  cars: Car[];
  count: number;
  query?: string;
}

export interface ApiError {
  error: string;
  message?: string;
}

/**
 * Normalize car data from API to match frontend Car interface
 */
function normalizeCar(car: any): Car {
  return {
    id: car.id?.toString() || Math.random().toString(),
    make: car.make || 'Unknown',
    model: car.model || 'Unknown',
    year: car.year || 0,
    price: car.price || 0,
    mileage: car.mileage || 0,
    fuelType: car.fuel_type || car.fuelType || 'Unknown',
    bodyType: car.body_type || car.bodyType || car.carType || 'Unknown',
    color: car.color || 'Unknown',
    image: car.image || car.image_url || 'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=600&h=400&fit=crop',
    location: car.location || car.city || 'Unknown',
    url: car.url || car.listing_url,
  };
}

/**
 * Make a request to the API with error handling
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json().catch(() => ({
        error: `HTTP ${response.status}: ${response.statusText}`,
      }));
      throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    return data as T;
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Network error: Could not connect to backend API');
  }
}

/**
 * AI-powered car search
 * Uses natural language query to find cars
 */
export async function searchCars(
  query: string,
  filters?: Filters
): Promise<SearchResponse> {
  try {
    // If filters are provided, use filtered search endpoint
    if (filters && hasActiveFilters(filters)) {
      return await searchCarsWithFilters(filters, query);
    }

    // Otherwise, use AI search
    const response = await apiRequest<SearchResponse>('/api/search', {
      method: 'POST',
      body: JSON.stringify({ query: query.trim() }),
    });

    // Normalize car data
    return {
      ...response,
      cars: response.cars.map(normalizeCar),
    };
  } catch (error) {
    console.error('Search error:', error);
    throw error;
  }
}

/**
 * Filter-based car search
 * Uses specific filters to find cars
 */
export async function searchCarsWithFilters(
  filters: Filters,
  query?: string
): Promise<SearchResponse> {
  try {
    // Convert frontend filters to backend format
    const filterPayload: any = {};

    if (filters.maxPrice) {
      filterPayload.maxPrice = parseInt(filters.maxPrice);
    }
    if (filters.maxMileage) {
      filterPayload.maxMileage = parseInt(filters.maxMileage);
    }
    if (filters.minYear) {
      filterPayload.minYear = parseInt(filters.minYear);
    }
    if (filters.maxYear) {
      filterPayload.maxYear = parseInt(filters.maxYear);
    }
    if (filters.bodyTypes && filters.bodyTypes.length > 0) {
      filterPayload.bodyTypes = filters.bodyTypes;
    }
    if (filters.makes && filters.makes.length > 0) {
      filterPayload.makes = filters.makes;
    }
    if (filters.colors && filters.colors.length > 0) {
      filterPayload.colors = filters.colors;
    }
    if (filters.models && filters.models.length > 0) {
      filterPayload.models = filters.models;
    }

    const response = await apiRequest<SearchResponse>('/api/search/filtered', {
      method: 'POST',
      body: JSON.stringify({ filters: filterPayload }),
    });

    // Normalize car data
    return {
      ...response,
      cars: response.cars.map(normalizeCar),
      query: query || 'Filter search',
    };
  } catch (error) {
    console.error('Filtered search error:', error);
    throw error;
  }
}

/**
 * Get all cars (for testing/debugging)
 */
export async function getAllCars(limit: number = 10): Promise<SearchResponse> {
  try {
    const response = await apiRequest<SearchResponse>(`/api/cars?limit=${limit}`, {
      method: 'GET',
    });

    return {
      ...response,
      cars: response.cars.map(normalizeCar),
    };
  } catch (error) {
    console.error('Get cars error:', error);
    throw error;
  }
}

/**
 * Health check - test if backend is running
 */
export async function healthCheck(): Promise<{ status: string; message: string }> {
  try {
    return await apiRequest<{ status: string; message: string }>('/api/health', {
      method: 'GET',
    });
  } catch (error) {
    console.error('Health check error:', error);
    throw error;
  }
}

/**
 * Check if filters are active
 */
function hasActiveFilters(filters: Filters): boolean {
  return !!(
    filters.bodyTypes?.length ||
    filters.makes?.length ||
    filters.colors?.length ||
    filters.minYear ||
    filters.maxYear ||
    filters.minPrice ||
    filters.maxPrice ||
    filters.maxMileage
  );
}

