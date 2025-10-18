"""
Fetch.ai Video Generation Agent
Generates videos using Veo3 API
"""

from uagents import Agent, Context, Model
from typing import Optional, List
import os
import hashlib
from dotenv import load_dotenv

load_dotenv()

# Agent configuration
AGENT_SEED = os.getenv("VIDEO_AGENT_SEED", "video_agent_secret_seed")
AGENT_PORT = int(os.getenv("VIDEO_AGENT_PORT", "8002"))
VEO3_API_KEY = os.getenv("VEO3_API_KEY", "")

# Create the video agent
video_agent = Agent(
    name="video_generator",
    seed=AGENT_SEED,
    port=AGENT_PORT,
    endpoint=[f"http://localhost:{AGENT_PORT}/submit"],
)


class VideoGenerationRequest(Model):
    blackCard: str
    whiteCards: List[str]
    style: str = "comedic"


class VideoGenerationResponse(Model):
    success: bool
    videoUrl: Optional[str] = None
    generationId: Optional[str] = None
    status: str = "pending"
    error: Optional[str] = None


@video_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Video Generation Agent started")
    ctx.logger.info(f"Agent address: {video_agent.address}")
    ctx.logger.info(f"Veo3 API configured: {bool(VEO3_API_KEY)}")


@video_agent.on_message(model=VideoGenerationRequest)
async def handle_video_request(ctx: Context, sender: str, msg: VideoGenerationRequest):
    """Handle video generation requests"""
    ctx.logger.info(f"Received video generation request from {sender}")
    
    try:
        # Generate creative prompt for Veo3
        prompt = create_video_prompt(msg.blackCard, msg.whiteCards, msg.style)
        ctx.logger.info(f"Generated prompt: {prompt}")
        
        # Generate video
        if VEO3_API_KEY:
            # TODO: Call actual Veo3 API
            result = await generate_video_veo3(ctx, prompt)
        else:
            # Mock generation
            result = generate_video_mock(msg.blackCard, msg.whiteCards)
        
        await ctx.send(
            sender,
            VideoGenerationResponse(
                success=True,
                videoUrl=result["videoUrl"],
                generationId=result["generationId"],
                status=result["status"]
            )
        )
    
    except Exception as e:
        ctx.logger.error(f"Error generating video: {e}")
        await ctx.send(
            sender,
            VideoGenerationResponse(success=False, error=str(e))
        )


def create_video_prompt(black_card: str, white_cards: List[str], style: str) -> str:
    """Create a creative prompt for Veo3 video generation"""
    
    # Combine cards into a scenario
    scenario = black_card
    for white_card in white_cards:
        scenario = scenario.replace("_", white_card, 1)
    
    # Style-specific prompt engineering
    style_prompts = {
        "comedic": "Create a humorous, slapstick comedy scene showing: ",
        "cinematic": "Create an epic, cinematic scene with dramatic lighting showing: ",
        "absurd": "Create a surreal, absurdist scene with unexpected elements showing: "
    }
    
    prefix = style_prompts.get(style, style_prompts["comedic"])
    
    prompt = f"{prefix}{scenario}. Make it visually engaging, short (5-10 seconds), and family-friendly."
    
    return prompt


async def generate_video_veo3(ctx: Context, prompt: str) -> dict:
    """Generate video using Veo3 API"""
    # TODO: Implement actual Veo3 API call
    # This is a placeholder for the actual implementation
    
    ctx.logger.info("Calling Veo3 API...")
    
    # Placeholder response
    import hashlib
    video_id = hashlib.md5(prompt.encode()).hexdigest()[:8]
    
    return {
        "videoUrl": f"https://veo3-generated.com/{video_id}.mp4",
        "generationId": video_id,
        "status": "completed"
    }


def generate_video_mock(black_card: str, white_cards: List[str]) -> dict:
    """Generate mock video URL for testing"""
    combination = f"{black_card}{''.join(white_cards)}"
    video_id = hashlib.md5(combination.encode()).hexdigest()[:8]
    
    return {
        "videoUrl": f"https://placeholder-video.com/{video_id}.mp4",
        "generationId": video_id,
        "status": "completed",
        "mock": True
    }


# REST API endpoint
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Video Generation Agent API")


class VideoAPIRequest(BaseModel):
    blackCard: str
    whiteCards: List[str]
    style: str = "comedic"


@app.post("/generate")
async def generate_video_endpoint(request: VideoAPIRequest):
    """REST API endpoint for video generation"""
    try:
        prompt = create_video_prompt(request.blackCard, request.whiteCards, request.style)
        
        if VEO3_API_KEY:
            result = await generate_video_veo3(None, prompt)
        else:
            result = generate_video_mock(request.blackCard, request.whiteCards)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/{generation_id}")
async def get_video_status(generation_id: str):
    """Check video generation status"""
    # TODO: Implement actual status checking
    return {
        "status": "completed",
        "progress": 100,
        "videoUrl": f"https://placeholder-video.com/{generation_id}.mp4"
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "agent": "video_generator"}


if __name__ == "__main__":
    import uvicorn
    import asyncio
    
    async def run_agent():
        await video_agent.run()
    
    config = uvicorn.Config(app, host="0.0.0.0", port=AGENT_PORT, log_level="info")
    server = uvicorn.Server(config)
    
    loop = asyncio.get_event_loop()
    loop.create_task(run_agent())
    loop.run_until_complete(server.serve())
