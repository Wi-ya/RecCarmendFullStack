# Controller

Backend API server and business logic layer.

**Main Files:**
- `api_server.py` - Flask REST API server (runs on port 5001)
- `backend_service.py` - Manages all services (Cohere, Supabase, Pexels)
- `data_maintenance.py` - Scheduled scraping and database updates, uses scraping_controller.py
- `scraping_controller.py` - Manages web scraping operations, can call different type of scrapers if more are implemented

**What it does:**
- Handles HTTP requests from the frontend
- Processes AI-powered car searches using Cohere to change sentences to filter options
- Queries the database for car listings
- Formats and returns results to the frontend to display

