# Absurdly Visual - Setup Guide

A multiplayer Cards Against Humanity game with AI bots, video generation via Fetch.ai uAgent, and a TikTok-style video feed powered by Supabase.

## 🎯 Features

- **Multiplayer Game**: Real-time gameplay with WebSocket
- **AI Bots**: Gemini-powered AI players with different personalities
- **Video Generation**: Fetch.ai uAgent integration for generating absurd videos
- **Video Feed**: TikTok/Instagram Reel-style feed with likes and comments
- **Supabase Backend**: Scalable database and storage for videos

## 📋 Prerequisites

- Node.js 16+ and npm
- Python 3.9+
- Supabase account (free tier works)
- Google Gemini API key
- Fetch.ai uAgent deployed on marketplace (optional for video generation)

## 🚀 Quick Start

### 1. Supabase Setup

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to SQL Editor and run the schema from `backend/supabase_schema.sql`
3. Go to Storage and create a bucket named `videos` (make it public)
4. Copy your project URL and anon key from Settings > API

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your keys:
# - SUPABASE_URL
# - SUPABASE_KEY
# - GEMINI_API_KEY
# - FETCHAI_AGENT_ADDRESS (optional)
# - FETCHAI_AGENT_ENDPOINT (optional)

# Run the server
python -m app.main
```

Backend will run on http://localhost:8000

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will run on http://localhost:3000

## 🤖 Fetch.ai uAgent Setup (Optional)

To enable video generation, you need to deploy a Fetch.ai uAgent that generates videos:

### uAgent Requirements

Your uAgent should expose an endpoint that accepts:

```json
{
  "prompt": "string",
  "black_card": "string",
  "white_cards": ["string"],
  "duration": 4,
  "style": "absurd_comedy"
}
```

And returns:

```json
{
  "video_url": "https://your-storage.com/video.mp4"
}
```

### Deploy to Fetch.ai Marketplace

1. Create your video generation uAgent using Fetch.ai SDK
2. Deploy to Fetch.ai marketplace
3. Copy the agent address and endpoint URL
4. Add to your `.env`:
   ```
   FETCHAI_AGENT_ADDRESS=agent1q...
   FETCHAI_AGENT_ENDPOINT=https://your-agent-endpoint.com/generate-video
   ```

## 📊 Database Schema

The Supabase database includes:

- **videos**: Stores video metadata (cards, URL, likes, comments)
- **likes**: User likes on videos
- **comments**: User comments on videos

All tables have Row Level Security (RLS) enabled for public read access.

## 🎮 How to Play

1. **Create a Game**: Enter your name and create a new game
2. **Add AI Bots**: Click "+ Add AI Bot" to add AI players
3. **Start Game**: Once you have 3+ players, click "Start Game"
4. **Play Rounds**: 
   - Submit your funniest white cards
   - If you're the Czar, judge the submissions
   - AI bots play automatically
5. **Watch Videos**: Click "📹 Watch Feed" to see generated videos in TikTok-style feed

## 🎨 Video Feed Features

- **Vertical Scrolling**: Swipe or scroll to navigate videos
- **Like Videos**: Tap the heart to like
- **Comment**: Add comments with your name
- **Share**: Share videos (coming soon)

## 🔧 Configuration

### Backend (.env)

```bash
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_BUCKET=videos

# Fetch.ai
FETCHAI_AGENT_ADDRESS=agent1q...
FETCHAI_AGENT_ENDPOINT=https://your-agent.com/generate-video

# AI Services
GEMINI_API_KEY=your-gemini-api-key

# Game Settings
MAX_PLAYERS=8
MIN_PLAYERS=3
POINTS_TO_WIN=7
```

## 🐛 Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Verify all environment variables are set
- Check Python version (3.9+)

### Frontend can't connect
- Ensure backend is running on port 8000
- Check CORS settings in backend config
- Verify WebSocket connection in browser console

### Video generation fails
- Check Fetch.ai agent endpoint is accessible
- Verify agent address is correct
- Check agent logs for errors
- Video generation is optional - game works without it

### Supabase errors
- Verify URL and key are correct
- Check if SQL schema was run successfully
- Ensure storage bucket is created and public

## 📚 API Endpoints

### Game API (WebSocket)
- `create_game`: Create a new game
- `join_game`: Join existing game
- `start_game`: Start the game
- `submit_cards`: Submit white cards
- `select_winner`: Czar selects winner
- `request_ai_join`: Add AI bot

### Feed API (REST)
- `GET /api/feed/videos`: Get video feed
- `GET /api/feed/videos/{id}`: Get specific video
- `POST /api/feed/like`: Like/unlike video
- `POST /api/feed/comment`: Add comment
- `GET /api/feed/comments/{video_id}`: Get comments

## 🎯 Next Steps

1. **Deploy Fetch.ai uAgent**: Set up video generation
2. **Add More Card Packs**: Expand the game content
3. **User Authentication**: Add user accounts
4. **Video Sharing**: Social media integration
5. **Mobile App**: React Native version

## 📝 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

## 💬 Support

For issues or questions, please open a GitHub issue.
