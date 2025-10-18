# 📊 Visual Diagrams - Absurdly Visual

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                       │
│                         🌐 FRONTEND LAYER                            │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Lobby      │  │  Game Room   │  │ Video Player │              │
│  │  Component   │  │  Component   │  │  Component   │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                  │                  │                       │
│         └──────────────────┴──────────────────┘                      │
│                            │                                          │
│                   ┌────────▼────────┐                                │
│                   │  Socket.io      │                                │
│                   │  Client         │                                │
│                   └────────┬────────┘                                │
│                            │                                          │
└────────────────────────────┼──────────────────────────────────────────┘
                             │ WebSocket + REST
                             │
┌────────────────────────────▼──────────────────────────────────────────┐
│                                                                        │
│                         ⚙️  BACKEND LAYER                             │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    FastAPI Server                             │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐             │   │
│  │  │   Game     │  │   Card     │  │   Video    │             │   │
│  │  │  Service   │  │  Service   │  │   Cache    │             │   │
│  │  └────────────┘  └────────────┘  └────────────┘             │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              Python Socket.io Server                          │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐             │   │
│  │  │   Event    │  │  Player    │  │   Round    │             │   │
│  │  │  Handlers  │  │  Manager   │  │  Manager   │             │   │
│  │  └────────────┘  └────────────┘  └────────────┘             │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                        │
│  ┌──────────────┐              ┌──────────────┐                     │
│  │   MongoDB    │              │    Redis     │                     │
│  │  (Game Data) │              │   (Cache)    │                     │
│  └──────────────┘              └──────────────┘                     │
│                                                                        │
└────────────────────────────┬───────────────────────────────────────────┘
                             │ REST API
                             │
┌────────────────────────────▼───────────────────────────────────────────┐
│                                                                         │
│                      🤖 FETCH.AI AGENT LAYER                           │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │                  Coordinator Agent (8001)                     │    │
│  │                    Orchestration Logic                        │    │
│  └────────────────┬─────────────────────────┬───────────────────┘    │
│                   │                          │                         │
│         ┌─────────▼─────────┐    ┌──────────▼──────────┐             │
│         │  Video Generation │    │   AI Player Agent   │             │
│         │   Agent (8002)    │    │      (8003)         │             │
│         │                   │    │                     │             │
│         │  ┌─────────────┐ │    │  ┌──────────────┐  │             │
│         │  │   Prompt    │ │    │  │   Gemini     │  │             │
│         │  │  Generator  │ │    │  │  Integration │  │             │
│         │  └─────────────┘ │    │  └──────────────┘  │             │
│         └─────────┬─────────┘    └──────────┬──────────┘             │
│                   │                          │                         │
└───────────────────┼──────────────────────────┼─────────────────────────┘
                    │                          │
          ┌─────────▼─────────┐    ┌──────────▼──────────┐
          │   Veo3 API        │    │   Gemini API        │
          │ (Video Generation)│    │  (AI Intelligence)  │
          └───────────────────┘    └─────────────────────┘
