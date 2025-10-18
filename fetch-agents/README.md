# Fetch.ai Agents for Absurdly Visual

This directory contains the Fetch.ai agents that power the AI features of Absurdly Visual.

## Agents Overview

### 1. Coordinator Agent (Port 8001)
The main orchestration agent that routes requests to specialized agents.

**Responsibilities:**
- Receives requests from the backend
- Routes to Video Generation Agent or AI Player Agent
- Aggregates responses

### 2. Video Generation Agent (Port 8002)
Generates videos using Veo3 API based on card combinations.

**Responsibilities:**
- Creates creative prompts from card combinations
- Calls Veo3 API for video generation
- Monitors generation status
- Returns video URLs

### 3. AI Player Agent (Port 8003)
Uses Gemini to select the funniest card combinations.

**Responsibilities:**
- Analyzes black card and available white cards
- Uses Gemini to determine the funniest combination
- Returns card selection with confidence score
- Adapts to different AI personalities

## Setup

### 1. Install Dependencies

```bash
cd fetch-agents
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in each agent directory:

```bash
# Coordinator Agent
COORDINATOR_AGENT_SEED=your_coordinator_seed
COORDINATOR_AGENT_PORT=8001
VIDEO_AGENT_ADDRESS=agent1q...
AI_PLAYER_AGENT_ADDRESS=agent1q...

# Video Agent
VIDEO_AGENT_SEED=your_video_seed
VIDEO_AGENT_PORT=8002
VEO3_API_KEY=your_veo3_api_key

# AI Player Agent
AI_PLAYER_AGENT_SEED=your_ai_player_seed
AI_PLAYER_AGENT_PORT=8003
GEMINI_API_KEY=your_gemini_api_key
```

### 3. Run Agents

Each agent can be run independently:

```bash
# Terminal 1 - Coordinator
cd coordinator_agent
python agent.py

# Terminal 2 - Video Generator
cd video_agent
python agent.py

# Terminal 3 - AI Player
cd ai_player_agent
python agent.py
```

## Deploying to Fetch.ai Agentverse

### 1. Create Agent on Agentverse

1. Go to https://agentverse.ai
2. Create a new agent
3. Copy the agent address
4. Upload the agent code

### 2. Configure Backend

Update your backend `.env` file with the agent URLs:

```bash
FETCH_COORDINATOR_URL=https://agentverse.ai/v1/agents/your-coordinator-id
FETCH_VIDEO_AGENT_URL=https://agentverse.ai/v1/agents/your-video-agent-id
FETCH_AI_PLAYER_URL=https://agentverse.ai/v1/agents/your-ai-player-id
FETCH_API_KEY=your_fetch_api_key
```

## API Endpoints

### Coordinator Agent

**POST /coordinate**
```json
{
  "action": "generate_video",
  "data": {
    "blackCard": "What's the secret to happiness?",
    "whiteCards": ["Cats with opposable thumbs"],
    "style": "comedic"
  }
}
```

### Video Generation Agent

**POST /generate**
```json
{
  "blackCard": "What's the secret to happiness?",
  "whiteCards": ["Cats with opposable thumbs"],
  "style": "comedic"
}
```

**GET /status/{generation_id}**
Returns the status of a video generation.

### AI Player Agent

**POST /play**
```json
{
  "blackCard": "What's the secret to happiness?",
  "availableCards": ["card1", "card2", "card3"],
  "personality": "absurd",
  "gameContext": {}
}
```

## Testing

Test each agent's REST API endpoint:

```bash
# Test Coordinator
curl -X POST http://localhost:8001/coordinate \
  -H "Content-Type: application/json" \
  -d '{"action":"generate_video","data":{"blackCard":"Test","whiteCards":["Test"]}}'

# Test Video Agent
curl -X POST http://localhost:8002/generate \
  -H "Content-Type: application/json" \
  -d '{"blackCard":"Test","whiteCards":["Test"],"style":"comedic"}'

# Test AI Player
curl -X POST http://localhost:8003/play \
  -H "Content-Type: application/json" \
  -d '{"blackCard":"Test","availableCards":["Card1","Card2"],"personality":"absurd"}'
```

## Mock Mode

By default, agents run in mock mode (without API keys). This is useful for:
- Development and testing
- Demo purposes
- Cost savings during development

To enable real AI features:
1. Add `VEO3_API_KEY` for video generation
2. Add `GEMINI_API_KEY` for AI player intelligence

## Troubleshooting

**Agent won't start:**
- Check port availability
- Verify environment variables
- Check Python version (3.11+ required)

**API calls failing:**
- Verify API keys are correct
- Check network connectivity
- Review agent logs

**Videos not generating:**
- Ensure Veo3 API key is valid
- Check API quota/limits
- Verify prompt format

## Architecture Diagram

```
Backend (FastAPI)
    ↓
Coordinator Agent (8001)
    ├─→ Video Generation Agent (8002)
    │       ↓
    │   Veo3 API
    │
    └─→ AI Player Agent (8003)
            ↓
        Gemini API
```

## Future Enhancements

- [ ] Implement video caching in agents
- [ ] Add learning from winning patterns
- [ ] Support multiple AI personalities
- [ ] Implement rate limiting
- [ ] Add video quality options
- [ ] Support custom prompts
- [ ] Add analytics and metrics

---

**Built for Fetch.ai Hackathon 2025**
