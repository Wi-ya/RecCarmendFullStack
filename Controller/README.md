# Controller

Backend API server and business logic layer.

**Main Files:**
- `api_server.py` - Flask REST API server (runs on port 5001)
- `backend_service.py` - Orchestrates all services (Cohere, Supabase, Pexels)
- `data_maintenance.py` - Scheduled scraping and database updates
- `scraping_controller.py` - Manages web scraping operations

**What it does:**
- Handles HTTP requests from the frontend
- Processes AI-powered car searches using Cohere
- Queries the database for car listings
- Formats and returns results to the frontend

