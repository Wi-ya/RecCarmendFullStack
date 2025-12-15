# Deployment and Testing Guide

## Current Limitations (If Deployed)

### API Rate Limits (Free Tiers)

1. **Cohere AI**
   - Free tier: Limited requests per month
   - Each search uses 1 Cohere API call
   - **Limit**: ~100-1000 requests/month (depends on your plan)
   - **Solution**: Upgrade to paid plan for more requests

2. **Pexels API**
   - Free tier: **200 requests/hour**
   - Each search fetches up to 10 images (1 request per car)
   - **Limit**: 200 searches/hour = ~20 users/hour (if each user searches once)
   - **Solution**: Code already handles rate limits with fallback images

3. **Supabase (Database)**
   - Free tier: 
     - 500 MB database storage
     - 2 GB bandwidth/month
     - Unlimited API requests (but bandwidth limited)
   - **Limit**: ~50,000-100,000 database queries/month
   - **Solution**: Upgrade to Pro plan ($25/month) for more

4. **Flask Backend (Hosting)**
   - Depends on hosting provider
   - Free tiers (Heroku, Railway, Render): Limited hours/month
   - **Solution**: Use paid hosting or self-host

## How to Let Someone Test Your Website

### Option 1: Share on Local Network (Easiest for Testing)

1. **Find your local IP address:**
   ```bash
   # On Mac/Linux
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # Or
   ipconfig getifaddr en0
   ```

2. **Update CORS in backend:**
   ```python
   # In Controller/api_server.py, line 21
   CORS(app, origins=[
       "http://localhost:8080",
       "http://127.0.0.1:8080",
       "http://localhost:5001",
       "http://YOUR_IP:8080",  # Add your IP
       "http://YOUR_IP:5001"   # Add your IP
   ])
   ```

3. **Start both servers:**
   ```bash
   # Terminal 1 - Backend
   cd Controller
   python3 api_server.py
   # Note the IP address shown (e.g., http://192.168.1.134:5001)
   
   # Terminal 2 - Frontend
   cd View
   npm run dev
   # Note the IP address shown (e.g., http://192.168.1.134:8080)
   ```

4. **Share the frontend URL:**
   - Give tester: `http://YOUR_IP:8080`
   - They must be on the same WiFi/network

### Option 2: Use ngrok (Share Publicly - Best for Testing)

1. **Install ngrok:**
   ```bash
   # Download from https://ngrok.com/download
   # Or install via Homebrew (Mac)
   brew install ngrok
   ```

2. **Start your backend:**
   ```bash
   cd Controller
   python3 api_server.py
   ```

3. **Create ngrok tunnel for backend:**
   ```bash
   ngrok http 5001
   # Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
   ```

4. **Update frontend .env:**
   ```bash
   # In View/.env
   VITE_API_URL=https://abc123.ngrok.io
   ```

5. **Start frontend:**
   ```bash
   cd View
   npm run dev
   ```

6. **Create ngrok tunnel for frontend:**
   ```bash
   # In a new terminal
   ngrok http 8080
   # Copy the HTTPS URL (e.g., https://xyz789.ngrok.io)
   ```

7. **Share the frontend ngrok URL** with your tester

**Note**: ngrok free tier has limitations (connection timeouts, random URLs)

### Option 3: Deploy to Production (For Real Use)

#### Quick Deploy Options:

1. **Render.com** (Free tier available)
   - Deploy backend: Connect GitHub repo, set build command
   - Deploy frontend: Static site deployment
   - **Free tier**: Sleeps after inactivity

2. **Railway.app** (Free tier available)
   - Similar to Render
   - Better for backend APIs

3. **Vercel** (Free tier - best for frontend)
   - Deploy frontend easily
   - Backend can use serverless functions

4. **Heroku** (Paid now, but reliable)
   - $7/month for backend
   - Good for production

#### Deployment Checklist:

- [ ] Update CORS to allow production domain
- [ ] Set environment variables on hosting platform
- [ ] Update frontend `.env` with production API URL
- [ ] Configure database connection for production
- [ ] Set up error monitoring
- [ ] Configure rate limiting
- [ ] Set up SSL/HTTPS certificates

## Current Configuration for Testing

### Backend CORS (Currently Limited)
```python
# Controller/api_server.py line 21
CORS(app, origins=["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:5001"])
```

**To allow others to test, update to:**
```python
CORS(app, origins=["*"])  # Allows all origins (for testing only!)
# OR better:
CORS(app, origins=[
    "http://localhost:8080",
    "http://127.0.0.1:8080", 
    "http://localhost:5001",
    "http://YOUR_IP:8080",      # Your local IP
    "https://your-ngrok-url.ngrok.io"  # ngrok URL if using
])
```

## Recommendations

### For Testing (1-5 users):
- ✅ Use **Option 1** (local network) or **Option 2** (ngrok)
- ✅ Free API tiers should be sufficient
- ✅ No deployment needed

### For Production (Many users):
- ⚠️ Upgrade API plans (Cohere, Pexels)
- ⚠️ Upgrade Supabase to Pro plan
- ⚠️ Deploy to proper hosting
- ⚠️ Implement rate limiting
- ⚠️ Add caching for images
- ⚠️ Monitor API usage

## Quick Test Setup Commands

```bash
# 1. Get your IP address
ipconfig getifaddr en0  # Mac
# or
hostname -I  # Linux

# 2. Update CORS in api_server.py (add your IP)

# 3. Start backend
cd Controller && python3 api_server.py

# 4. Start frontend  
cd View && npm run dev

# 5. Share URL: http://YOUR_IP:8080
```

