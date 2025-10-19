# Environment Setup Guide

## Quick Start

### Development (Localhost)

**Backend:**
```bash
cd backend
./run_dev.sh
```
Server runs on: `http://localhost:8000`

**Frontend:**
```bash
cd frontend
npm install  # First time only
./start-dev.sh
```
App runs on: `http://localhost:3000`

---

### Stage (Testing)

**Backend:**
```bash
cd backend
./run_stage.sh
```

**Frontend:**
```bash
cd frontend
./start-stage.sh
```

---

### Production

**Backend:**
```bash
cd backend
./run_prod.sh
```

**Frontend (Build):**
```bash
cd frontend
./build-prod.sh
```
Output: `./build/` directory ready for deployment

---

## Environment Files

### Backend

- `.env` - Local development (git-ignored)
- `.env.stage` - Stage environment
- `.env.prod` - Production environment

**Required Variables:**
```env
GEMINI_API_KEY=your_key_here
SUPABASE_URL=your_url_here
SUPABASE_KEY=your_key_here
```

### Frontend

- `.env.development` - Development mode
- `.env.stage` - Stage mode
- `.env.production` - Production mode

**Variables:**
```env
REACT_APP_ENV=development
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

---

## NPM Scripts (Frontend)

```bash
# Development
npm run start:dev

# Stage
npm run start:stage

# Production build
npm run build:prod

# Development build
npm run build:dev

# Stage build
npm run build:stage
```

---

## Full Stack Development

**Terminal 1 - Backend:**
```bash
cd backend
./run_dev.sh
```

**Terminal 2 - Frontend:**
```bash
cd frontend
./start-dev.sh
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- WebSocket: ws://localhost:8000/socket.io

---

## API Endpoints

### Game API
- `GET /api/health` - Health check
- `GET /api/games` - List games
- `GET /api/cards/black` - Get black cards
- `GET /api/cards/white` - Get white cards

### Content Pipeline
- `POST /api/content/generate` - Generate social media content
- `POST /api/content/round` - Generate content for game round
- `POST /api/images/generate` - Generate image
- `POST /api/narration/generate` - Generate TTS narration

### Feed (TikTok-like)
- `GET /api/feed/videos` - Get video feed
- `GET /api/feed/trending` - Get trending videos
- `POST /api/feed/like` - Like video
- `POST /api/feed/view/{id}` - Track view
- `GET /api/feed/comments/{id}` - Get comments

---

## Deployment

### Backend (Railway/Heroku)
1. Set environment variables in platform
2. Deploy from `backend/` directory
3. Use `run_prod.sh` or platform's auto-detect

### Frontend (Netlify/Vercel)
1. Build: `npm run build:prod`
2. Deploy `build/` directory
3. Set environment variables in platform

---

## Troubleshooting

**Backend won't start:**
- Check `.env.stage` has all required variables
- Ensure Supabase credentials are valid
- Check port 8000 is not in use

**Frontend won't start:**
- Run `npm install` first
- Check backend is running on port 8000
- Clear cache: `rm -rf node_modules package-lock.json && npm install`

**CORS errors:**
- Check `CORS_ORIGINS` in backend `.env`
- Ensure frontend URL is in allowed origins
