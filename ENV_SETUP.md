# Environment Variables Setup Guide

## Frontend Environment Variables

Create a file named `.env` in the `View/` directory with the following:

```bash
# Supabase Configuration
# Get these from: Supabase Dashboard → Settings → API
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=your-anon-key-here

# Backend API URL
# This is where your Flask API server is running
VITE_API_URL=http://localhost:5000
```

**How to get Supabase credentials:**
1. Go to your Supabase project dashboard
2. Navigate to Settings → API
3. Copy the "Project URL" → use for `VITE_SUPABASE_URL`
4. Copy the "anon public" key → use for `VITE_SUPABASE_PUBLISHABLE_KEY`

---

## Backend Environment Variables

Create a file named `.env` in the `Controller/` directory with the following:

```bash
# Supabase Database Configuration
# Get these from: Supabase Dashboard → Settings → API
# Use the Service Role key (not the anon key) for backend access
DB_URL=https://your-project.supabase.co
DB_API_KEY=your-service-role-key-here

# Cohere AI API Key
# Get this from: https://dashboard.cohere.com/api-keys
COHERE_API_KEY=your-cohere-api-key-here
```

**How to get Supabase credentials:**
1. Go to your Supabase project dashboard
2. Navigate to Settings → API
3. Copy the "Project URL" → use for `DB_URL`
4. Copy the "service_role" key → use for `DB_API_KEY` (⚠️ Keep this secret!)

**How to get Cohere API key:**
1. Go to https://dashboard.cohere.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key or copy an existing one

---

## Important Notes

1. **Never commit `.env` files to git** - They contain sensitive credentials
2. **The `.env` files should already be in `.gitignore`**
3. **Restart your servers** after updating `.env` files:
   - Frontend: Stop and restart `npm run dev`
   - Backend: Stop and restart `python api_server.py`

---

## Quick Setup Commands

### Frontend
```bash
cd View
# Create .env file (copy the template above and fill in your values)
# Then restart the dev server
npm run dev
```

### Backend
```bash
cd Controller
# Create .env file (copy the template above and fill in your values)
# Install dependencies if needed
pip install -r requirements.txt
# Then start the API server
python api_server.py
```


