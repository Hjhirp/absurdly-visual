# 🧪 Testing Guide - Absurdly Visual

## Quick Test

```bash
# Start everything
./start.sh

# In browser, go to http://localhost:3000
# Create game, add 2 AI bots, start playing!
```

---

## Manual Testing Checklist

### ✅ Frontend Tests

#### Lobby
- [ ] Landing page loads correctly
- [ ] Can enter player name
- [ ] "Create Game" button works
- [ ] "Join Game" button works
- [ ] Game ID validation
- [ ] Responsive design (mobile/tablet/desktop)

#### Game Room
- [ ] Game room loads with correct state
- [ ] Player list displays correctly
- [ ] AI bot indicator shows
- [ ] Card Czar crown displays
- [ ] Score updates in real-time
- [ ] "Add AI Bot" button works
- [ ] "Start Game" button enables at 3+ players

#### Gameplay
- [ ] Black card displays correctly
- [ ] White cards in hand display
- [ ] Can select cards
- [ ] Selected cards highlight
- [ ] Submit button enables when correct number selected
- [ ] Submission confirmation shows
- [ ] Waiting state displays
- [ ] Judging phase shows all submissions
- [ ] Can select winner as Czar
- [ ] Video player shows
- [ ] Winner announcement displays
- [ ] Scores update correctly
- [ ] Next round starts automatically

#### Edge Cases
- [ ] Handles disconnection gracefully
- [ ] Reconnection works
- [ ] Multiple tabs/windows sync
- [ ] Long player names don't break UI
- [ ] Long card text wraps correctly
- [ ] Empty states display properly

---

### ✅ Backend Tests

#### API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get black cards
curl http://localhost:8000/api/cards/black

# Get white cards
curl http://localhost:8000/api/cards/white

# List games
curl http://localhost:8000/api/games

# Get stats
curl http://localhost:8000/api/stats

# Cache stats
curl http://localhost:8000/api/videos/cache/stats
```

#### WebSocket Events

Use browser console:

```javascript
// Connect to WebSocket
const socket = io('http://localhost:8000');

// Create game
socket.emit('create_game', {
  player_name: 'Test Player'
});

// Listen for response
socket.on('game_created', (data) => {
  console.log('Game created:', data);
});

// Join game
socket.emit('join_game', {
  game_id: 'game-id-here',
  player_name: 'Player 2'
});

// Request AI bot
socket.emit('request_ai_join', {
  game_id: 'game-id-here',
  personality: 'absurd'
});
```

#### Game Logic

- [ ] Game creation works
- [ ] Player can join game
- [ ] AI bot can be added
- [ ] Game starts with 3+ players
- [ ] Cards are dealt correctly
- [ ] Czar rotates properly
- [ ] Submissions are collected
- [ ] Winner selection works
- [ ] Scores are calculated correctly
- [ ] Round advances automatically
- [ ] Game ends at target score

---

### ✅ Agent Tests

#### Coordinator Agent

```bash
# Health check
curl http://localhost:8001/health

# Test video generation coordination
curl -X POST http://localhost:8001/coordinate \
  -H "Content-Type: application/json" \
  -d '{
    "action": "generate_video",
    "data": {
      "blackCard": "What is love?",
      "whiteCards": ["Baby dont hurt me"],
      "style": "comedic"
    }
  }'

# Test AI play coordination
curl -X POST http://localhost:8001/coordinate \
  -H "Content-Type: application/json" \
  -d '{
    "action": "ai_play",
    "data": {
      "blackCard": "What is love?",
      "availableCards": ["Card1", "Card2", "Card3"],
      "personality": "absurd"
    }
  }'
```

#### Video Generation Agent

```bash
# Health check
curl http://localhost:8002/health

# Generate video
curl -X POST http://localhost:8002/generate \
  -H "Content-Type: application/json" \
  -d '{
    "blackCard": "The secret to happiness is _.",
    "whiteCards": ["Cats with opposable thumbs"],
    "style": "comedic"
  }'

# Check status
curl http://localhost:8002/status/abc123
```

#### AI Player Agent

```bash
# Health check
curl http://localhost:8003/health

# AI card selection
curl -X POST http://localhost:8003/play \
  -H "Content-Type: application/json" \
  -d '{
    "blackCard": "What would grandma find disturbing?",
    "availableCards": [
      "A mime having a stroke",
      "Vigorous jazz hands",
      "Existential dread"
    ],
    "personality": "absurd"
  }'
```

---

## Load Testing

### Using Apache Bench

```bash
# Test API endpoint
ab -n 1000 -c 10 http://localhost:8000/health

# Test card endpoint
ab -n 500 -c 5 http://localhost:8000/api/cards/black
```

### Using Artillery

```bash
# Install artillery
npm install -g artillery

# Create test config (artillery.yml)
cat > artillery.yml << EOF
config:
  target: 'http://localhost:8000'
  phases:
    - duration: 60
      arrivalRate: 10
scenarios:
  - flow:
    - get:
        url: "/health"
    - get:
        url: "/api/cards/black"
EOF

# Run test
artillery run artillery.yml
```

### WebSocket Load Test

```javascript
// socket-load-test.js
const io = require('socket.io-client');

const NUM_CLIENTS = 100;
const clients = [];

for (let i = 0; i < NUM_CLIENTS; i++) {
  const socket = io('http://localhost:8000');
  
  socket.on('connect', () => {
    console.log(`Client ${i} connected`);
    
    socket.emit('create_game', {
      player_name: `Player ${i}`
    });
  });
  
  clients.push(socket);
}

// Cleanup after 60 seconds
setTimeout(() => {
  clients.forEach(s => s.disconnect());
  console.log('Test complete');
  process.exit(0);
}, 60000);
```

Run with: `node socket-load-test.js`

---

## Integration Tests

### Full Game Flow Test

```python
# test_game_flow.py
import socketio
import time

