# Backend Connection Plan - Step by Step

## Overview
This document outlines all the steps needed to connect your React frontend to your Python backend.

## Current State
- **Frontend**: React app with mock data, ready to make API calls
- **Backend**: Python CLI script (`recarmend-2.py`) that needs to be converted to a REST API
- **Database**: Supabase (configured but needs credentials)
- **AI**: Cohere API (configured in backend)

## Tasks Breakdown

### ✅ Task 1: Convert Python Backend to REST API
**Status**: In Progress

**What needs to be done:**
- Convert `recarmend-2.py` from CLI script to Flask/FastAPI web server
- Extract the core functions (`sortDB`, `aiSearch`, `filteredSearch`) 
- Create REST API endpoints that accept JSON and return JSON
- Handle errors gracefully

**Files to create:**
- `Controller/api_server.py` - New Flask API server
- Update `Controller/requirements.txt` to include Flask and flask-cors

---

### ⏳ Task 2: Create API Endpoints
**Status**: Pending

**Endpoints needed:**
1. `POST /api/search` - AI-powered search
   - Accepts: `{ "query": "user's natural language description" }`
   - Returns: `{ "cars": [...], "count": 10 }`

2. `POST /api/search/filtered` - Filter-based search
   - Accepts: `{ "filters": { "maxPrice": 35000, "bodyTypes": ["SUV"], ... } }`
   - Returns: `{ "cars": [...], "count": 10 }`

3. `GET /api/cars` - Get all cars (optional, for testing)
   - Returns: `{ "cars": [...], "count": 100 }`

---

### ⏳ Task 3: Set Up Environment Variables
**Status**: Pending

**Frontend `.env` file** (`View/.env`):
```
VITE_SUPABASE_URL=your-supabase-url
VITE_SUPABASE_PUBLISHABLE_KEY=your-supabase-anon-key
VITE_API_URL=http://localhost:5000
```

**Backend `.env` file** (`Controller/.env`):
```
DB_URL=your-supabase-url
DB_API_KEY=your-supabase-service-role-key
COHERE_API_KEY=your-cohere-api-key
```

---

### ⏳ Task 4: Configure CORS
**Status**: Pending

**What needs to be done:**
- Install `flask-cors` in backend
- Configure CORS to allow requests from frontend (localhost:8080)
- Handle preflight requests

---

### ⏳ Task 5: Create Frontend API Service
**Status**: Pending

**Files to create:**
- `View/src/services/api.ts` - API client functions
  - `searchCars(query: string, filters?: Filters)`
  - `searchCarsWithFilters(filters: Filters)`
  - Error handling and loading states

---

### ⏳ Task 6: Update Frontend Components
**Status**: Pending

**Files to update:**
- `View/src/components/SearchChat.tsx` - Call API instead of mock
- `View/src/pages/Results.tsx` - Fetch real data from API
- Remove mock data (`MOCK_CARS`)

---

### ⏳ Task 7: Configure Supabase
**Status**: Pending

**What needs to be done:**
- Get Supabase credentials from dashboard
- Update `.env` files with real values
- Verify database tables exist:
  - `CarListings` - Car inventory
  - `search_history` - User search history
  - `users` - User authentication (handled by Supabase Auth)

---

### ⏳ Task 8: Test End-to-End
**Status**: Pending

**Test flow:**
1. Start backend server (`python api_server.py`)
2. Start frontend server (`npm run dev`)
3. Test AI search: Type query → See results
4. Test filtered search: Use filters → See results
5. Test authentication: Sign up → Login → Check history
6. Verify data flows correctly through entire stack

---

## Architecture Flow

```
User Input (Frontend)
    ↓
React Component (SearchChat.tsx)
    ↓
API Service (api.ts)
    ↓ HTTP Request
Backend API (api_server.py)
    ↓
Cohere AI (for natural language)
    ↓
Supabase Database (CarListings table)
    ↓
Backend processes results
    ↓ HTTP Response
Frontend displays results
```

---

## Next Steps
1. ✅ Start with Task 1 (Convert backend to API)
2. Then move to Task 2 (Create endpoints)
3. Continue sequentially through all tasks

