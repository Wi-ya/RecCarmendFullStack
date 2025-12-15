# Service Objects Created in api_server.py

## Overview

The `api_server.py` file creates all service objects needed for the application. These objects can be represented in sequence diagrams as components.

## Objects Created

### 1. **CohereAPI** (`cohere_api`)
- **Type**: `CohereAPI` class instance
- **Purpose**: Handles natural language processing via Cohere AI
- **Created at**: Line 27
- **Usage**: Parses user queries into structured car search parameters

### 2. **SupabaseService** (`supabase_service`)
- **Type**: `SupabaseService` class instance
- **Purpose**: Handles database operations with Supabase
- **Created at**: Line 28
- **Usage**: Queries car listings from the database

### 3. **PexelsAPI** (`pexels_api`)
- **Type**: `PexelsAPI` class instance
- **Purpose**: Fetches car images from Pexels API
- **Created at**: Line 29
- **Usage**: Retrieves car images for display

### 4. **FrontendService** (`frontend_service`)
- **Type**: `FrontendService` class instance
- **Purpose**: Represents the frontend/UI component for sequence diagrams
- **Created at**: Line 30
- **Usage**: Represents the React frontend in system architecture
- **Note**: The actual frontend is implemented in TypeScript, but this object represents it for diagramming purposes

### 5. **BackendService** (`backend_service`)
- **Type**: `BackendService` class instance
- **Purpose**: Orchestrates all external services
- **Created at**: Lines 33-37
- **Dependencies**: 
  - `cohere_api` (CohereAPI)
  - `supabase_service` (SupabaseService)
  - `pexels_api` (PexelsAPI)
- **Usage**: Main service that coordinates AI search, database queries, and image fetching

## Code Location

```python
# Controller/api_server.py (lines 23-45)

# Initialize service layer
print("Initializing service layer...")
try:
    # Initialize individual services
    cohere_api = CohereAPI()                    # Line 27
    supabase_service = SupabaseService()        # Line 28
    pexels_api = PexelsAPI()                    # Line 29
    frontend_service = FrontendService()         # Line 30
    
    # Initialize main backend service that orchestrates all services
    backend_service = BackendService(           # Lines 33-37
        cohere_api=cohere_api,
        supabase_service=supabase_service,
        pexels_api=pexels_api
    )
    print("✅ Service layer initialized successfully")
    # ... logging output ...
except Exception as e:
    raise ConnectionError(f"Failed to initialize service layer: {e}")
```

## Sequence Diagram Representation

All these objects can be represented in sequence diagrams:

```
User (Actor)
  ↓
FrontendService (Component/Object)
  ↓
BackendService (Component/Object)
  ↓
  ├─→ CohereAPI (Component/Object)
  ├─→ SupabaseService (Component/Object)
  └─→ PexelsAPI (Component/Object)
```

## Benefits

1. **Clear Object Representation**: Each component is a distinct object that can be shown in sequence diagrams
2. **Separation of Concerns**: Each service handles one specific responsibility
3. **Testability**: Services can be easily mocked and tested independently
4. **Maintainability**: Changes to one service don't affect others
5. **Sequence Diagram Clarity**: All components are clearly defined as objects

