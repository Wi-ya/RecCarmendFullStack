# How to Run

Use a **single `.env` at the project root** for secrets (COHERE_API_KEY, DB_URL, DB_API_KEY, PEXELS_API_KEY, VITE_* for frontend).  
Use a **single `.venv` at the project root** for all Python work.

## Required software

- Python 3.10+ (3.11, 3.12, or 3.14 recommended; 3.9 works with relaxed pins)
- Node.js and npm

Commands below: macOS/Linux first, then Windows.

## Step 1: One virtual environment at project root

Create and activate one venv at the project root. All Python (Controller, Database, Webscraping, Cohere, Pexels) use this same venv.

**macOS/Linux:**
```bash
cd ReccarmendFullStack
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
(Use `python3.11`, `python3.12`, or `python3` if you don't have 3.14.)

**Windows (Command Prompt or PowerShell):**
```cmd
cd ReccarmendFullStack
py -3.14 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

The root `requirements.txt` pulls in Controller, Database_Model_Connection, and Webscraping dependencies in one go. You can delete any `.venv` (or `venv`) inside subfolders and use only this root `.venv`.

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

From the **project root** (with `.venv` activated):

**macOS/Linux:**
```bash
cd ReccarmendFullStack
source .venv/bin/activate
python3 -m Controller.api_server
```

**Windows:**
```cmd
cd ReccarmendFullStack
.venv\Scripts\activate
python -m Controller.api_server
```

Backend runs at `http://localhost:5001`.

## Step 4: Run the Frontend

Open a **new terminal**:

**macOS/Linux:**
```bash
cd ReccarmendFullStack/View
npm install
npm run dev
```

**Windows:**
```cmd
cd ReccarmendFullStack\View
npm install
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

