# 🏗️ Architecture Documentation - Absurdly Visual

## System Overview

Absurdly Visual is a distributed, real-time multiplayer game that combines traditional card game mechanics with AI-powered video generation. The system is built on a microservices architecture with Fetch.ai agents handling AI operations.

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│              React + TypeScript + Socket.io                  │
│                    (Port 3000)                               │
└────────────────────┬────────────────────────────────────────┘
                     │ WebSocket + REST
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                         Backend                              │
│           FastAPI + Python Socket.io + Redis                 │
│                    (Port 8000)                               │
└────────────────────┬────────────────────────────────────────┘
                     │ REST API
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Fetch.ai Coordinator                      │
│                    (Port 8001)                               │
└───────────┬────────────────────────────────┬────────────────┘
            │                                │
            ▼                                ▼
┌───────────────────────┐      ┌───────────────────────────┐
│   Video Gen Agent     │      │    AI Player Agent        │
│   (Port 8002)         │      │    (Port 8003)            │
│   ↓                   │      │    ↓                      │
│   Veo3 API            │      │    Gemini API             │
└───────────────────────┘      └───────────────────────────┘
```

---

## Component Architecture

### 1. Frontend Layer

**Technology:** React 18 + TypeScript + Tailwind CSS

**Responsibilities:**
- User interface rendering
- Real-time game state management
- WebSocket communication
- Video playback

**Key Components:**
```
src/
├── components/
│   ├── Lobby.tsx           # Game creation/joining
│   ├── GameRoom.tsx        # Main game interface
│   ├── BlackCard.tsx       # Question card display
│   ├── WhiteCard.tsx       # Answer card display
│   ├── CardHand.tsx        # Player's card hand
│   ├── PlayerList.tsx      # Player roster
│   └── VideoPlayer.tsx     # Video playback
├── hooks/
│   ├── useSocket.ts        # WebSocket management
│   └── useGame.ts          # Game state logic
├── services/
│   ├── socketService.ts    # Socket.io client
│   └── apiService.ts       # REST API client
└── types/
    └── game.types.ts       # TypeScript definitions
```

**State Management:**
- React hooks for local state
- Socket.io for real-time updates
- No Redux (keeps it simple)

---

### 2. Backend Layer

**Technology:** FastAPI + Python Socket.io + Motor (MongoDB) + Redis

**Responsibilities:**
- Game logic orchestration
- Player management
- Card deck management
- WebSocket event handling
- API endpoints
- Video caching

**Architecture:**
```
app/
├── main.py                 # FastAPI + Socket.io server
├── config.py               # Configuration management
├── models/
│   ├── game.py             # Game state models
│   ├── player.py           # Player models
│   └── card.py             # Card models
├── services/
│   ├── game_service.py     # Game logic
│   ├── card_service.py     # Card management
│   ├── fetch_client.py     # Fetch.ai client
│   └── video_cache.py      # Video caching
├── websocket/
│   └── events.py           # Socket event handlers
└── api/
    └── routes.py           # REST API routes
```

**Key Design Patterns:**
- **Singleton Services:** Game and card services
- **Event-Driven:** Socket.io for real-time updates
- **Async/Await:** Non-blocking I/O operations
- **Dependency Injection:** FastAPI's DI system

---

### 3. Fetch.ai Agent Layer

**Technology:** uAgents + FastAPI (for REST endpoints)

#### 3.1 Coordinator Agent (Port 8001)

**Purpose:** Orchestrate requests between backend and specialized agents

**Responsibilities:**
- Route video generation requests
- Route AI player requests
- Aggregate responses
- Load balancing (future)

**Communication:**
```python
Backend → POST /coordinate
    ↓
Coordinator analyzes request
    ↓
Routes to Video Agent or AI Player Agent
    ↓
Returns aggregated response
```

#### 3.2 Video Generation Agent (Port 8002)

**Purpose:** Generate videos from card combinations

**Responsibilities:**
- Create creative prompts from cards
- Call Veo3 API
- Monitor generation status
- Return video URLs

**Prompt Engineering:**
```python
def create_video_prompt(black_card, white_cards, style):
    # Combine cards into scenario
    scenario = format_cards(black_card, white_cards)
    
    # Apply style-specific prompt
    if style == "comedic":
        return f"Create a humorous scene: {scenario}"
    elif style == "cinematic":
        return f"Create an epic scene: {scenario}"
    # ...
