# 💾 Database Usage - Absurdly Visual

## Overview

The application supports both **JSON file storage** (default) and **MongoDB** (optional) for cards, with **Redis** configured but currently unused.

---

## 📊 Current Setup

### Cards Storage

**Default: JSON File** ✅ (Currently Active)
- Location: `backend/data/cards.json`
- **121 black cards** (questions)
- **172 white cards** (answers)
- **293 total cards** from internetcards (PG & PG-13 only)
- Loaded at startup into memory
- Fast access, no database needed

**Optional: MongoDB** (Ready to use)
- Collections: `black_cards`, `white_cards`
- Indexed by: `id`, `pack`, `nsfw`
- Async loading supported
- Better for large card sets

### Game State Storage

**Current: In-Memory** ✅
- Games stored in `game_service.games` dictionary
- Players stored in `game_service.players` dictionary
- Fast, but not persistent across restarts

**Future: MongoDB**
- Can persist games and players
- Survives server restarts
- Better for production

### Video Cache

**Current: Redis with In-Memory Fallback** ✅
- Implemented in `video_cache.py`
- **Primary:** Redis for distributed caching
- **Fallback:** In-memory if Redis unavailable
- Stores video URLs with TTL
- Permanent cache for winners (no expiration)
- 24-hour TTL for temporary cache
- Auto-detects Redis availability

---

## 🚀 Using MongoDB for Cards

### 1. Import Cards to MongoDB

```bash
cd backend

# Make sure MongoDB is running
# Default: mongodb://localhost:27017

# Import cards
python3 import_cards_to_mongo.py
```

This will:
- ✅ Connect to MongoDB
- ✅ Clear existing cards
- ✅ Import 121 black cards
- ✅ Import 172 white cards
- ✅ Create indexes for performance
- ✅ Show pack distribution

### 2. Enable MongoDB in Code

The `CardService` now supports MongoDB loading:

```python
# In card_service.py
card_service = CardService(use_mongodb=True)

# Then in your startup code:
await card_service.load_cards_from_mongodb(db)
```

### 3. MongoDB Collections Structure

**black_cards collection:**
```json
{
  "id": "b001",
  "text": "This quarantine really got me horny for _.",
  "type": "black",
  "pick": 1,
  "pack": "pg13"
}
```

**white_cards collection:**
```json
{
  "id": "w001",
  "text": "My crippling loneliness",
  "type": "white",
  "nsfw": false,
  "pack": "pg13"
}
```

### 4. Indexes Created

```javascript
// black_cards
db.black_cards.createIndex({ "id": 1 }, { unique: true })
db.black_cards.createIndex({ "pack": 1 })

// white_cards
db.white_cards.createIndex({ "id": 1 }, { unique: true })
db.white_cards.createIndex({ "pack": 1 })
db.white_cards.createIndex({ "nsfw": 1 })
```

---

## 🔴 Redis Usage

### Current Status: **ACTIVELY USED** ✅

Redis is now the primary caching mechanism with automatic fallback!

**Implementation:**
- `video_cache.py` - Redis-based video caching
- Auto-connects on startup
- Falls back to in-memory if Redis unavailable
- Graceful degradation

**Features:**
- ✅ Permanent cache (no expiration) for winners
- ✅ 24-hour TTL for temporary cache
- ✅ Distributed caching across multiple servers
- ✅ Automatic fallback to in-memory
- ✅ Connection pooling and error handling

### How It Works

**1. Video Caching** (Active)
```python
# Automatic Redis usage in video_cache.py
from app.services.video_cache import video_cache

# Set video (uses Redis if available)
video_cache.set(black_card, white_cards, video_url, permanent=True)

# Get video (checks Redis first)
cached_url = video_cache.get(black_card, white_cards)
```

**2. Session Management** (Future)
```python
# Store WebSocket sessions
redis_client.hset(f"session:{sid}", mapping={
    "player_id": player_id,
    "game_id": game_id,
    "connected_at": timestamp
})
```

**3. Game State Caching** (Future)
```python
# Cache frequently accessed game states
redis_client.setex(
    f"game:{game_id}",
    300,  # 5 minutes
    json.dumps(game_state)
)
```

### Benefits of Redis Implementation

1. **Distributed caching** - Works across multiple server instances
2. **Persistent caching** - Survives server restarts
3. **TTL support** - Automatic expiration for temporary cache
4. **Graceful fallback** - Works without Redis for development
5. **Production-ready** - Scales horizontally

### Redis Connection Behavior

**On Startup:**
```
✅ Connected to Redis for video caching
```

**If Redis Unavailable:**
```
⚠️  Redis connection failed: [error]
⚠️  Falling back to in-memory cache
```

**The application works in both cases!**

---

## 📈 Performance Comparison

### Cards Loading

| Method | Startup Time | Memory | Persistence | Best For |
|--------|--------------|--------|-------------|----------|
| **JSON** | ~10ms | Low | No | Development, Demo |
| **MongoDB** | ~100ms | Low | Yes | Production |

### Video Caching

| Method | Access Time | Distributed | Persistence | Best For |
|--------|-------------|-------------|-------------|----------|
| **In-Memory** | < 1ms | No | No | Single server |
| **Redis** | ~2ms | Yes | Yes | Multi-server |

### Game State

| Method | Access Time | Persistence | Scalability | Best For |
|--------|-------------|-------------|-------------|----------|
| **In-Memory** | < 1ms | No | Limited | Demo |
| **MongoDB** | ~10ms | Yes | High | Production |

---

## 🔧 Configuration

### Environment Variables

```bash
# MongoDB (Optional)
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=absurdly_visual

# Redis (Configured but not used)
REDIS_URL=redis://localhost:6379
REDIS_DB=0
```

### Docker Compose

```yaml
# MongoDB service (optional)
mongo:
  image: mongo:7
  ports:
    - "27017:27017"

# Redis service (configured but not used)
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
```

---

## 🎯 Recommendations

### For Hackathon Demo
✅ **Use JSON files** (current setup)
- Fast startup
- No database setup needed
- Easy to demo
- Works offline

### For Production
✅ **Use MongoDB + Redis**
- MongoDB for cards and game state
- Redis for video caching and sessions
- Better scalability
- Persistent data

---

## 📝 Summary

**Current State:**
- ✅ Cards: JSON file (293 cards from internetcards)
- ✅ Game State: In-memory
- ✅ Video Cache: **Redis with in-memory fallback** 🔴
- ⚙️ MongoDB: Configured, ready to use
- ✅ Redis: **Actively used for video caching** 🔴

**To Enable MongoDB:**
```bash
python3 import_cards_to_mongo.py
```

**Redis is Already Enabled!**
- ✅ Just start Redis and it will be used automatically
- ✅ If Redis is unavailable, falls back to in-memory
- ✅ No code changes needed

**To Start Redis:**
```bash
# Option 1: Docker Compose (includes Redis)
docker-compose up

# Option 2: Standalone Redis
redis-server

# Option 3: Docker only Redis
docker run -d -p 6379:6379 redis:7-alpine
```

---

**Redis is now production-ready! Start Redis to enable distributed caching, or run without it for local development! 🚀**
