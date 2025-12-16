# How to Run

This document will explain how to run this project. We assume that you have obtained the project files from a zip file. So .env files should be included.
If this project is pulled from github, you will need to create .env files for some folders for sensitive information such as COHERE_API_KEY, SUPABASE_URL, SUPABASE_URL and PEXELS_API_KEY

## Required software

- Python 3.8+ installed
- Node.js and npm installed

There will be 2 example commands for the entire step: one for macOS/Linux and one for Windows terminal.

## Step 1: Install Python Dependencies

Install dependencies for each Python module:
These terminal commands download all the library requirements for each virtual environment in each module. 

At each stage, make sure your terminal is in the project folder so that cd command directs terminal to the correct moudle.

### Controller (Backend API)

**macOS/Linux:**
```bash
cd Controller
pip install -r requirements.txt
cd ..
```

**Windows (Command Prompt or PowerShell):**
```cmd
cd Controller
pip install -r requirements.txt
cd ..
```

### Database Model Connection

**macOS/Linux:**
```bash
cd Database_Model_Connection
pip install -r requirements.txt
cd ..
```

**Windows (Command Prompt or PowerShell):**
```cmd
cd Database_Model_Connection
pip install -r requirements.txt
cd ..
```

### Webscraping

**macOS/Linux:**
```bash
cd Webscraping
pip install -r requirements.txt
cd ..
```

**Windows (Command Prompt or PowerShell):**
```cmd
cd Webscraping
pip install -r requirements.txt
cd ..
```

The `Cohere` and `Pexels` folders don't have separate requirements.txt files - their dependencies are included in the Controller requirements.txt. They use the same venv so that Controller can import Cohere and Pexels directly.

## Step 2: Install Frontend Dependencies

**macOS/Linux:**
```bash
cd View
npm install
cd ..
```

**Windows (Command Prompt or PowerShell):**
```cmd
cd View
npm install
cd ..
```

## Step 3: Run the Backend

Open a terminal and run:

**macOS/Linux:**
```bash
cd Controller
python3 api_server.py
```

**Windows (Command Prompt or PowerShell):**
```cmd
cd Controller
python api_server.py
```

The backend will start on `http://localhost:5001`

## Step 4: Run the Frontend

Open a **new terminal** and run:

**macOS/Linux:**
```bash
cd View
npm run dev
```

**Windows (Command Prompt or PowerShell):**
```cmd
cd View
npm run dev
```

The frontend will start on `http://localhost:8080` (or another port if 8080 is taken)

## The servers are up and you can look at the website from localhost.

- Frontend: Open `http://localhost:8080` in your browser
- Backend API: Running on `http://localhost:5001`

Make sure both terminals are running simultaneously - the frontend needs the backend to be running.

## How to Stop the Servers

To stop either the backend or frontend server without closing your IDE:

1. **Click on the terminal window** where the server is running
2. **Press `Ctrl+C`** (on both macOS/Linux and Windows)
3. The server will stop

**Note:** You have to do this for both frontend and backend server or you can just close the IDE directly.

**Additional Notes:** Most important functional methods have commented input arguments and output as well as explanation for readibility.

