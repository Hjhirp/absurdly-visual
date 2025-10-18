# Railway Deployment Guide

## Backend Deployment

### 1. Create New Project on Railway
1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account and select this repository
5. Choose the `backend` directory as the root

### 2. Configure Environment Variables
Add these in Railway Dashboard → Variables:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_BUCKET=videos
SUPABASE_WINNING_BUCKET=winning-videos

# Optional
DEBUG=False
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=https://your-frontend-url.vercel.app,http://localhost:3000

# Fetch.ai (Optional)
FETCHAI_AGENT_ADDRESS=
FETCHAI_AGENT_ENDPOINT=

# Game Settings
CARDS_PER_HAND=5
POINTS_TO_WIN=7
VIDEO_DURATION=4
```

### 3. Deploy
Railway will automatically:
- Detect Python app
- Install dependencies from `requirements.txt`
- Run the start command from `Procfile`
- Assign a public URL

### 4. Get Your Backend URL
After deployment, Railway will give you a URL like:
```
https://your-app.up.railway.app
```

## Frontend Deployment (Vercel/Netlify)

### 1. Update Frontend Environment
Create `frontend/.env.production`:

```bash
REACT_APP_API_URL=https://your-backend.up.railway.app
REACT_APP_WS_URL=wss://your-backend.up.railway.app
```

### 2. Update CORS on Backend
Add your frontend URL to `CORS_ORIGINS` in Railway:
```
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
```

### 3. Deploy Frontend
```bash
cd frontend
npm run build
# Deploy to Vercel/Netlify
```

## Testing Deployment

### 1. Test Backend Health
```bash
curl https://your-backend.up.railway.app/health
```

Should return:
```json
{"status": "healthy"}
```

### 2. Test WebSocket
Open browser console on your frontend and check for:
```
✅ Socket connected
```

### 3. Test Video Generation
Play a game round and check:
- Videos generate during judging phase
- Videos upload to Supabase
- Videos display in game

## Troubleshooting

### Backend won't start
- Check Railway logs for errors
- Verify all environment variables are set
- Check `PORT` is not hardcoded (Railway sets it)

### CORS errors
- Add frontend URL to `CORS_ORIGINS`
- Include both `http://` and `https://`
- Restart backend after changing

### Videos not generating
- Check `GEMINI_API_KEY` is set
- Check Railway logs for Veo3 errors
- Verify Supabase bucket exists and is public

### WebSocket connection fails
- Use `wss://` (not `ws://`) for production
- Check firewall/proxy settings
- Verify Railway app is running

## Monitoring

### Railway Dashboard
- View logs in real-time
- Monitor CPU/Memory usage
- Check deployment history

### Supabase Dashboard
- Monitor video storage usage
- Check database queries
- View API usage

## Scaling

### Railway
- Upgrade plan for more resources
- Enable auto-scaling
- Add custom domains

### Optimization
- Videos are 720p (smaller size)
- In-memory cache (no Redis needed)
- Cards loaded from Supabase

## Cost Estimates

### Railway (Backend)
- Hobby: $5/month (500 hours)
- Pro: $20/month (unlimited)

### Supabase (Database + Storage)
- Free: 500MB storage, 2GB bandwidth
- Pro: $25/month (8GB storage, 50GB bandwidth)

### Google Gemini (Veo3)
- Pay per video generated
- ~$0.10-0.50 per video (estimate)

## Support

- Railway Docs: https://docs.railway.app
- Supabase Docs: https://supabase.com/docs
- GitHub Issues: Create an issue in your repo
