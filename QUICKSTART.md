# 🚀 Quick Start Guide - Absurdly Visual

Get up and running in 5 minutes!

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)

## Option 1: Docker (Recommended)

### 1. Setup Environment Files

```bash
# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env
```

### 2. Start Everything

```bash
docker-compose up --build
```

### 3. Access the Game

Open your browser to: **http://localhost:3000**

That's it! 🎉

---

## Option 2: Manual Setup

### Backend Setup

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Edit .env with your API keys (optional for demo)

# 5. Run the server
python -m uvicorn app.main:socket_app --reload --port 8000
```

Backend will be available at: **http://localhost:8000**

### Frontend Setup

```bash
# 1. Navigate to frontend (in a new terminal)
cd frontend

# 2. Install dependencies
npm install

# 3. Setup environment
cp .env.example .env

# 4. Start the app
npm start
```

Frontend will open automatically at: **http://localhost:3000**

---

## Option 3: With Fetch.ai Agents

### 1. Start Backend & Frontend

Follow Option 2 above.

### 2. Start Fetch.ai Agents

```bash
# Terminal 3 - Coordinator Agent
cd fetch-agents/coordinator_agent
pip install -r ../requirements.txt
python agent.py

# Terminal 4 - Video Agent
cd fetch-agents/video_agent
python agent.py

# Terminal 5 - AI Player Agent
cd fetch-agents/ai_player_agent
python agent.py
```

### 3. Configure Backend

Update `backend/.env`:
```bash
FETCH_COORDINATOR_URL=http://localhost:8001
FETCH_VIDEO_AGENT_URL=http://localhost:8002
FETCH_AI_PLAYER_URL=http://localhost:8003
```

---

## 🎮 How to Play

### 1. Create a Game
- Enter your name
- Click "Create New Game"
- Share the Game ID with friends

### 2. Add Players
- Have friends join with the Game ID
- Or click "Add AI Bot" to add computer players
- Need 3+ players to start

### 3. Start Playing
- Click "Start Game" when ready
- Each round, one player is the Card Czar
- Others submit their funniest white cards
- Czar picks the winner
- **AI generates a video of the winning combo!** 🎬

### 4. Win the Game
- First player to 7 points wins!

---

## 🧪 Testing

### Test Backend API
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/cards/black
```

### Test Agents
```bash
# Coordinator
curl http://localhost:8001/health

# Video Agent
curl http://localhost:8002/health

# AI Player
curl http://localhost:8003/health
```

---

## 🔧 Configuration

### Backend (.env)
```bash
# Required for basic functionality
MONGODB_URL=mongodb://localhost:27017  # Optional
REDIS_URL=redis://localhost:6379      # Optional

# Required for AI features
VEO3_API_KEY=your_veo3_key            # For video generation
GEMINI_API_KEY=your_gemini_key        # For AI players

# Fetch.ai Agents
FETCH_COORDINATOR_URL=http://localhost:8001
```

### Frontend (.env)
```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Backend Won't Start
- Check Python version: `python --version` (need 3.11+)
- Verify virtual environment is activated
- Check all dependencies installed: `pip list`

### Frontend Won't Start
- Check Node version: `node --version` (need 18+)
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`
- Clear cache: `npm cache clean --force`

### WebSocket Connection Failed
- Ensure backend is running on port 8000
- Check CORS settings in backend config
- Verify firewall isn't blocking connections

### Videos Not Generating
- This is normal without Veo3 API key
- Mock videos will be shown instead
- Add VEO3_API_KEY to enable real video generation

---

## 📊 API Documentation

Once backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🎯 Demo Mode

Want to demo quickly without API keys?

1. Start backend and frontend (Option 1 or 2)
2. Create a game
3. Add 2-3 AI bots
4. Start playing!

Mock videos will be generated automatically. Perfect for testing and demos!

---

## 🚀 Production Deployment

### Deploy to Agentverse

1. Create agents on https://agentverse.ai
2. Upload agent code from `fetch-agents/`
3. Update backend .env with Agentverse URLs

### Deploy Backend

```bash
# Build Docker image
docker build -t absurdly-visual-backend ./backend

# Run container
docker run -p 8000:8000 --env-file backend/.env absurdly-visual-backend
```

### Deploy Frontend

```bash
# Build for production
cd frontend
npm run build

# Serve with nginx or deploy to Vercel/Netlify
```

---

## 📚 Next Steps

- Read the full [README.md](README.md) for architecture details
- Check [fetch-agents/README.md](fetch-agents/README.md) for agent documentation
- Customize cards in `backend/data/cards.json`
- Add your own card packs
- Integrate real Veo3 and Gemini APIs

---

## 🆘 Need Help?

- Check the logs in the terminal
- Visit the API docs at http://localhost:8000/docs
- Review the architecture in README.md

---

**Have fun playing Absurdly Visual! 🎭🎬**