```

#### 3.3 AI Player Agent (Port 8003)

**Purpose:** Select cards using AI

**Responsibilities:**
- Analyze black card context
- Evaluate available white cards
- Use Gemini for humor analysis
- Return card selection with reasoning

**AI Personalities:**
- **Savage:** Dark humor, shocking combinations
- **Wholesome:** Family-friendly, clever wordplay
- **Absurd:** Random, nonsensical combinations
- **Strategic:** Analyzes past wins

---

## Data Flow

### Game Creation Flow

```
1. User clicks "Create Game"
   ↓
2. Frontend → emit('create_game', {player_name})
   ↓
3. Backend creates Game + Player
   ↓
4. Backend → emit('game_created', {game_id, player_id, game_state})
   ↓
5. Frontend stores game_id and displays lobby
```

### Round Flow

```
1. Czar selected (rotating)
   ↓
2. Black card drawn
   ↓
3. Players submit white cards
   │
   ├─→ Human players: UI selection
   │
   └─→ AI players: Fetch.ai AI Player Agent
       ↓
       Gemini analyzes cards
       ↓
       Returns selection
   ↓
4. All submissions collected
   ↓
5. Czar judges submissions
   ↓
6. Winner selected
   ↓
7. Video generation triggered
   │
   ├─→ Check cache first
   │
   └─→ If not cached:
       Backend → Coordinator Agent
       ↓
       Coordinator → Video Agent
       ↓
       Video Agent → Veo3 API
       ↓
       Video URL returned
       ↓
       Cached for future use
   ↓
8. Video displayed to all players
   ↓
9. Scores updated
   ↓
10. Next round starts
```

---

## Database Schema

### MongoDB Collections

#### Games Collection
```javascript
{
  _id: ObjectId,
  id: "uuid",
  state: "lobby|playing|judging|round_end|game_end",
  players: ["player_id_1", "player_id_2"],
  current_round: {
    round_number: 1,
    black_card_id: "b001",
    czar_id: "player_id_1",
    submissions: [{
      player_id: "player_id_2",
      card_ids: ["w001", "w002"]
    }],
    winner_id: "player_id_2",
    video_url: "https://..."
  },
  round_history: [...],
  black_deck: ["b001", "b002", ...],
  white_deck: ["w001", "w002", ...],
  created_at: ISODate,
  updated_at: ISODate
}
```

#### Players Collection
```javascript
{
  _id: ObjectId,
  id: "uuid",
  name: "Player Name",
  type: "human|ai",
  score: 0,
  hand: ["w001", "w002", ...],
  is_connected: true,
  socket_id: "socket_id"
}
```

### Redis Cache

**Video Cache:**
```
Key: sha256(black_card + white_cards)
Value: {
  video_url: "https://...",
  created_at: timestamp,
  expires_at: timestamp,
  permanent: boolean
}
TTL: 24 hours (temporary), ∞ (permanent)
```

---

## WebSocket Events

### Client → Server

| Event | Payload | Description |
|-------|---------|-------------|
| `create_game` | `{player_name, settings}` | Create new game |
| `join_game` | `{game_id, player_name}` | Join existing game |
| `start_game` | `{game_id}` | Start the game |
| `submit_cards` | `{game_id, player_id, card_ids[]}` | Submit cards |
| `select_winner` | `{game_id, player_id, winning_submission}` | Czar selects winner |
| `request_ai_join` | `{game_id, personality}` | Add AI bot |
| `send_message` | `{game_id, player_id, message}` | Chat message |

### Server → Client

| Event | Payload | Description |
|-------|---------|-------------|
| `game_created` | `{game_id, player_id, game_state}` | Game created successfully |
| `game_state` | `{GameStateData}` | Full game state update |
| `player_joined` | `{player}` | New player joined |
| `player_left` | `{player_id, player_name}` | Player disconnected |
| `round_started` | `{round_number}` | New round started |
| `cards_submitted` | `{player_id, count}` | Player submitted cards |
| `judging_phase` | `{}` | All cards submitted |
| `winner_selected` | `{winner_id, cards, video_url}` | Round winner |
| `video_ready` | `{video_url}` | Video generated |
| `error` | `{message}` | Error occurred |

---

## API Endpoints

### REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/cards/black` | Get all black cards |
| GET | `/api/cards/white` | Get all white cards |
| GET | `/api/game/:id` | Get game info |
| GET | `/api/game/:id/state/:player_id` | Get game state for player |
| GET | `/api/games` | List all games |
| GET | `/api/stats` | Get statistics |
| GET | `/api/videos/cache/stats` | Video cache stats |

