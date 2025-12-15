/**
 * Frontend Service
 * Abstraction layer for frontend operations and API communication.
 * This class represents the frontend component in the system architecture.
 */

import { searchCars, searchCarsWithFilters, getAllCars, healthCheck } from './api';
import type { Car, SearchResponse, Filters } from './api';

export class FrontendService {
  private apiUrl: string;

  constructor(apiUrl?: string) {
    this.apiUrl = apiUrl || import.meta.env.VITE_API_URL || 'http://localhost:5001';
  }

  /**
   * Perform AI-powered car search using natural language query.
   * 
   * @param query - Natural language description of desired car
   * @param filters - Optional filters to apply
   * @param lastId - Optional cursor for pagination
   * @returns Promise resolving to search results
   */
  async searchCars(
    query: string,
    filters?: Filters,
    lastId?: string | number | null
  ): Promise<SearchResponse> {
    try {
      return await searchCars(query, filters, lastId);
    } catch (error) {
      console.error('FrontendService: Search error:', error);
      throw error;
    }
  }

  /**
   * Perform filter-based car search.
   * 
   * @param filters - Filter criteria
   * @param query - Optional search query
   * @param lastId - Optional cursor for pagination
   * @returns Promise resolving to search results
   */
  async searchCarsWithFilters(
    filters: Filters,
    query?: string,
    lastId?: string | number | null
  ): Promise<SearchResponse> {
    try {
      return await searchCarsWithFilters(filters, query, lastId);
    } catch (error) {
      console.error('FrontendService: Filtered search error:', error);
      throw error;
    }
  }

  /**
   * Get all cars (for testing/debugging).
   * 
   * @param limit - Maximum number of cars to return
   * @returns Promise resolving to search results
   */
  async getAllCars(limit: number = 10): Promise<SearchResponse> {
    try {
      return await getAllCars(limit);
    } catch (error) {
      console.error('FrontendService: Get all cars error:', error);
      throw error;
    }
  }

  /**
   * Health check - test if backend is running.
   * 
   * @returns Promise resolving to health status
   */
  async healthCheck(): Promise<{ status: string; message: string }> {
    try {
      return await healthCheck();
    } catch (error) {
      console.error('FrontendService: Health check error:', error);
      throw error;
    }
  }

  /**
   * Normalize car data from API to match frontend Car interface.
   * 
   * @param car - Raw car data from API
   * @returns Normalized car object
   */
  normalizeCar(car: any): Car {
    // Filter out 'gas' and 'unknown' from fuelType
    let fuelType = car.fuel_type || car.fuelType || null;
    if (fuelType) {
      const lower = fuelType.toLowerCase().trim();
      if (lower === 'gas' || lower === 'unknown' || lower === 'null' || lower === '') {
        fuelType = null;
      }
    }

    return {
      id: car.id?.toString() || Math.random().toString(),
      make: car.make || 'Unknown',
      model: car.model || 'Unknown',
      year: car.year || 0,
      price: car.price || 0,
      mileage: car.mileage || 0,
      fuelType: fuelType || '',
      bodyType: car.body_type || car.bodyType || car.carType || 'Unknown',
      color: car.color || 'Unknown',
      image: car.imageUrl || car.image || car.image_url || car.url || car.listing_url || this.getCarImageUrl(car.make, car.model, car.year),
      location: car.location || car.city || 'Unknown',
      url: car.url || car.listing_url,
      colorHex: car.colorHex || car.color_hex || null,
    };
  }

  /**
   * Generate a car image URL from Unsplash based on car details.
   * 
   * @param make - Car manufacturer
   * @param model - Car model
   * @param year - Car year
   * @returns Image URL string
   */
  private getCarImageUrl(make?: string, model?: string, year?: number): string {
    const searchTerms = [make, model, year ? year.toString() : null]
      .filter(Boolean)
      .join(' ');
    
    // Use Unsplash Source API for dynamic car images
    if (searchTerms) {
      const query = encodeURIComponent(`${searchTerms} car`);
      return `https://source.unsplash.com/600x400/?${query}`;
    }
    
    // Fallback to a generic car image from Unsplash
    return 'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=600&h=400&fit=crop&auto=format';
  }
}

// Export singleton instance for convenience
export const frontendService = new FrontendService();

