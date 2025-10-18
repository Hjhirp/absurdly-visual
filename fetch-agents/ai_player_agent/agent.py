"""
Fetch.ai AI Player Agent
Uses Gemini to select the funniest card combinations
"""

from uagents import Agent, Context, Model
from typing import Optional, List
import os
import random
from dotenv import load_dotenv

load_dotenv()

# Agent configuration
AGENT_SEED = os.getenv("AI_PLAYER_AGENT_SEED", "ai_player_secret_seed")
AGENT_PORT = int(os.getenv("AI_PLAYER_AGENT_PORT", "8003"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Create the AI player agent
ai_player = Agent(
    name="ai_player",
    seed=AGENT_SEED,
    port=AGENT_PORT,
    endpoint=[f"http://localhost:{AGENT_PORT}/submit"],
)


class AIPlayRequest(Model):
    blackCard: str
    availableCards: List[str]
    personality: str = "absurd"
    gameContext: Optional[dict] = None


class AIPlayResponse(Model):
    success: bool
    selectedCardId: Optional[str] = None
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    error: Optional[str] = None


@ai_player.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"AI Player Agent started")
    ctx.logger.info(f"Agent address: {ai_player.address}")
    ctx.logger.info(f"Gemini API configured: {bool(GEMINI_API_KEY)}")


@ai_player.on_message(model=AIPlayRequest)
async def handle_play_request(ctx: Context, sender: str, msg: AIPlayRequest):
    """Handle AI player card selection requests"""
    ctx.logger.info(f"Received play request from {sender}")
    
    try:
        if not msg.availableCards:
            await ctx.send(
                sender,
                AIPlayResponse(success=False, error="No cards available")
            )
            return
        
        # Select card using AI
        if GEMINI_API_KEY:
            result = await select_card_gemini(
                ctx, msg.blackCard, msg.availableCards, msg.personality
            )
        else:
            result = select_card_mock(msg.availableCards, msg.personality)
        
        await ctx.send(
            sender,
            AIPlayResponse(
                success=True,
                selectedCardId=result["selectedCardId"],
                confidence=result["confidence"],
                reasoning=result["reasoning"]
            )
        )
    
    except Exception as e:
        ctx.logger.error(f"Error selecting card: {e}")
        await ctx.send(
            sender,
            AIPlayResponse(success=False, error=str(e))
        )


async def select_card_gemini(ctx: Context, black_card: str, available_cards: List[str], 
                             personality: str) -> dict:
    """Use Gemini to select the funniest card"""
    # TODO: Implement actual Gemini API call
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        
        # Create prompt based on personality
        personality_prompts = {
            "savage": "You are a savage comedian who loves dark humor and shocking combinations.",
            "wholesome": "You are a wholesome comedian who loves family-friendly, clever wordplay.",
            "absurd": "You are an absurdist comedian who loves random, nonsensical combinations.",
            "strategic": "You are a strategic player who analyzes past wins and selects accordingly."
        }
        
        personality_prompt = personality_prompts.get(personality, personality_prompts["absurd"])
        
        prompt = f"""
{personality_prompt}

Black Card: "{black_card}"

Available White Cards:
{chr(10).join(f"{i+1}. {card}" for i, card in enumerate(available_cards))}

Select the number of the funniest white card that best completes the black card.
Respond with ONLY the number (1-{len(available_cards)}) and a brief reason.

Format: NUMBER: reason
"""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Parse response
        parts = response_text.split(":", 1)
        if len(parts) == 2:
            try:
                card_index = int(parts[0].strip()) - 1
                reasoning = parts[1].strip()
                
                if 0 <= card_index < len(available_cards):
                    return {
                        "selectedCardId": available_cards[card_index],
                        "confidence": 0.85,
                        "reasoning": reasoning
                    }
            except ValueError:
                pass
        
        # Fallback to random if parsing fails
        ctx.logger.warning(f"Failed to parse Gemini response: {response_text}")
        return select_card_mock(available_cards, personality)
    
    except Exception as e:
        ctx.logger.error(f"Gemini API error: {e}")
        return select_card_mock(available_cards, personality)


def select_card_mock(available_cards: List[str], personality: str) -> dict:
    """Mock card selection for testing"""
    selected = random.choice(available_cards)
    
    reasoning_templates = {
        "savage": "This combination is delightfully offensive",
        "wholesome": "This is clever and family-friendly",
        "absurd": "This makes absolutely no sense, perfect!",
        "strategic": "Based on past wins, this should work"
    }
    
    reasoning = reasoning_templates.get(personality, "This seems funny")
    
    return {
        "selectedCardId": selected,
        "confidence": random.uniform(0.6, 0.95),
        "reasoning": reasoning,
        "mock": True
    }


# REST API endpoint
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="AI Player Agent API")


class AIPlayAPIRequest(BaseModel):
    blackCard: str
    availableCards: List[str]
    personality: str = "absurd"
    gameContext: Optional[dict] = None


@app.post("/play")
async def play_endpoint(request: AIPlayAPIRequest):
    """REST API endpoint for AI card selection"""
    try:
        if not request.availableCards:
            raise HTTPException(status_code=400, detail="No cards available")
        
        if GEMINI_API_KEY:
            result = await select_card_gemini(
                None, request.blackCard, request.availableCards, request.personality
            )
        else:
            result = select_card_mock(request.availableCards, request.personality)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy", "agent": "ai_player"}


if __name__ == "__main__":
    import uvicorn
    import asyncio
    
    async def run_agent():
        await ai_player.run()
    
    config = uvicorn.Config(app, host="0.0.0.0", port=AGENT_PORT, log_level="info")
    server = uvicorn.Server(config)
    
    loop = asyncio.get_event_loop()
    loop.create_task(run_agent())
    loop.run_until_complete(server.serve())
