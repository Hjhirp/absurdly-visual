"""
Example API routes for Card Generator Service

Add these to your routes/api.py or similar file to expose card generation via API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from app.services.card_generator_service import card_generator_service
from app.services.card_service import card_service


# Create router
generator_router = APIRouter(prefix="/api/generator", tags=["card-generator"])


# Request/Response models
class GenerateBlackCardsRequest(BaseModel):
    count: int = Field(default=5, ge=1, le=20, description="Number of cards to generate")
    pack: str = Field(default="ai-generated", description="Pack name")
    temperature: float = Field(default=1.0, ge=0.0, le=2.0, description="AI creativity level")


class GenerateWhiteCardsRequest(BaseModel):
    count: int = Field(default=10, ge=1, le=50, description="Number of cards to generate")
    pack: str = Field(default="ai-generated", description="Pack name")
    nsfw: bool = Field(default=False, description="Generate NSFW content")
    temperature: float = Field(default=1.0, ge=0.0, le=2.0, description="AI creativity level")


class GeneratePackRequest(BaseModel):
    black_count: int = Field(default=10, ge=1, le=50, description="Number of black cards")
    white_count: int = Field(default=30, ge=1, le=100, description="Number of white cards")
    pack_name: str = Field(default="ai-generated", description="Pack name")
    nsfw_ratio: float = Field(default=0.3, ge=0.0, le=1.0, description="Ratio of NSFW white cards")
    temperature: float = Field(default=1.0, ge=0.0, le=2.0, description="AI creativity level")


class CardResponse(BaseModel):
    id: str
    text: str
    type: str
    pack: str


class BlackCardResponse(CardResponse):
    pick: int


class WhiteCardResponse(CardResponse):
    nsfw: bool


class GeneratedPackResponse(BaseModel):
    pack_name: str
    black_cards: List[BlackCardResponse]
    white_cards: List[WhiteCardResponse]


# Routes
@generator_router.post("/black-cards", response_model=List[BlackCardResponse])
async def generate_black_cards_endpoint(request: GenerateBlackCardsRequest):
    """
    Generate new black cards using AI
    
    Returns a list of generated black cards
    """
    try:
        # Get existing cards for context
        existing_cards = card_service.get_all_black_cards()
        
        # Generate cards
        cards = await card_generator_service.generate_black_cards(
            count=request.count,
            pack=request.pack,
            temperature=request.temperature,
            existing_cards=existing_cards
        )
        
        # Convert to response format
        return [
            BlackCardResponse(
                id=card.id,
                text=card.text,
                type=card.type,
                pack=card.pack,
                pick=card.pick
            )
            for card in cards
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate black cards: {str(e)}")


@generator_router.post("/white-cards", response_model=List[WhiteCardResponse])
async def generate_white_cards_endpoint(request: GenerateWhiteCardsRequest):
    """
    Generate new white cards using AI
    
    Returns a list of generated white cards
    """
    try:
        # Get existing cards for context
        existing_cards = card_service.get_all_white_cards()
        
        # Generate cards
        cards = await card_generator_service.generate_white_cards(
            count=request.count,
            pack=request.pack,
            nsfw=request.nsfw,
            temperature=request.temperature,
            existing_cards=existing_cards
        )
        
        # Convert to response format
        return [
            WhiteCardResponse(
                id=card.id,
                text=card.text,
                type=card.type,
                pack=card.pack,
                nsfw=card.nsfw
            )
            for card in cards
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate white cards: {str(e)}")


@generator_router.post("/pack", response_model=GeneratedPackResponse)
async def generate_pack_endpoint(request: GeneratePackRequest):
    """
    Generate a complete card pack using AI
    
    Returns a full pack with black and white cards
    """
    try:
        # Get existing cards for context
        existing_black = card_service.get_all_black_cards()
        existing_white = card_service.get_all_white_cards()
        
        # Generate pack
        pack = await card_generator_service.generate_card_pack(
            black_count=request.black_count,
            white_count=request.white_count,
            pack_name=request.pack_name,
            nsfw_ratio=request.nsfw_ratio,
            temperature=request.temperature,
            existing_black=existing_black,
            existing_white=existing_white
        )
        
        # Convert to response format
        return GeneratedPackResponse(
            pack_name=request.pack_name,
            black_cards=[
                BlackCardResponse(
                    id=card.id,
                    text=card.text,
                    type=card.type,
                    pack=card.pack,
                    pick=card.pick
                )
                for card in pack['black_cards']
            ],
            white_cards=[
                WhiteCardResponse(
                    id=card.id,
                    text=card.text,
                    type=card.type,
                    pack=card.pack,
                    nsfw=card.nsfw
                )
                for card in pack['white_cards']
            ]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate pack: {str(e)}")


@generator_router.get("/health")
async def health_check():
    """Check if card generator service is available"""
    if not card_generator_service.model:
        return {
            "status": "unavailable",
            "message": "Gemini API not configured"
        }
    
    return {
        "status": "available",
        "message": "Card generator service is ready"
    }


# To use in your main app:
# from app.api.generator_routes import generator_router
# app.include_router(generator_router)
