"""
Fetch.ai Coordinator Agent
Orchestrates video generation and AI player actions
"""

from uagents import Agent, Context, Model
from typing import Optional, List
import os
from dotenv import load_dotenv

load_dotenv()

# Agent configuration
AGENT_SEED = os.getenv("COORDINATOR_AGENT_SEED", "coordinator_secret_seed")
AGENT_PORT = int(os.getenv("COORDINATOR_AGENT_PORT", "8001"))

# Create the coordinator agent
coordinator = Agent(
    name="coordinator",
    seed=AGENT_SEED,
    port=AGENT_PORT,
    endpoint=[f"http://localhost:{AGENT_PORT}/submit"],
)


class CoordinateRequest(Model):
    action: str  # "generate_video" or "ai_play"
    data: dict


class CoordinateResponse(Model):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


@coordinator.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Coordinator Agent started")
    ctx.logger.info(f"Agent address: {coordinator.address}")


@coordinator.on_message(model=CoordinateRequest)
async def handle_coordinate_request(ctx: Context, sender: str, msg: CoordinateRequest):
    """Handle coordination requests from the backend"""
    ctx.logger.info(f"Received {msg.action} request from {sender}")
    
    try:
        if msg.action == "generate_video":
            # Forward to video generation agent
            result = await generate_video_handler(ctx, msg.data)
            await ctx.send(
                sender,
                CoordinateResponse(success=True, result=result)
            )
        
        elif msg.action == "ai_play":
            # Forward to AI player agent
            result = await ai_player_handler(ctx, msg.data)
            await ctx.send(
                sender,
                CoordinateResponse(success=True, result=result)
            )
        
        else:
            await ctx.send(
                sender,
                CoordinateResponse(
                    success=False,
                    error=f"Unknown action: {msg.action}"
                )
            )
    
    except Exception as e:
        ctx.logger.error(f"Error handling request: {e}")
        await ctx.send(
            sender,
            CoordinateResponse(success=False, error=str(e))
        )


async def generate_video_handler(ctx: Context, data: dict) -> dict:
    """Handle video generation request"""
    black_card = data.get("blackCard", "")
    white_cards = data.get("whiteCards", [])
    style = data.get("style", "comedic")
    
    ctx.logger.info(f"Generating video for: {black_card} + {white_cards}")
    
    # TODO: Call actual video generation agent
    # For now, return mock response
    import hashlib
    combination = f"{black_card}{''.join(white_cards)}"
    video_id = hashlib.md5(combination.encode()).hexdigest()[:8]
    
    return {
        "videoUrl": f"https://placeholder-video.com/{video_id}.mp4",
        "generationId": video_id,
        "status": "completed",
        "mock": True
    }


async def ai_player_handler(ctx: Context, data: dict) -> dict:
    """Handle AI player card selection request"""
    black_card = data.get("blackCard", "")
    available_cards = data.get("availableCards", [])
    personality = data.get("personality", "absurd")
    
    ctx.logger.info(f"AI selecting card for: {black_card}")
    
    # TODO: Call actual AI player agent
    # For now, return mock response
    import random
    
    if not available_cards:
        return {"error": "No cards available"}
    
    selected = random.choice(available_cards)
    
    return {
        "selectedCardId": selected,
        "confidence": random.uniform(0.6, 0.95),
        "reasoning": f"Selected based on {personality} personality",
        "mock": True
    }


# REST API endpoint for external access
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Coordinator Agent API")


class CoordinateAPIRequest(BaseModel):
    action: str
    data: dict


@app.post("/coordinate")
async def coordinate_endpoint(request: CoordinateAPIRequest):
    """REST API endpoint for coordination requests"""
    try:
        if request.action == "generate_video":
            result = await generate_video_handler(None, request.data)
            return result
        elif request.action == "ai_play":
            result = await ai_player_handler(None, request.data)
            return result
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy", "agent": "coordinator"}


if __name__ == "__main__":
    import uvicorn
    
    # Run both the agent and the REST API
    import asyncio
    
    async def run_agent():
        await coordinator.run()
    
    # Start REST API in background
    config = uvicorn.Config(app, host="0.0.0.0", port=AGENT_PORT, log_level="info")
    server = uvicorn.Server(config)
    
    # Run both
    loop = asyncio.get_event_loop()
    loop.create_task(run_agent())
    loop.run_until_complete(server.serve())