### Agent APIs

**Coordinator (8001):**
- POST `/coordinate` - Coordinate action
- GET `/health` - Health check

**Video Agent (8002):**
- POST `/generate` - Generate video
- GET `/status/:id` - Check generation status
- GET `/health` - Health check

**AI Player (8003):**
- POST `/play` - Select card
- GET `/health` - Health check

---

## Security Considerations

### Authentication
- Socket.io session management
- Player ID validation
- Game room isolation

### Input Validation
- Pydantic models for all inputs
- Card ID validation
- Player action authorization

### Rate Limiting
- Video generation rate limits
- API request throttling
- WebSocket connection limits

### Content Moderation
- Censorship levels (none, mild, family)
- NSFW card filtering
- Video prompt sanitization

---

## Performance Optimization

### Caching Strategy

**Video Cache:**
- Winning combinations cached permanently
- Popular combinations pre-generated
- 24-hour TTL for temporary cache
- Redis for distributed caching

**Card Data:**
- Loaded once at startup
- In-memory storage
- No database queries during gameplay

### WebSocket Optimization
- Binary protocol for large payloads
- Event batching
- Compression enabled
- Reconnection handling

### Database Optimization
- Indexed queries
- Minimal writes during gameplay
- Batch updates
- Connection pooling

---

## Scalability

### Horizontal Scaling

**Frontend:**
- Static files served via CDN
- Multiple instances behind load balancer

**Backend:**
- Stateless design
- Redis for shared state
- Multiple instances possible
- Sticky sessions for WebSocket

**Agents:**
- Independent scaling
- Load balancing via Coordinator
- Async processing
- Queue-based video generation

### Vertical Scaling

**Database:**
- MongoDB sharding
- Read replicas
- Index optimization

**Cache:**
- Redis cluster
- Memory optimization
- Eviction policies

---

## Monitoring & Logging

### Metrics to Track
- Active games count
- Connected players
- Video generation time
- API response times
- WebSocket latency
- Cache hit rate

### Logging Strategy
- Structured logging (JSON)
- Log levels (DEBUG, INFO, WARNING, ERROR)
- Centralized log aggregation
- Error tracking (Sentry)

---

## Deployment Architecture

### Development
```
Local machine
├── Backend (localhost:8000)
├── Frontend (localhost:3000)
└── Agents (localhost:8001-8003)
```

### Production
```
Cloud Provider (AWS/GCP/Azure)
├── Frontend (CDN + S3/Cloud Storage)
├── Backend (ECS/Cloud Run)
│   ├── Load Balancer
│   └── Multiple instances
├── Database (MongoDB Atlas)
├── Cache (Redis Cloud)
└── Agents (Fetch.ai Agentverse)
```

---

## Future Enhancements

### Phase 2
- [ ] Persistent user accounts
- [ ] Game history and replays
- [ ] Custom card packs
- [ ] Tournament mode
- [ ] Leaderboards

### Phase 3
- [ ] Voice chat integration
- [ ] Mobile app (React Native)
- [ ] Spectator mode
- [ ] Twitch integration
- [ ] NFT card packs

### Phase 4
- [ ] Machine learning for card recommendations
- [ ] Video style customization
- [ ] Multi-language support
- [ ] Accessibility features
- [ ] Advanced analytics

---

## Technology Choices Rationale

### Why FastAPI?
- Native async/await support
- Automatic API documentation
- Type hints and validation
- High performance
- WebSocket support

### Why React?
- Component reusability
- Large ecosystem
- TypeScript support
- Excellent developer experience
- Virtual DOM performance

### Why Fetch.ai?
- Distributed agent architecture
- Built-in agent discovery
- Blockchain integration ready
- Perfect for hackathon innovation

### Why Socket.io?
- Reliable WebSocket fallback
- Room-based messaging
- Automatic reconnection
- Wide browser support
- Easy to use

---

**Architecture designed for scalability, maintainability, and innovation! 🚀**