```

---

## Game Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         GAME FLOW                                │
└─────────────────────────────────────────────────────────────────┘

    START
      │
      ▼
┌──────────────┐
│ Create Game  │◄─── Player enters name
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Add Players │◄─── Friends join OR AI bots added
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Start Game   │◄─── Min 3 players required
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Deal Cards   │─── Each player gets 10 white cards
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Select Czar  │─── Rotates each round
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Draw Black   │─── Question/prompt card
│    Card      │
└──────┬───────┘
       │
       ├─────────────────────────────────────┐
       │                                     │
       ▼                                     ▼
┌──────────────┐                    ┌──────────────┐
│ Human Players│                    │  AI Players  │
│ Select Cards │                    │ Select Cards │
│   (via UI)   │                    │ (via Gemini) │
└──────┬───────┘                    └──────┬───────┘
       │                                     │
       └─────────────────┬───────────────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ All Cards    │
                  │  Submitted   │
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ Czar Judges  │─── Selects funniest
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ Check Cache  │
                  └──────┬───────┘
                         │
                    ┌────┴────┐
                    │         │
                 Found    Not Found
                    │         │
                    │         ▼
                    │    ┌──────────────┐
                    │    │  Generate    │
                    │    │   Video      │
                    │    │ (Veo3 API)   │
                    │    └──────┬───────┘
                    │           │
                    │           ▼
                    │    ┌──────────────┐
                    │    │ Cache Video  │
                    │    └──────┬───────┘
                    │           │
                    └───────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ Play Video   │
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ Update Score │
                  └──────┬───────┘
                         │
                    ┌────┴────┐
                    │         │
              Game Won    Continue
                    │         │
                    ▼         │
              ┌──────────┐   │
              │   END    │   │
              └──────────┘   │
                             │
                             └──► Next Round (Rotate Czar)
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      PLAYER SUBMISSION FLOW                      │
└─────────────────────────────────────────────────────────────────┘

Player Browser                Backend                  Fetch.ai Agents
      │                          │                            │
      │  1. Submit Cards         │                            │
      ├─────────────────────────►│                            │
      │  {card_ids: [...]}       │                            │
      │                          │                            │
      │                          │  2. Validate Cards         │
      │                          │     & Update State         │
      │                          │                            │
      │  3. Confirmation         │                            │
      │◄─────────────────────────┤                            │
      │  {status: "submitted"}   │                            │
      │                          │                            │
      │                          │  4. Check if all           │
      │                          │     players submitted      │
      │                          │                            │
      │  5. Broadcast Update     │                            │
      │◄─────────────────────────┤                            │
      │  {submissions_count: N}  │                            │
      │                          │                            │
      │                          │  6. If AI player turn      │
      │                          ├───────────────────────────►│
      │                          │  POST /coordinate          │
      │                          │  {action: "ai_play"}       │
      │                          │                            │
      │                          │                            │  7. Gemini
      │                          │                            │     Analysis
      │                          │                            │
      │                          │  8. AI Selection           │
      │                          │◄───────────────────────────┤
      │                          │  {selectedCardId: "..."}   │
      │                          │                            │
      │  9. All Submitted        │                            │
      │◄─────────────────────────┤                            │
      │  {state: "judging"}      │                            │
      │                          │                            │
```

---

## Video Generation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    VIDEO GENERATION FLOW                         │
└─────────────────────────────────────────────────────────────────┘

Czar Selects Winner
      │
      ▼
┌──────────────────┐
│ Backend Receives │
│ Winner Selection │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Check Video     │
│     Cache        │
└────────┬─────────┘
         │
    ┌────┴────┐
    │         │
  Found   Not Found
    │         │
    │         ▼
    │   ┌──────────────────┐
    │   │ Call Coordinator │
    │   │     Agent        │
    │   └────────┬─────────┘
    │            │
    │            ▼
    │   ┌──────────────────┐
    │   │ Coordinator      │
    │   │ Routes to Video  │
    │   │     Agent        │
    │   └────────┬─────────┘
    │            │
    │            ▼
    │   ┌──────────────────┐
    │   │ Video Agent      │
    │   │ Creates Prompt   │
    │   └────────┬─────────┘
    │            │
    │            ▼
    │   ┌──────────────────┐
    │   │ Call Veo3 API    │
    │   │ Generate Video   │
    │   └────────┬─────────┘
    │            │
    │            ▼
    │   ┌──────────────────┐
    │   │ Return Video URL │
    │   └────────┬─────────┘
    │            │
    │            ▼
    │   ┌──────────────────┐
    │   │  Cache Video     │
    │   │  (Permanent)     │
    │   └────────┬─────────┘
    │            │
    └────────────┘
         │
         ▼
┌──────────────────┐
│ Broadcast Video  │
│  to All Players  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Video Player    │
│  Auto-plays      │
└──────────────────┘
```

---

## Component Hierarchy

```
App.tsx
│
├─── Lobby.tsx
│    ├─── Create Game Form
│    └─── Join Game Form
│
└─── GameRoom.tsx
     │
     ├─── PlayerList.tsx
     │    └─── Player Cards (x N)
     │         ├─── Player Name
     │         ├─── Score
     │         ├─── AI Badge
     │         └─── Czar Crown
     │
     ├─── BlackCard.tsx
     │    ├─── Card Text
     │    └─── Pick Count
     │
     ├─── Submissions Area
     │    └─── WhiteCard.tsx (x N)
     │         ├─── Card Text
     │         └─── NSFW Badge
     │
     ├─── CardHand.tsx
     │    └─── WhiteCard.tsx (x 10)
     │         ├─── Selectable
     │         └─── Submit Button
     │
     └─── VideoPlayer.tsx
          ├─── Video Element
          ├─── Loading State
          └─── Mock Fallback
