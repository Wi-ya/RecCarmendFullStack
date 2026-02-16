This project is a content generation pipeline. 
Users can use filters or raw text (parsed by AI) to get a list of appropriate car recommendations.
It automates the process of gathering car sales data through webscraping.
User input is processed through Cohere LLM, and results are produced through non-copyright content from Pexels API. 
The system is built with the MVC architectural style.

Key Features

AI Integration: Used Cohere API for parsing raw text from users into filter options.
Automated Scraping: Custom-built scraping module from a specific website to pull real-world data.
Media Integration: Copyright free image retrieval using the Pexels API.
Persistence: Backend connection to Supabase for secure consistent data.
Architecture: Designed with modularity and scalability as priorities (Classes and Intefaces defined for easier process of adding new scraping modules, etc).

🛠️ Tech Stack

Frontend: React, Node.js (Vite/NPM)
Backend: Python 3.8+ (API Server)
Database/Auth: Supabase
AI/External APIs: Cohere LLM, Pexels API, Beautiful Soup
