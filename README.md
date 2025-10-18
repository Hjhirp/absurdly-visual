# 🎭 Absurdly Visual - Multimodal Cards Against Humanity

A revolutionary take on Cards Against Humanity that generates AI videos for winning card combinations using Veo3, powered by Fetch.ai agents and Gemini AI players.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Fetch.ai Agentverse account
- Google Cloud account (Veo3 API access)
- Gemini API key

### Installation

1. **Clone and setup:**
```bash
cd absurdly-visual
```

2. **Backend setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

3. **Frontend setup:**
```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with backend URL
```

4. **Fetch.ai Agents setup:**
```bash
cd fetch-agents
pip install -r requirements.txt
# Deploy agents to Agentverse (see fetch-agents/README.md)
```

### Running the Application

**Option 1: Docker Compose (Recommended)**
```bash
docker-compose up
```

**Option 2: Manual**
```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm start
```

Access the game at: `http://localhost:3000`

## 🎮 How to Play

1. **Create/Join Game**: Enter your name and create a new game or join existing one
2. **Wait for Players**: Game starts with 3+ players (humans or AI bots)
3. **Read Black Card**: The Card Czar reads the question/prompt
4. **Submit White Cards**: All players (except Czar) submit their funniest answer cards
5. **Czar Judges**: Czar picks the winning combination
6. **Watch Video**: AI generates a hilarious video of the winning combo using Veo3!
7. **Next Round**: Winner gets a point, new Czar is selected

## 🏗️ Architecture

### Tech Stack
- **Frontend**: React 18 + TypeScript + Tailwind CSS + Socket.io
- **Backend**: FastAPI + Python Socket.io + MongoDB
- **AI Agents**: Fetch.ai Agentverse + Veo3 + Gemini
- **Infrastructure**: Docker + Redis (caching)

### Key Features
- ✅ Real-time multiplayer with WebSockets
- ✅ AI bots powered by Gemini that play like humans
- ✅ Automatic video generation for winning cards (Veo3)
- ✅ Smart video caching to reduce API costs
- ✅ AI bot auto-joins when players leave
- ✅ Colonist.io-inspired clean UI
- ✅ Content filtering (family-friendly mode)

## 📁 Project Structure

```
absurdly-visual/
├── backend/          # FastAPI + Socket.io server
├── frontend/         # React + TypeScript app
├── fetch-agents/     # Fetch.ai AI agents
├── docker-compose.yml
└── README.md
```

## 🤖 Fetch.ai Agents

### 1. Coordinator Agent
Orchestrates game events and routes requests to specialized agents.

### 2. Video Generation Agent
Generates creative prompts and calls Veo3 API to create videos.

### 3. AI Player Agent
Uses Gemini to analyze cards and select the funniest combinations.

## 🎯 Demo Features

- 4-player game (2 humans + 2 AI bots)
- Complete round flow with video generation
- AI seamlessly replaces leaving players
- Pre-seeded game for instant demo

## 📊 API Documentation

Once running, visit:
- Backend API docs: `http://localhost:8000/docs`
- WebSocket events: See `backend/app/websocket/events.py`

## 🔒 Environment Variables

### Backend (.env)
```
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379
VEO3_API_KEY=your_veo3_key
GEMINI_API_KEY=your_gemini_key
FETCH_COORDINATOR_URL=your_fetch_agent_url
SECRET_KEY=your_secret_key
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

## 🎨 Credits

- Inspired by Cards Against Humanity
- Card database from internetcards
- UI inspired by colonist.io
- Powered by Fetch.ai, Veo3, and Gemini

## 📝 License

MIT License - Built for hackathon demonstration

## 🤝 Contributing

This is a hackathon project, but contributions welcome!

---

**Built with ❤️ for the Fetch.ai Hackathon**
