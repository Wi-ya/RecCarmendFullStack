# ReCarmend System Sequence Diagram

## Mermaid Format (for Figma import or recreation)

```mermaid
sequenceDiagram
    participant User
    participant Frontend as Frontend<br/>(React/Vite)
    participant Backend as Backend<br/>(Flask API)
    participant Cohere as Cohere AI<br/>(NLP)
    participant Supabase as Supabase<br/>(Database)
    participant Pexels as Pexels API<br/>(Images)

    activate User
    User->>Frontend: 1. searchCars(query)<br/>"red SUV under $30k"
    activate Frontend
    
    Frontend->>Backend: 2. POST /api/search<br/>search(query)
    activate Backend
    
    Backend->>Cohere: 3. co.chat()<br/>aiSearch(prompt)
    activate Cohere
    Cohere-->>Backend: 4. return parsed_params<br/>{make: null, price: 30000, bodyType: SUV}
    deactivate Cohere
    
    Backend->>Supabase: 5. sortDB()<br/>query.select().limit(10).execute()
    activate Supabase
    Supabase-->>Backend: 6. return cars[]<br/>[{id, make, model, year, ...}, ...]
    deactivate Supabase
    
    loop For each car (max 10)
        Backend->>Pexels: 7. get_car_image_url()<br/>requests.get(search_url)
        activate Pexels
        Pexels-->>Backend: 8. return image_url<br/>https://images.pexels.com/...
        deactivate Pexels
    end
    
    Backend->>Backend: 9. format_car_results()<br/>Add colorHex, imageUrl
    
    Backend-->>Frontend: 10. return jsonify()<br/>{cars: [...], count: 10, hasMore: true}
    deactivate Backend
    
    Frontend->>Frontend: 11. normalizeCar()<br/>Process response data
    
    Frontend-->>User: 12. render CarCard[]<br/>Display car cards with images
    deactivate Frontend
    deactivate User
```

## Alternative: Filter-Based Search Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend as Frontend<br/>(React/Vite)
    participant Backend as Backend<br/>(Flask API)
    participant Supabase as Supabase<br/>(Database)
    participant Pexels as Pexels API<br/>(Images)

    activate User
    User->>Frontend: 1. searchCarsWithFilters(filters)
    activate Frontend
    
    Frontend->>Backend: 2. POST /api/search/filtered<br/>filtered_search()
    activate Backend
    
    Backend->>Supabase: 3. sortDB()<br/>query.select().limit(10).execute()
    activate Supabase
    Supabase-->>Backend: 4. return cars[]<br/>[{id, make, model, ...}, ...]
    deactivate Supabase
    
    loop For each car (max 10)
        Backend->>Pexels: 5. get_car_image_url()<br/>requests.get(search_url)
        activate Pexels
        Pexels-->>Backend: 6. return image_url
        deactivate Pexels
    end
    
    Backend->>Backend: 7. format_car_results()<br/>Add colorHex, imageUrl
    
    Backend-->>Frontend: 8. return jsonify()<br/>{cars: [...], count: 10, hasMore: true}
    deactivate Backend
    
    Frontend->>Frontend: 9. normalizeCar()<br/>Process response
    
    Frontend-->>User: 10. render CarCard[]<br/>Display filtered results
    deactivate Frontend
    deactivate User
```

## Components Summary

**Frontend (React/Vite):**
- User interface
- Search input & filters
- Car card display
- API service layer

**Backend (Flask API):**
- REST API endpoints
- Request processing
- Data formatting
- Image fetching orchestration

**Cohere AI:**
- Natural language processing
- Query parsing
- Parameter extraction

**Supabase:**
- PostgreSQL database
- Car listings storage
- Query execution
- Data filtering

**Pexels API:**
- Image search
- Car photo retrieval
- Image URL generation

## Key Rules Applied:
- ✅ Function calls use solid arrows (→)
- ✅ Return values use dotted arrows (-->>)
- ✅ User lifeline spans entire diagram (activate/deactivate)
- ✅ All components have activation boxes when active
- ✅ Loop notation for repeated operations
- ✅ Self-calls shown for internal processing