# Create clients
client1 = socketio.Client()
client2 = socketio.Client()

# Connect
client1.connect('http://localhost:8000')
client2.connect('http://localhost:8000')

# Create game
game_id = None
player1_id = None

@client1.on('game_created')
def on_game_created(data):
    global game_id, player1_id
    game_id = data['game_id']
    player1_id = data['player_id']
    print(f"Game created: {game_id}")

client1.emit('create_game', {'player_name': 'Player 1'})
time.sleep(1)

# Player 2 joins
client2.emit('join_game', {
    'game_id': game_id,
    'player_name': 'Player 2'
})
time.sleep(1)

# Add AI bot
client1.emit('request_ai_join', {
    'game_id': game_id,
    'personality': 'absurd'
})
time.sleep(1)

# Start game
client1.emit('start_game', {'game_id': game_id})
time.sleep(2)

print("Integration test passed!")

# Cleanup
client1.disconnect()
client2.disconnect()
```

---

## Performance Benchmarks

### Target Metrics

| Metric | Target | Acceptable |
|--------|--------|------------|
| API Response Time | < 50ms | < 100ms |
| WebSocket Latency | < 20ms | < 50ms |
| Video Generation | < 10s | < 30s |
| Page Load Time | < 2s | < 5s |
| Concurrent Games | 100+ | 50+ |
| Players per Game | 8 | 8 |

### Measuring Performance

```javascript
// Frontend performance
console.time('page-load');
// ... page loads ...
console.timeEnd('page-load');

// API performance
const start = Date.now();
fetch('http://localhost:8000/api/cards/black')
  .then(() => {
    console.log(`API took ${Date.now() - start}ms`);
  });

// WebSocket latency
const sent = Date.now();
socket.emit('ping');
socket.on('pong', () => {
  console.log(`Latency: ${Date.now() - sent}ms`);
});
```

---

## Automated Testing

### Backend Unit Tests

```python
# tests/test_game_service.py
import pytest
from app.services.game_service import game_service
from app.models.player import Player

def test_create_game():
    player = Player(name="Test Player")
    game = game_service.create_game(player.id)
    assert game is not None
    assert player.id in game.players

def test_add_player():
    player1 = Player(name="Player 1")
    game = game_service.create_game(player1.id)
    
    player2 = Player(name="Player 2")
    result = game_service.add_player(game.id, player2)
    
    assert result is True
    assert player2.id in game.players

def test_start_game():
    # Create game with 3 players
    player1 = Player(name="Player 1")
    game = game_service.create_game(player1.id)
    
    player2 = Player(name="Player 2")
    player3 = Player(name="Player 3")
    
    game_service.add_player(game.id, player2)
    game_service.add_player(game.id, player3)
    
    result = game_service.start_game(game.id)
    assert result is True
    assert game.state == "playing"

# Run with: pytest tests/
```

### Frontend Unit Tests

```typescript
// src/components/__tests__/WhiteCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { WhiteCard } from '../WhiteCard';

test('renders white card', () => {
  const card = {
    id: 'w001',
    text: 'Test Card',
    type: 'white' as const,
    pack: 'base',
    nsfw: false
  };
  
  render(<WhiteCard card={card} />);
  expect(screen.getByText('Test Card')).toBeInTheDocument();
});

test('handles click', () => {
  const handleClick = jest.fn();
  const card = {
    id: 'w001',
    text: 'Test Card',
    type: 'white' as const,
    pack: 'base',
    nsfw: false
  };
  
  render(<WhiteCard card={card} onClick={handleClick} />);
  fireEvent.click(screen.getByText('Test Card'));
  expect(handleClick).toHaveBeenCalled();
});

// Run with: npm test
```

---

## Browser Compatibility

### Tested Browsers

- [ ] Chrome 90+
- [ ] Firefox 88+
- [ ] Safari 14+
- [ ] Edge 90+
- [ ] Mobile Safari (iOS 14+)
- [ ] Chrome Mobile (Android 10+)

### Known Issues

- Safari: WebSocket reconnection may be slower
- Mobile: Video playback requires user interaction
- IE11: Not supported (use modern browsers)

---

## Debugging Tips

### Backend Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add breakpoints
import pdb; pdb.set_trace()

# Print game state
print(f"Game state: {game.dict()}")
```

### Frontend Debugging

```javascript
// Enable Socket.io debug
localStorage.debug = 'socket.io-client:*';

// Log all socket events
socket.onAny((event, ...args) => {
  console.log('Socket event:', event, args);
});

// React DevTools
// Install React DevTools browser extension
```

### Agent Debugging

```python
# Enable agent logging
ctx.logger.setLevel(logging.DEBUG)

# Log all messages
@agent.on_message()
async def log_all(ctx, sender, msg):
    ctx.logger.info(f"Received from {sender}: {msg}")
```

---

## Common Issues & Solutions

### Issue: WebSocket won't connect
**Solution:** Check CORS settings, verify backend is running, check firewall

### Issue: Cards not loading
**Solution:** Verify cards.json exists, check file permissions, restart backend

### Issue: Video not generating
**Solution:** Check agent is running, verify API keys, check logs

### Issue: AI bot not playing
**Solution:** Verify AI player agent is running, check Gemini API key

### Issue: Game state not syncing
**Solution:** Check WebSocket connection, verify room joining, check Redis

---

## Test Coverage Goals

- Backend: > 80%
- Frontend: > 70%
- Agents: > 60%
- Integration: Key flows covered

---

## CI/CD Testing

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: |
          cd backend
          pip install -r requirements.txt
          pytest tests/
  
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: |
          cd frontend
          npm install
          npm test
```

---

**Happy Testing! 🧪**