```

---

## Database Schema

```
┌─────────────────────────────────────────────────────────────────┐
│                         MONGODB SCHEMA                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Games Collection                                                 │
├─────────────────────────────────────────────────────────────────┤
│ {                                                                │
│   _id: ObjectId,                                                 │
│   id: "uuid",                                                    │
│   state: "lobby|playing|judging|round_end|game_end",           │
│   players: ["player_id_1", "player_id_2", ...],                │
│   current_round: {                                               │
│     round_number: 1,                                             │
│     black_card_id: "b001",                                       │
│     czar_id: "player_id_1",                                      │
│     submissions: [...],                                          │
│     winner_id: "player_id_2",                                    │
│     video_url: "https://..."                                     │
│   },                                                             │
│   round_history: [...],                                          │
│   black_deck: ["b001", "b002", ...],                            │
│   white_deck: ["w001", "w002", ...],                            │
│   created_at: ISODate,                                           │
│   updated_at: ISODate                                            │
│ }                                                                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Players Collection                                               │
├─────────────────────────────────────────────────────────────────┤
│ {                                                                │
│   _id: ObjectId,                                                 │
│   id: "uuid",                                                    │
│   name: "Player Name",                                           │
│   type: "human|ai",                                              │
│   score: 0,                                                      │
│   hand: ["w001", "w002", ...],                                  │
│   is_connected: true,                                            │
│   socket_id: "socket_id"                                         │
│ }                                                                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Redis Cache                                                      │
├─────────────────────────────────────────────────────────────────┤
│ Key: sha256(black_card + white_cards)                           │
│ Value: {                                                         │
│   video_url: "https://...",                                      │
│   created_at: timestamp,                                         │
│   expires_at: timestamp,                                         │
│   permanent: boolean                                             │
│ }                                                                │
│ TTL: 24 hours (temporary) or ∞ (permanent)                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      PRODUCTION DEPLOYMENT                       │
└─────────────────────────────────────────────────────────────────┘

                        ┌──────────────┐
                        │   Internet   │
                        └──────┬───────┘
                               │
                               ▼
                        ┌──────────────┐
                        │     CDN      │
                        │  (Frontend)  │
                        └──────┬───────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │  Load Balancer   │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        ┌─────────┐    ┌─────────┐    ┌─────────┐
        │Backend  │    │Backend  │    │Backend  │
        │Instance1│    │Instance2│    │Instance3│
        └────┬────┘    └────┬────┘    └────┬────┘
             │              │              │
             └──────────────┼──────────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
        ┌─────────┐   ┌─────────┐   ┌─────────┐
        │MongoDB  │   │  Redis  │   │Fetch.ai │
        │ Atlas   │   │  Cloud  │   │Agentverse│
        └─────────┘   └─────────┘   └─────────┘
```

---

## WebSocket Event Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    WEBSOCKET EVENTS                              │
└─────────────────────────────────────────────────────────────────┘

Client                                              Server
  │                                                    │
  │  connect                                           │
  ├───────────────────────────────────────────────────►│
  │                                                    │
  │                                     connected      │
  │◄───────────────────────────────────────────────────┤
  │  {sid: "..."}                                      │
  │                                                    │
  │  create_game                                       │
  ├───────────────────────────────────────────────────►│
  │  {player_name: "..."}                              │
  │                                                    │
  │                                  game_created      │
  │◄───────────────────────────────────────────────────┤
  │  {game_id, player_id, game_state}                  │
  │                                                    │
  │  join_game                                         │
  ├───────────────────────────────────────────────────►│
  │  {game_id, player_name}                            │
  │                                                    │
  │                                  player_joined     │
  │◄───────────────────────────────────────────────────┤
  │  {player: {...}}                                   │
  │                                                    │
  │  start_game                                        │
  ├───────────────────────────────────────────────────►│
  │  {game_id}                                         │
  │                                                    │
  │                                  round_started     │
  │◄───────────────────────────────────────────────────┤
  │  {round_number: 1}                                 │
  │                                                    │
  │  submit_cards                                      │
  ├───────────────────────────────────────────────────►│
  │  {game_id, player_id, card_ids}                    │
  │                                                    │
  │                                cards_submitted     │
  │◄───────────────────────────────────────────────────┤
  │  {player_id, count}                                │
  │                                                    │
  │  select_winner                                     │
  ├───────────────────────────────────────────────────►│
  │  {game_id, player_id, winning_submission}          │
  │                                                    │
  │                                winner_selected     │
  │◄───────────────────────────────────────────────────┤
  │  {winner_id, cards, video_url}                     │
  │                                                    │
  │                                  video_ready       │
  │◄───────────────────────────────────────────────────┤
  │  {video_url}                                       │
  │                                                    │
```

---

These diagrams provide a comprehensive visual understanding of the Absurdly Visual architecture!
