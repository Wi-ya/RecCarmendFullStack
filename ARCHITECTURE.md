# ReCarmend Architecture - Object-Oriented Service Layer

## Overview

The ReCarmend application has been refactored to use an object-oriented architecture with abstraction classes for each major component. This design allows each component to be represented as objects in sequence diagrams and provides better separation of concerns.

## Service Classes

### 1. **CohereAPI** (`Controller/services/cohere_service.py`)
- **Purpose**: Abstraction layer for Cohere AI natural language processing
- **Key Methods**:
  - `parse_car_query(user_prompt: str)`: Parses natural language car queries into structured parameters
- **Dependencies**: Cohere API key from environment variables

### 2. **PexelsAPI** (`Controller/services/pexels_service.py`)
- **Purpose**: Abstraction layer for fetching car images from Pexels API
- **Key Methods**:
  - `get_car_image_url(make, model, year, color)`: Fetches car image URLs
  - `get_fallback_image(make, model, year)`: Returns fallback images when API fails
- **Dependencies**: Pexels API key from environment variables (optional)

### 3. **SupabaseService** (`Controller/services/supabase_service.py`)
- **Purpose**: Abstraction layer for database operations using Supabase
- **Key Methods**:
  - `search_cars(...)`: Searches for cars matching specified criteria
  - `get_all_cars(limit)`: Retrieves all cars (for testing)
- **Dependencies**: Supabase URL and API key from environment variables

### 4. **BackendService** (`Controller/services/backend_service.py`)
- **Purpose**: Main orchestrator that coordinates all external services
- **Key Methods**:
  - `ai_search(user_query)`: Performs AI-powered car search
  - `filtered_search(filters)`: Performs filter-based car search
  - `format_car_results(cars)`: Formats car data with images and color codes
- **Dependencies**: CohereAPI, SupabaseService, PexelsAPI instances

### 5. **FrontendService** (`View/src/services/FrontendService.ts`)
- **Purpose**: Abstraction layer for frontend operations and API communication
- **Key Methods**:
  - `searchCars(query, filters, lastId)`: Performs AI-powered search
  - `searchCarsWithFilters(filters, query, lastId)`: Performs filter-based search
  - `normalizeCar(car)`: Normalizes car data from API
- **Dependencies**: Backend API URL from environment variables

## Architecture Flow

```
User
  ↓
FrontendService (TypeScript)
  ↓ HTTP Request
BackendService (Python)
  ↓
  ├─→ CohereAPI (for AI search parsing)
  ├─→ SupabaseService (for database queries)
  └─→ PexelsAPI (for image fetching)
```

## Usage in Sequence Diagrams

Each service class can now be represented as an object/component in sequence diagrams:

1. **User** (Actor)
2. **FrontendService** (Component)
3. **BackendService** (Component)
4. **CohereAPI** (Component)
5. **SupabaseService** (Component)
6. **PexelsAPI** (Component)

## Benefits

1. **Separation of Concerns**: Each service handles one specific responsibility
2. **Testability**: Services can be easily mocked and tested independently
3. **Maintainability**: Changes to one service don't affect others
4. **Reusability**: Services can be reused across different parts of the application
5. **Sequence Diagram Clarity**: Each component is clearly defined as an object

## File Structure

```
Controller/
  ├── services/
  │   ├── __init__.py
  │   ├── cohere_service.py      # CohereAPI class
  │   ├── pexels_service.py      # PexelsAPI class
  │   ├── supabase_service.py    # SupabaseService class
  │   └── backend_service.py     # BackendService class
  └── api_server.py              # Flask API routes (uses services)

View/
  └── src/
      └── services/
          └── FrontendService.ts # FrontendService class
```

## Example Usage

### Backend (Python)
```python
from services import BackendService

# Initialize services
backend_service = BackendService()

# Perform AI search
results = backend_service.ai_search("red SUV under $30k")

# Perform filtered search
results, has_more, total = backend_service.filtered_search({
    "maxPrice": 30000,
    "bodyTypes": ["SUV"]
})
```

### Frontend (TypeScript)
```typescript
import { frontendService } from '@/services/FrontendService';

// Perform AI search
const results = await frontendService.searchCars("red SUV under $30k");

// Perform filtered search
const filteredResults = await frontendService.searchCarsWithFilters({
    maxPrice: 30000,
    bodyTypes: ["SUV"]
});
```

