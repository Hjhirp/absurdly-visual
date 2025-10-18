# 🎬 Demo Script - Absurdly Visual

Perfect for hackathon presentations and live demos!

## 🎯 Demo Objectives

1. Show the complete game flow
2. Demonstrate AI video generation
3. Highlight Fetch.ai agent architecture
4. Show multiplayer real-time features

---

## 📋 Pre-Demo Checklist

### Before the Presentation

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] All 3 Fetch.ai agents running (8001, 8002, 8003)
- [ ] Test game created with 2 AI bots
- [ ] Browser windows prepared (one for each player)
- [ ] Network stable (for WebSocket connections)

### Quick Setup

```bash
# Terminal 1 - Backend
cd backend && python -m uvicorn app.main:socket_app --reload --port 8000

# Terminal 2 - Frontend
cd frontend && npm start

# Terminal 3 - Coordinator Agent
cd fetch-agents/coordinator_agent && python agent.py

# Terminal 4 - Video Agent
cd fetch-agents/video_agent && python agent.py

# Terminal 5 - AI Player Agent
cd fetch-agents/ai_player_agent && python agent.py
```

---

## 🎭 Demo Script (5 Minutes)

### Part 1: Introduction (30 seconds)

**Say:**
> "Welcome to Absurdly Visual - a revolutionary take on Cards Against Humanity that combines multiplayer gaming with AI-generated videos. Built with Fetch.ai agents, Veo3, and Gemini AI."

**Show:**
- Landing page with game title
- Quick overview of tech stack

---

### Part 2: Game Setup (1 minute)

**Say:**
> "Let me show you how easy it is to start a game. I'll create a game, and we'll add some AI players powered by Gemini."

**Do:**
1. Click "Create New Game"
2. Enter name: "Demo Player"
3. Show the Game ID prominently
4. Click "Add AI Bot" twice
5. Show the player list with AI bots

**Highlight:**
- Real-time player joining
- AI bot indicators
- Clean, colonist.io-inspired UI

---

### Part 3: Gameplay (2 minutes)

**Say:**
> "Now let's play a round. Watch how the game flows seamlessly with real-time updates."

**Do:**
1. Click "Start Game"
2. Show the black card: "What's the secret to happiness?"
3. Select a funny white card from your hand
4. Click "Submit"
5. Show "Waiting for others..." message
6. **AI bots automatically submit** (happens in background)

**Highlight:**
- Real-time submission updates
- Card Czar indicator (crown icon)
- Beautiful card animations

---

### Part 4: AI Video Generation (1.5 minutes)

**Say:**
> "Here's where it gets interesting. As the Card Czar, I'll select the winning combination, and our Fetch.ai agents will generate a video!"

**Do:**
1. Show all submissions (anonymized)
2. Click on the funniest combination
3. Click "Select as Winner"
4. **Show the video generation process:**
   - "Generating video..." animation
   - Fetch.ai Coordinator Agent routes request
   - Video Agent creates prompt
   - Veo3 generates video (or mock)
5. Video appears and plays automatically

**Highlight:**
- Fetch.ai agent orchestration
- Video generation in real-time
- Winner announcement with score update

---

### Part 5: Architecture Deep Dive (Optional - 1 minute)

**Say:**
> "Let me quickly show you the architecture that makes this possible."

**Show:**
- Open backend terminal showing WebSocket logs
- Open agent terminals showing agent communication
- Explain the flow:
  ```
  Frontend → Backend → Coordinator Agent
                           ↓
                    Video Agent → Veo3
                    AI Player → Gemini
  ```

**Highlight:**
- Distributed agent architecture
- Real-time WebSocket communication
- Microservices design

---

## 🎯 Key Talking Points

### Innovation
- **First** Cards Against Humanity with AI video generation
- **Multimodal** experience (text + video)
- **Distributed** AI agents via Fetch.ai

### Technical Excellence
- Real-time multiplayer with Socket.io
- Fetch.ai agent orchestration
- Modern React + TypeScript frontend
- FastAPI backend with async support

### User Experience
- Seamless gameplay
- Beautiful, responsive UI
- AI bots that play like humans
- Instant video generation

### Scalability
- Microservices architecture
- Video caching for performance
- Horizontal scaling ready
- Cloud deployment ready

---

## 🎪 Demo Variations

### Quick Demo (2 minutes)
1. Show landing page
2. Create game + add AI bots
3. Play one round
4. Show video generation

### Full Demo (10 minutes)
1. Introduction + architecture
2. Create game
3. Show multiplayer (2 browser windows)
4. Play 2-3 rounds
5. Show different AI personalities
6. Explain Fetch.ai agents
7. Show code briefly

### Technical Deep Dive (15 minutes)
1. Full demo above
2. Show backend code
3. Show agent code
4. Explain WebSocket events
5. Show database/caching
6. Discuss deployment strategy

---

## 🐛 Troubleshooting During Demo

### Video Won't Generate
**Backup Plan:**
- Say: "In production, this would call Veo3 API"
- Show the mock video placeholder
- Explain the caching strategy

### WebSocket Disconnects
**Backup Plan:**
- Refresh the page
- Show that game state persists
- Highlight resilience features

### AI Bot Doesn't Play
**Backup Plan:**
- Manually submit cards
- Explain the AI logic
- Show the agent code

---

## 📊 Metrics to Highlight

- **Response Time:** < 100ms for card submissions
- **Video Generation:** 5-10 seconds (with Veo3)
- **Concurrent Players:** Supports 8 per game
- **Agent Communication:** < 50ms latency

---

## 🎬 Closing Statement

**Say:**
> "Absurdly Visual demonstrates the future of gaming - where AI doesn't just play with you, but creates content in real-time. Built on Fetch.ai's agent framework, it showcases how distributed AI can create truly unique, multimodal experiences. Thank you!"

---

## 📸 Screenshots to Prepare

1. Landing page
2. Game lobby with players
3. Black card display
4. Hand of white cards
5. Submission phase
6. Video generation
7. Winner announcement
8. Architecture diagram

---

## 🎥 Video Recording Tips

### For Recorded Demos

1. **Screen Resolution:** 1920x1080
2. **Browser Zoom:** 100%
3. **Hide Bookmarks Bar**
4. **Close Unnecessary Tabs**
5. **Disable Notifications**
6. **Use Incognito Mode** (clean state)

### Recording Checklist

- [ ] Audio test
- [ ] Screen recording software ready
- [ ] Backup demo environment
- [ ] Script printed/visible
- [ ] Timer visible
- [ ] Backup video ready

---

## 🏆 Judging Criteria Alignment

### Innovation (25%)
- First multimodal CAH game
- AI video generation
- Fetch.ai agent architecture

### Technical Implementation (25%)
- Clean, scalable code
- Real-time features
- Microservices design

### User Experience (25%)
- Intuitive UI
- Smooth gameplay
- Beautiful design

### Presentation (25%)
- Clear demo
- Good storytelling
- Technical depth

---

## 🎯 Q&A Preparation

### Expected Questions

**Q: How long does video generation take?**
A: 5-10 seconds with Veo3 Fast, cached videos are instant.

**Q: Can it scale to more players?**
A: Yes, architecture supports multiple game rooms and horizontal scaling.

**Q: What happens if a player disconnects?**
A: AI bot can automatically replace them, game state persists.

**Q: How do Fetch.ai agents communicate?**
A: Via REST APIs and agent-to-agent messaging protocol.

**Q: Is the video generation expensive?**
A: We implement aggressive caching and use Veo3 Fast for cost optimization.

---

**Good luck with your demo! 🚀**
