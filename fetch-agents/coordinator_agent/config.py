"""Configuration for Coordinator Agent"""

import os
from dotenv import load_dotenv

load_dotenv()

# Agent Configuration
AGENT_SEED = os.getenv("COORDINATOR_AGENT_SEED", "coordinator_secret_seed")
AGENT_PORT = int(os.getenv("COORDINATOR_AGENT_PORT", "8001"))

# Video Agent
VIDEO_AGENT_ADDRESS = os.getenv("VIDEO_AGENT_ADDRESS", "")

# AI Player Agent
AI_PLAYER_AGENT_ADDRESS = os.getenv("AI_PLAYER_AGENT_ADDRESS", "")
