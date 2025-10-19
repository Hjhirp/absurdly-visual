# Deployment Checklist ✅

## Backend (Railway) - DONE ✅
- [x] Deployed to Railway
- [ ] Set environment variables
- [ ] Generate public domain
- [ ] Test backend health

## Frontend (Vercel) - DONE ✅  
- [x] Deployed to Vercel
- [ ] Set environment variables
- [ ] Test frontend loads

## Configuration Steps

### 1. Get Railway Backend URL
1. Go to Railway dashboard: https://railway.app/project/9b62b34d-c9ce-4834-ae11-392ea4c03558
2. Click on your service
3. Go to "Settings" → "Networking"
4. Click "Generate Domain"
5. Copy the URL (e.g., `https://absurdly-visual-production.up.railway.app`)

### 2. Set Railway Environment Variables
In Railway Dashboard → Variables, add:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_BUCKET=videos
SUPABASE_WINNING_BUCKET=winning-videos

# CORS - Add your Vercel URL
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000

# Optional
DEBUG=False
SECRET_KEY=your-secret-key
CARDS_PER_HAND=5
POINTS_TO_WIN=7
VIDEO_DURATION=4
```

### 3. Set Vercel Environment Variables
In Vercel Dashboard → Settings → Environment Variables:

```bash
REACT_APP_API_URL=https://your-backend.up.railway.app
REACT_APP_WS_URL=wss://your-backend.up.railway.app
```

Then redeploy frontend:
```bash
vercel --prod
```

### 4. Test Deployment

#### Backend Health Check
```bash
curl https://your-backend.up.railway.app/health
```

Should return:
```json
{"status": "healthy"}
```

#### Frontend Check
1. Open your Vercel URL
2. Open browser console (F12)
3. Check for WebSocket connection:
   ```
   ✅ Socket connected
   ```

#### Full Game Test
1. Create a game
2. Add AI players
3. Start game
4. Submit cards
5. Check videos generate during judging
6. Verify videos display

## Troubleshooting

### Backend Issues

**"Application failed to respond"**
- Check Railway logs
- Verify PORT environment variable is set by Railway
- Check all required env vars are set

**CORS errors**
- Add Vercel URL to CORS_ORIGINS in Railway
- Format: `https://your-app.vercel.app` (no trailing slash)
- Redeploy backend after changing

**Videos not generating**
- Check GEMINI_API_KEY is set
- Check Railway logs for Veo3 errors
- Verify Supabase bucket exists

### Frontend Issues

**Can't connect to backend**
- Check REACT_APP_API_URL is correct
- Use `https://` for API URL
- Use `wss://` for WebSocket URL
- Redeploy after env var changes

**WebSocket fails**
- Verify Railway backend is running
- Check CORS_ORIGINS includes Vercel URL
- Try connecting from localhost first

## URLs

### Your Deployments
- **Backend**: https://your-backend.up.railway.app
- **Frontend**: https://your-app.vercel.app
- **Railway Dashboard**: https://railway.app/project/9b62b34d-c9ce-4834-ae11-392ea4c03558
- **Supabase Dashboard**: https://supabase.com/dashboard

### Monitoring
- Railway logs: Real-time in dashboard
- Vercel logs: Functions tab
- Supabase: Storage and Database tabs

## Post-Deployment

### 1. Create Supabase Buckets
Run in Supabase SQL Editor:
```sql
-- See: backend/create_storage_bucket.sql
```

### 2. Migrate Cards
If not done yet:
```bash
cd backend
python migrate_cards_to_supabase.py
```

### 3. Test Video Generation
```bash
cd backend  
python test_veo3.py
```

## Success Criteria ✅

- [ ] Backend responds to health check
- [ ] Frontend loads without errors
- [ ] WebSocket connects successfully
- [ ] Can create and join games
- [ ] AI players work
- [ ] Cards display correctly
- [ ] Videos generate during judging
- [ ] Videos display in game
- [ ] Winning videos saved to feed

## Next Steps

1. Share the Vercel URL with friends
2. Monitor Railway usage/costs
3. Check Supabase storage usage
4. Monitor Gemini API costs
5. Add custom domain (optional)

## Support

- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs
- Supabase Docs: https://supabase.com/docs
- Google Gemini: https://ai.google.dev/

---

**Your app is live! 🎉**
