from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from ..services.game_service import game_service
from ..services.card_service import card_service
from ..services.video_cache import video_cache
from ..services.content_pipeline_service import content_pipeline_service
from ..services.nanobanana_service import nanobanana_service
from ..services.gemini_tts_service import gemini_tts_service
from ..models.card import BlackCard, WhiteCard

router = APIRouter(prefix="/api", tags=["api"])


class CreateGameRequest(BaseModel):
    player_name: str
    settings: Optional[dict] = None


class GameResponse(BaseModel):
    game_id: str
    player_id: str
    message: str


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "absurdly-visual-api"}


@router.get("/cards/black", response_model=List[BlackCard])
async def get_black_cards():
    """Get all black cards"""
    return card_service.get_all_black_cards()


@router.get("/cards/white", response_model=List[WhiteCard])
async def get_white_cards():
    """Get all white cards"""
    return card_service.get_all_white_cards()


@router.get("/cards/black/{card_id}")
async def get_black_card(card_id: str):
    """Get a specific black card"""
    card = card_service.get_black_card(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card


@router.get("/cards/white/{card_id}")
async def get_white_card(card_id: str):
    """Get a specific white card"""
    card = card_service.get_white_card(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card


@router.get("/game/{game_id}")
async def get_game(game_id: str):
    """Get game information"""
    game = game_service.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return {
        "id": game.id,
        "state": game.state,
        "players": game.players,
        "max_players": game.max_players,
        "points_to_win": game.points_to_win,
        "current_round": game.current_round.round_number if game.current_round else None
    }


@router.get("/game/{game_id}/state/{player_id}")
async def get_game_state(game_id: str, player_id: str):
    """Get game state for a specific player"""
    state = game_service.get_game_state_for_player(game_id, player_id)
    if not state:
        raise HTTPException(status_code=404, detail="Game or player not found")
    return state


@router.get("/videos/cache/stats")
async def get_cache_stats():
    """Get video cache statistics"""
    return video_cache.get_stats()


@router.get("/games")
async def list_games():
    """List all active games"""
    games = []
    for game in game_service.games.values():
        games.append({
            "id": game.id,
            "state": game.state,
            "player_count": len(game.players),
            "max_players": game.max_players,
            "created_at": game.created_at.isoformat()
        })
    return games


@router.get("/stats")
async def get_stats():
    """Get overall statistics"""
    return {
        "total_games": len(game_service.games),
        "total_players": len(game_service.players),
        "active_games": len([g for g in game_service.games.values() if g.state == "playing"]),
        "video_cache": video_cache.get_stats()
    }


# Content Pipeline Endpoints

class CardCombination(BaseModel):
    black_card: str
    white_cards: List[str]


class GenerateContentRequest(BaseModel):
    black_card: str
    white_cards: List[str]
    narration_style: Optional[str] = "humorous"


class GenerateRoundContentRequest(BaseModel):
    black_card: str
    submissions: List[dict]  # [{player_id, cards: [str]}]
    narration_style: Optional[str] = "humorous"


class BatchContentRequest(BaseModel):
    combinations: List[CardCombination]
    narration_style: Optional[str] = "humorous"


@router.post("/content/generate")
async def generate_social_content(request: GenerateContentRequest):
    """
    Generate complete social media content (image, video, narration)
    for a single card combination
    """
    try:
        result = await content_pipeline_service.generate_social_media_content(
            request.black_card,
            request.white_cards,
            request.narration_style
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")


@router.post("/content/round")
async def generate_round_content(request: GenerateRoundContentRequest):
    """
    Generate content for a full game round:
    1. Generate images for all submissions in parallel
    2. Select winner
    3. Generate video for winner
    4. Generate narration
    """
    try:
        result = await content_pipeline_service.generate_content_for_round(
            request.black_card,
            request.submissions,
            request.narration_style
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Round content generation failed: {str(e)}")


@router.post("/content/batch")
async def generate_batch_content(request: BatchContentRequest):
    """
    Generate content for multiple card combinations in parallel
    Useful for batch content creation
    """
    try:
        combinations = [
            {"black_card": combo.black_card, "white_cards": combo.white_cards}
            for combo in request.combinations
        ]
        results = await content_pipeline_service.generate_batch_content(
            combinations,
            request.narration_style
        )
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch content generation failed: {str(e)}")


@router.post("/images/generate")
async def generate_image(request: GenerateContentRequest):
    """Generate a single image using Nanobanana"""
    try:
        from ..services.ai_service import ai_service
        
        # Generate prompt
        prompt = await ai_service.generate_video_prompt(
            request.black_card,
            request.white_cards
        )
        
        # Generate image
        image_url = await nanobanana_service.generate_image(prompt, aspect_ratio="9:16")
        
        if not image_url:
            raise HTTPException(status_code=500, detail="Image generation failed")
        
        return {
            "image_url": image_url,
            "prompt": prompt,
            "black_card": request.black_card,
            "white_cards": request.white_cards
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")


@router.post("/narration/generate")
async def generate_narration(request: GenerateContentRequest):
    """Generate TTS narration for a card combination"""
    try:
        narration = await gemini_tts_service.generate_narrated_script(
            request.black_card,
            request.white_cards,
            style=request.narration_style
        )
        
        return narration
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Narration generation failed: {str(e)}")
