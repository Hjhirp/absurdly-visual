# Deployment Guide - Absurdly Visual

## Quick Deploy

### Backend (Railway)
1. Connect Railway to GitHub repo
2. Set environment variables:
```
GEMINI_API_KEY=your_key
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
SUPABASE_BUCKET=videos
PORT=8000
```
3. Deploy from `/backend` directory
4. Railway will auto-detect Python and run

### Frontend (Vercel)
1. Connect Vercel to GitHub repo
2. Set build settings:
   - Framework: Create React App
   - Root Directory: `frontend`
   - Build Command: `npm run build:prod`
   - Output Directory: `build`
3. Set environment variables:
```
REACT_APP_API_URL=https://your-railway-app.railway.app
REACT_APP_WS_URL=https://your-railway-app.railway.app
```
4. Deploy

## Features Implemented

### ✅ Game Flow
- Players join lobby (min 3 players)
- AI bots with random personalities (8 types)
- 5 points to win
- Confetti on winner announcement

### ✅ Content Generation
- **Images**: Generated with Gemini (9:16 aspect)
- **Narration**: Gemini TTS with humor
- **Video**: Veo3 for 8-second clips
- **Moderation**: Gemini sanitizes prompts before generation

### ✅ Real-time Updates
- Socket.IO for live game state
- Image + audio appear first (~5-10s)
- Video replaces image when ready (~30-60s)
- All players see all submissions with media

### ✅ Public Feed
- Winning videos saved to Supabase
- TikTok-like feed at `/api/feed/videos`
- Likes, views, comments supported
- Trending endpoint available

### ✅ AI Players
- 8 personalities: absurd, edgy, wholesome, chaotic, sarcastic, punny, dark_humor, innocent
- Random personality each game
- Gemini-powered card selection
- Gemini-powered judging

## API Endpoints

### Game
- `POST /api/game/create` - Create game
- `GET /api/games` - List games
- WebSocket: `/socket.io`

### Feed
- `GET /api/feed/videos` - Get feed
- `GET /api/feed/trending` - Trending videos
- `POST /api/feed/like` - Like video
- `POST /api/feed/view/{id}` - Track view

### Content
- `POST /api/content/generate` - Generate content
- `POST /api/images/generate` - Generate image
- `POST /api/narration/generate` - Generate TTS

## Environment Variables

### Required
- `GEMINI_API_KEY` - Gemini API key
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase anon key

### Optional
- `POINTS_TO_WIN=5` - Points needed to win
- `MAX_PLAYERS=8` - Max players per game
- `VIDEO_DURATION=8` - Video length in seconds
- `USE_VEO3_FAST=true` - Use fast Veo3 model

## Testing Locally

```bash
# Backend
cd backend
./run_stage.sh

# Frontend
cd frontend
./start-dev.sh
```

Access: http://localhost:3000

## Hackathon Demo Flow

1. **Start**: Player creates game
2. **Add AI**: Click "Add AI Bot" (3 times for demo)
3. **Start Game**: Click "Start Game"
4. **Play**: Submit cards, czar judges
5. **Watch**: See images + audio immediately
6. **Winner**: Confetti + video generation
7. **Feed**: Visit `/feed` to see winning videos

## Tech Stack

- **Backend**: FastAPI, Socket.IO, Python
- **Frontend**: React, TypeScript, TailwindCSS
- **AI**: Gemini (LLM, TTS, Moderation), Veo3 (Video)
- **Storage**: Supabase (DB + Storage)
- **Deploy**: Railway (Backend), Vercel (Frontend)
